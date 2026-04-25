# tasks/graders.py
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataclasses import dataclass, field
from typing import List, Dict
from server.environment import CodeReviewEnvironment
from models import ReviewerAction, CodeReviewObservation, BugType


@dataclass
class TaskResult:
    task_id:         str
    score:           float
    raw_reward:      float
    max_possible:    float
    steps_used:      int
    max_steps:       int
    passed:          bool
    per_snippet:     List[Dict] = field(default_factory=list)
    history:         List[Dict] = field(default_factory=list)
    arms_race_stats: Dict       = field(default_factory=dict)
    notes:           str = ""


class BaseAgent:
    def act(self, obs: CodeReviewObservation) -> ReviewerAction:
        raise NotImplementedError


def _run_episode(agent: BaseAgent, task_id: str, seed: int = 42) -> TaskResult:
    env  = CodeReviewEnvironment(task_id=task_id, seed=seed)
    obs  = env.reset()

    total_reward = 0.0
    steps        = 0
    done         = False
    per_snippet  = []

    while not done:
        action = agent.act(obs)
        obs, reward, done, info = env.step(action)
        total_reward += reward
        steps        += 1

        if action.action_type != "retrieve":
            per_snippet.append({
                "snippet_id":  action.snippet_id,
                "action":      action.action_type,
                "bug_type":    action.bug_type.value if action.bug_type else None,
                "reward":      round(reward, 4),
                "explanation": info["reward_breakdown"]["explanation"],
            })

    snippet_counts  = {
        "task1_easy":    4,
        "task2_medium":  8,
        "task3_hard":    15,
        "task4_longhor": 3,
    }
    pass_thresholds = {
        "task1_easy":    0.50,
        "task2_medium":  0.55,
        "task3_hard":    0.60,
        "task4_longhor": 0.55,
    }
    max_possible = float(snippet_counts.get(task_id, 4))
    score        = round(max(0.0, min(1.0, total_reward / max_possible)), 4)
    passed       = score >= pass_thresholds.get(task_id, 0.50)

    return TaskResult(
        task_id=task_id,
        score=score,
        raw_reward=round(total_reward, 4),
        max_possible=max_possible,
        steps_used=steps,
        max_steps=env._max_steps,
        passed=passed,
        per_snippet=per_snippet,
        history=info.get("history", []),
        arms_race_stats=info.get("arms_race_stats", {}),
        notes=f"raw={total_reward:.3f}/max={max_possible}->score={score}",
    )


def grade_task1(agent: BaseAgent, seed: int = 42) -> TaskResult:
    return _run_episode(agent, "task1_easy", seed=seed)


def grade_task2(agent: BaseAgent, seed: int = 42) -> TaskResult:
    return _run_episode(agent, "task2_medium", seed=seed)


def grade_task3(agent: BaseAgent, seed: int = 42) -> TaskResult:
    return _run_episode(agent, "task3_hard", seed=seed)


def grade_task4(agent: BaseAgent, seed: int = 42) -> TaskResult:
    return _run_episode(agent, "task4_longhor", seed=seed)


TASKS = {
    "task1_easy": {
        "grader":      grade_task1,
        "description": "4 snippets with obvious bugs",
        "difficulty":  "easy",
        "threshold":   0.50,
    },
    "task2_medium": {
        "grader":      grade_task2,
        "description": "8 snippets with logic bugs",
        "difficulty":  "medium",
        "threshold":   0.55,
    },
    "task3_hard": {
        "grader":      grade_task3,
        "description": "15 snippets with security bugs and hallucination traps",
        "difficulty":  "hard",
        "threshold":   0.60,
    },
    "task4_longhor": {
        "grader":      grade_task4,
        "description": "3 multi-function files each with 4 connected bugs requiring sequential analysis",
        "difficulty":  "long-horizon",
        "threshold":   0.55,
    },
}