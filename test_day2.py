# test_day2.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.environment import CodeReviewEnvironment
from models import ReviewerAction, BugType

print("=== Day 2 Smoke Test ===\n")

env = CodeReviewEnvironment(task_id="task1_easy")
obs = env.reset()

print(f"Reset OK — {obs.snippets_remaining} snippets in queue")
print(f"First snippet: {obs.current_snippet.title}\n")

# Step 1: RETRIEVE
print("Step 1 — RETRIEVE")
action = ReviewerAction(
    action_type="retrieve",
    snippet_id=obs.current_snippet.id,
)
obs, reward, done, info = env.step(action)
print(f"  reward={reward}, rag_context={len(obs.rag_context)} patterns")
for p in obs.rag_context:
    print(f"    → {p.bug_id} (score={p.score:.3f})")

# Step 2: IDENTIFY BUG
print("\nStep 2 — IDENTIFY BUG")
action2 = ReviewerAction(
    action_type="identify_bug",
    snippet_id=obs.current_snippet.id,
    bug_type=BugType.OFF_BY_ONE,
    bug_line=4,
)
obs2, reward2, done2, info2 = env.step(action2)
print(f"  reward={reward2:.4f}")
print(f"  explanation: {info2['reward_breakdown']['explanation']}")

# Step 3: PROPOSE FIX
print("\nStep 3 — PROPOSE FIX")
snippet_id = obs2.current_snippet.id if obs2.current_snippet else "s001"
action3 = ReviewerAction(
    action_type="propose_fix",
    snippet_id=snippet_id,
    bug_type=BugType.OFF_BY_ONE,
    proposed_fix="return sum(numbers) / len(numbers)",
)
obs3, reward3, done3, info3 = env.step(action3)
print(f"  reward={reward3:.4f}")
print(f"  explanation: {info3['reward_breakdown']['explanation']}")

print(f"\nRender:\n{env.render()}")
print("\nDay 2 complete!")