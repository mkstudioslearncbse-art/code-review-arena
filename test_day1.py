# test_day1.py
from models import BugType, Severity, CodeSnippet
from corpus.snippets import (
    get_snippets_for_task,
    get_ground_truth,
    is_hallucination_trap,
    SNIPPETS_RAW
)

# Test task slices
t1 = get_snippets_for_task("task1_easy")
t2 = get_snippets_for_task("task2_medium")
t3 = get_snippets_for_task("task3_hard")
print(f"Task 1: {len(t1)} snippets")
print(f"Task 2: {len(t2)} snippets")
print(f"Task 3: {len(t3)} snippets")

# Test ground truth
gt = get_ground_truth("s001")
print(f"\ns001 bug type: {gt['bug_type']}")
print(f"s001 bug line: {gt['bug_line']}")

# Test hallucination traps
print(f"\ns009 is trap: {is_hallucination_trap('s009')}")
print(f"s010 is trap: {is_hallucination_trap('s010')}")
print(f"s001 is trap: {is_hallucination_trap('s001')}")

# Test bug types present
bug_types = set(s["bug_type"] for s in SNIPPETS_RAW)
print(f"\nBug types in corpus: {bug_types}")

# Test severity distribution
severities = {}
for s in SNIPPETS_RAW:
    sev = s["severity"]
    severities[sev] = severities.get(sev, 0) + 1
print(f"Severity distribution: {severities}")

print("\nDay 1 complete!")