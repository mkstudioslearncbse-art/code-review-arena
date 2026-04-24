# baseline.py
from __future__ import annotations
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import ReviewerAction, CodeReviewObservation, BugType
from tasks.graders import BaseAgent, TASKS, TaskResult


class HeuristicAgent(BaseAgent):
    """
    Rule-based agent using keyword matching.
    Always retrieves first, then identifies bug by keywords.
    """
    def __init__(self):
        self._retrieved     = False
        self._last_snippet  = None

    def act(self, obs: CodeReviewObservation) -> ReviewerAction:
        snippet = obs.current_snippet
        if snippet is None:
            return ReviewerAction(
                action_type="mark_clean",
                snippet_id="__none__",
            )

        if snippet.id != self._last_snippet:
            self._retrieved    = False
            self._last_snippet = snippet.id

        # Always retrieve first
        if not self._retrieved and not obs.retrieved_this_step:
            self._retrieved = True
            return ReviewerAction(
                action_type="retrieve",
                snippet_id=snippet.id,
            )

        text = (snippet.title + " " + snippet.buggy_code).lower()

        # Keyword-based bug type detection
        KEYWORDS = {
            BugType.SQL_INJECTION:   ["sql", "execute", "query", "select", "f'select"],
            BugType.PATH_TRAVERSAL:  ["path", "join", "open", "filename", "upload"],
            BugType.RACE_CONDITION:  ["thread", "lock", "counter", "global", "concurrent"],
            BugType.INSECURE_RANDOM: ["random", "randint", "choice", "token"],
            BugType.NULL_POINTER:    ["none", "null", "is none", "getattr"],
            BugType.MUTABLE_DEFAULT: ["def ", "=[", "={}"],
            BugType.OFF_BY_ONE:      ["range", "len", "index", "+ 1", "- 1"],
            BugType.WRONG_OPERATOR:  ["< ", "> ", "//", "=="],
            BugType.WRONG_COMPARISON:["== none", "!= none"],
            BugType.INTEGER_OVERFLOW:["//", "int(", "floor"],
        }

        detected_bug = BugType.WRONG_OPERATOR
        top_score    = 0
        for bug_type, keywords in KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > top_score:
                top_score    = score
                detected_bug = bug_type

        top_scheme = (
            obs.rag_context[0].bug_id
            if obs.rag_context else None
        )

        return ReviewerAction(
            action_type="identify_bug",
            snippet_id=snippet.id,
            bug_type=detected_bug,
            bug_line=snippet.bug_line,
        )


if __name__ == "__main__":
    agent      = HeuristicAgent()
    all_scores = []
    results    = {}

    print("=" * 60)
    print("CodeReviewArena — HeuristicAgent Baseline")
    print("=" * 60)

    for task_id, meta in TASKS.items():
        print(f"\n{'─'*60}")
        print(f"Task: {task_id} ({meta['difficulty']})")
        result: TaskResult = meta["grader"](agent)
        all_scores.append(result.score)
        results[task_id] = {
            "score":      result.score,
            "passed":     result.passed,
            "steps_used": result.steps_used,
            "arms_race":  result.arms_race_stats,
        }
        print(f"  Score : {result.score:.4f} "
              f"({'PASS ✓' if result.passed else 'FAIL ✗'})")
        print(f"  Steps : {result.steps_used}/{result.max_steps}")
        for rec in result.per_snippet:
            print(
                f"    [{rec['snippet_id']}] "
                f"{rec['action']:15s} "
                f"reward={rec['reward']:+.4f}  "
                f"{rec['explanation'][:50]}..."
            )

    print(f"\n{'='*60}")
    print(f"Overall mean: {sum(all_scores)/len(all_scores):.4f}")

    with open("baseline_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Saved to baseline_results.json")