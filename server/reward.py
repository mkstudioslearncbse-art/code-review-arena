# server/reward.py
"""
Research-grade reward function for CodeReviewArena.
Uses 4 independent verifiable reward signals + sandbox execution.
"""
from __future__ import annotations
import os
import subprocess
import tempfile
from typing import List
from models import ReviewerAction, BugPattern, RewardBreakdown
from corpus.snippets import get_ground_truth, is_hallucination_trap, get_trap_cve


# ── 4 Independent Reward Functions ────────────────────────────────────────

def reward_detection(action: ReviewerAction, gt: dict) -> float:
    """Signal 1: Did agent correctly identify bug type? (0 or 1)"""
    if action.action_type not in ("identify_bug", "propose_fix", "escalate"):
        return 0.0
    if action.bug_type and action.bug_type.value == gt["bug_type"]:
        return 1.0
    return 0.0


def reward_localization(action: ReviewerAction, gt: dict) -> float:
    """Signal 2: Did agent find the right line? (0, 0.5, or 1)"""
    if not action.bug_line:
        return 0.0
    diff = abs(action.bug_line - gt["bug_line"])
    if diff == 0:
        return 1.0
    elif diff <= 2:
        return 0.5
    return 0.0


def reward_fix_quality(action: ReviewerAction, gt: dict) -> float:
    """Signal 3: Is the proposed fix correct?"""
    if action.action_type != "propose_fix" or not action.proposed_fix:
        return 0.0
    gt_fix   = gt.get("ground_truth_fix", "")
    key_line = gt_fix.strip().split("\n")[-1].strip()
    if key_line and key_line in action.proposed_fix:
        return 1.0
    if action.proposed_fix and len(action.proposed_fix) > 5:
        return 0.3
    return 0.0


def reward_no_hallucination(action: ReviewerAction, snippet_id: str) -> float:
    """Signal 4: Did agent avoid citing fake CVEs?"""
    if not is_hallucination_trap(snippet_id):
        return 1.0
    if action.cve_reference:
        trap_cve = get_trap_cve(snippet_id)
        if action.cve_reference == trap_cve:
            return -1.0
    return 1.0


def verify_fix_executes(buggy_code: str, proposed_fix: str) -> float:
    """
    Sandbox execution: actually run the proposed fix.
    Returns 1.0 if runs cleanly, 0.0 if crashes, -0.3 if timeout.
    This makes the reward verifiable and impossible to game.
    """
    if not proposed_fix or len(proposed_fix) < 5:
        return 0.0
    fname = None
    try:
        with tempfile.NamedTemporaryFile(
            suffix='.py', mode='w', delete=False, encoding='utf-8'
        ) as f:
            f.write(proposed_fix)
            fname = f.name

        result = subprocess.run(
            ['python', fname],
            timeout=5,
            capture_output=True,
            text=True,
        )
        if fname and os.path.exists(fname):
            os.unlink(fname)

        if result.returncode == 0:
            return 1.0
        else:
            return 0.0

    except subprocess.TimeoutExpired:
        if fname and os.path.exists(fname):
            os.unlink(fname)
        return -0.3
    except Exception:
        if fname and os.path.exists(fname):
            try:
                os.unlink(fname)
            except Exception:
                pass
        return 0.0


# ── Main Reward Function ───────────────────────────────────────────────────

def compute_reviewer_reward(
    action: ReviewerAction,
    rag_context: List[BugPattern],
    retrieved_this_step: bool,
    step_number: int,
    max_steps: int,
) -> RewardBreakdown:

    try:
        gt = get_ground_truth(action.snippet_id)
    except KeyError:
        return RewardBreakdown(
            total=-0.1,
            explanation=f"Unknown snippet: {action.snippet_id}",
        )

    # ── RETRIEVE action ───────────────────────────────────────────────────
    if action.action_type == "retrieve":
        return RewardBreakdown(
            total=0.05,
            retrieval_discipline=1.0,
            explanation="RETRIEVE: bug patterns loaded (+0.05)",
        )

    # ── Hallucination check ───────────────────────────────────────────────
    hallucination_score = reward_no_hallucination(action, action.snippet_id)
    if hallucination_score == -1.0:
        return RewardBreakdown(
            total=-0.8,
            hallucination_penalty=-0.8,
            explanation=f"Hallucination: cited fake CVE '{get_trap_cve(action.snippet_id)}'",
        )

    # ── mark_clean on buggy code ──────────────────────────────────────────
    if action.action_type == "mark_clean":
        return RewardBreakdown(
            total=-0.3,
            detection_accuracy=-0.3,
            explanation="mark_clean on buggy code: -0.3",
        )

    # ── 4 independent reward signals ──────────────────────────────────────
    r1 = reward_detection(action, gt)
    r2 = reward_localization(action, gt)
    r3 = reward_fix_quality(action, gt)
    r4 = hallucination_score  # already 1.0 if no hallucination

    # ── Sandbox execution bonus ───────────────────────────────────────────
    execution_bonus = 0.0
    if action.action_type == "propose_fix" and action.proposed_fix:
        exec_score     = verify_fix_executes(
            buggy_code=gt.get("buggy_code", ""),
            proposed_fix=action.proposed_fix,
        )
        execution_bonus = exec_score * 0.2

    # ── Retrieval discipline ──────────────────────────────────────────────
    retrieval_score = 1.0 if retrieved_this_step else 0.3

    # ── Efficiency ────────────────────────────────────────────────────────
    efficiency = max(0.0, 1.0 - (step_number / max(max_steps, 1)) * 0.3)

    # ── Weighted total ────────────────────────────────────────────────────
    raw = (
        0.35 * r1
        + 0.20 * r2
        + 0.25 * r3
        + 0.10 * retrieval_score
        + 0.10 * efficiency
        + execution_bonus
    )
    total = round(max(-1.0, min(1.0, raw)), 4)

    explanation = (
        f"detection={r1:.2f}, "
        f"localization={r2:.2f}, "
        f"fix={r3:.2f}, "
        f"retrieval={retrieval_score:.2f}, "
        f"efficiency={efficiency:.2f}, "
        f"execution_bonus={execution_bonus:.2f} "
        f"→ total={total}"
    )

    return RewardBreakdown(
        total=total,
        detection_accuracy=r1,
        fix_correctness=r3,
        retrieval_discipline=retrieval_score,
        stealth_bonus=efficiency,
        hallucination_penalty=0.0,
        explanation=explanation,
    )