# server/environment.py
from __future__ import annotations
import copy
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (
    ReviewerAction, CodeReviewObservation,
    AgentRole, CodeSnippet, BugPattern, RewardBreakdown
)
from corpus.snippets import get_snippets_for_task, get_ground_truth
from rag.retriever import retriever
from server.reward import compute_reviewer_reward


class CodeReviewEnvironment:
    TASK_CONFIG = {
        "task1_easy":   {"max_steps": 20,  "snippet_count": 4},
        "task2_medium": {"max_steps": 30,  "snippet_count": 8},
        "task3_hard":   {"max_steps": 50,  "snippet_count": 15},
    }

    def __init__(self, task_id: str = "task1_easy", seed: int = 42):
        if task_id not in self.TASK_CONFIG:
            raise ValueError(
                f"Unknown task_id='{task_id}'. "
                f"Choose from: {list(self.TASK_CONFIG.keys())}"
            )
        self._task_id            = task_id
        self._seed               = seed
        self._max_steps          = self.TASK_CONFIG[task_id]["max_steps"]
        self._queue:             List[CodeSnippet] = []
        self._current_idx:       int   = 0
        self._step_number:       int   = 0
        self._cumulative_reward: float = 0.0
        self._done:              bool  = True
        self._rag_context:       List[BugPattern] = []
        self._retrieved_this_snippet: bool = False
        self._history:           List[Dict] = []
        self._difficulty:        int   = 1
        self._arms_race_stats:   Dict  = {
            "bugs_caught":    0,
            "bugs_missed":    0,
            "correct_fixes":  0,
            "hallucinations": 0,
        }

    def reset(self) -> CodeReviewObservation:
        self._queue                  = copy.deepcopy(
            get_snippets_for_task(self._task_id)
        )
        self._current_idx            = 0
        self._step_number            = 0
        self._cumulative_reward      = 0.0
        self._done                   = False
        self._rag_context            = []
        self._retrieved_this_snippet = False
        self._history                = []
        return self._build_observation()

    def step(
        self, action: ReviewerAction
    ) -> Tuple[CodeReviewObservation, float, bool, Dict[str, Any]]:
        if self._done:
            raise RuntimeError("Episode done. Call reset() first.")

        self._step_number += 1
        current = self._current_snippet()

        # RETRIEVE action
        if action.action_type == "retrieve":
            if current:
                query = f"{current.title} {current.buggy_code}"
                docs  = retriever.retrieve(query, top_k=3)
                self._rag_context            = docs
                self._retrieved_this_snippet = True
            reward_obj = RewardBreakdown(
                total=0.05,
                retrieval_discipline=1.0,
                explanation="RETRIEVE: bug patterns loaded (+0.05)",
            )
            self._cumulative_reward += 0.05
            obs = self._build_observation(
                last_action="retrieve",
                last_reward=0.05,
                info_message=f"Retrieved {len(self._rag_context)} bug patterns.",
            )
            return obs, 0.05, False, self._build_info(reward_obj)

        # All other actions
        reward_obj = compute_reviewer_reward(
            action=action,
            rag_context=self._rag_context,
            retrieved_this_step=self._retrieved_this_snippet,
            step_number=self._step_number,
            max_steps=self._max_steps,
        )
        reward = reward_obj.total
        self._cumulative_reward += reward

        # Update arms race stats
        if action.action_type in ("identify_bug", "propose_fix", "escalate"):
            if reward_obj.detection_accuracy >= 1.0:
                self._arms_race_stats["bugs_caught"] += 1
            else:
                self._arms_race_stats["bugs_missed"] += 1
            if reward_obj.fix_correctness >= 1.0:
                self._arms_race_stats["correct_fixes"] += 1
            if reward_obj.hallucination_penalty < 0:
                self._arms_race_stats["hallucinations"] += 1

        # Mark snippet as reviewed
        if current:
            current.is_reviewed = True

        # Record history
        self._history.append({
            "step":        self._step_number,
            "snippet_id":  action.snippet_id,
            "action":      action.action_type,
            "bug_type":    action.bug_type.value if action.bug_type else None,
            "reward":      reward,
            "explanation": reward_obj.explanation,
        })

        # Advance to next snippet
        self._advance()
        self._rag_context            = []
        self._retrieved_this_snippet = False

        # Check done
        unreviewed = [s for s in self._queue if not s.is_reviewed]
        if not unreviewed or self._step_number >= self._max_steps:
            self._done = True

        obs = self._build_observation(
            last_action=action.action_type,
            last_reward=reward,
            info_message=reward_obj.explanation,
        )
        return obs, reward, self._done, self._build_info(reward_obj)

    @property
    def state(self) -> Dict[str, Any]:
        return {
            "task_id":            self._task_id,
            "step_number":        self._step_number,
            "max_steps":          self._max_steps,
            "done":               self._done,
            "cumulative_reward":  self._cumulative_reward,
            "snippets_remaining": sum(1 for s in self._queue if not s.is_reviewed),
            "arms_race_stats":    self._arms_race_stats,
            "difficulty_level":   self._difficulty,
            "history":            self._history,
        }

    def _current_snippet(self) -> Optional[CodeSnippet]:
        unreviewed = [s for s in self._queue if not s.is_reviewed]
        return unreviewed[0] if unreviewed else None

    def _advance(self):
        unreviewed = [s for s in self._queue if not s.is_reviewed]
        if unreviewed:
            self._current_idx = self._queue.index(unreviewed[0])
        else:
            self._current_idx = len(self._queue)

    def _build_observation(
        self,
        last_action:  Optional[str] = None,
        last_reward:  float = 0.0,
        info_message: str = "",
    ) -> CodeReviewObservation:
        current    = self._current_snippet()
        unreviewed = sum(1 for s in self._queue if not s.is_reviewed)
        reviewed   = sum(1 for s in self._queue if s.is_reviewed)
        return CodeReviewObservation(
            queue=self._queue,
            current_snippet=current,
            current_snippet_idx=self._current_idx,
            rag_context=self._rag_context,
            step_number=self._step_number,
            snippets_processed=reviewed,
            snippets_remaining=unreviewed,
            last_action=last_action,
            last_reward=last_reward,
            cumulative_reward=self._cumulative_reward,
            retrieved_this_step=self._retrieved_this_snippet,
            current_agent_role=AgentRole.CODE_REVIEWER,
            difficulty_level=self._difficulty,
            arms_race_stats=self._arms_race_stats,
            info_message=info_message,
        )

    def _build_info(self, reward_obj: RewardBreakdown) -> Dict[str, Any]:
        return {
            "reward_breakdown":  reward_obj.model_dump(),
            "task_id":           self._task_id,
            "step_number":       self._step_number,
            "cumulative_reward": self._cumulative_reward,
            "arms_race_stats":   self._arms_race_stats,
            "history":           self._history,
        }

    def render(self) -> str:
        lines = [
            f"=== CodeReviewArena | task={self._task_id} "
            f"| step={self._step_number}/{self._max_steps} ===",
            f"Cumulative reward: {self._cumulative_reward:.4f}",
            f"Arms race: {self._arms_race_stats}",
            f"Queue ({len(self._queue)} snippets):",
        ]
        for i, s in enumerate(self._queue):
            marker = "→" if i == self._current_idx else " "
            done   = "✓" if s.is_reviewed else "•"
            lines.append(
                f"  {marker} [{done}] [{s.severity}] "
                f"{s.id}: {s.title}"
            )
        return "\n".join(lines)