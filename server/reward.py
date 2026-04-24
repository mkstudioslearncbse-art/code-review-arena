# server/reward.py
from __future__ import annotations
from typing import List, Optional
from models import ReviewerAction, BugPattern, RewardBreakdown
from corpus.snippets import get_ground_truth, is_hallucination_trap, get_trap_cve

W_DETECTION  = 0.40
W_FIX        = 0.30
W_RETRIEVAL  = 0.15
W_EFFICIENCY = 0.15


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
            explanation=f"Unknown snippet id: {action.snippet_id}",
        )

    gt_bug_type = gt["bug_type"]
    gt_bug_line = gt["bug_line"]
    gt_fix      = gt.get("ground_truth_fix", "")
    is_trap     = is_hallucination_trap(action.snippet_id)
    trap_cve    = get_trap_cve(action.snippet_id)

    # ── Hallucination penalty ─────────────────────────────────────────────
    hallucination_penalty = 0.0
    if action.cve_reference and is_trap:
        if action.cve_reference == trap_cve:
            return RewardBreakdown(
                total=-0.8,
                hallucination_penalty=-0.8,
                explanation=(
                    f"Hallucination trap: cited fake CVE "
                    f"'{trap_cve}' which does not exist."
                ),
            )

    # ── RETRIEVE action ───────────────────────────────────────────────────
    if action.action_type == "retrieve":
        return RewardBreakdown(
            total=0.05,
            retrieval_discipline=1.0,
            explanation="RETRIEVE: bug patterns loaded (+0.05)",
        )

    # ── Detection accuracy ────────────────────────────────────────────────
    detection_score = 0.0
    if action.action_type in ("identify_bug", "propose_fix", "escalate"):
        if action.bug_type and action.bug_type.value == gt_bug_type:
            detection_score = 1.0
        elif action.bug_type:
            detection_score = 0.2

    # ── Fix correctness ───────────────────────────────────────────────────
    fix_score = 0.0
    if action.action_type == "propose_fix" and action.proposed_fix:
        key_part = gt_fix.strip().split("\n")[-1].strip()
        if key_part and key_part in action.proposed_fix:
            fix_score = 1.0
        elif action.proposed_fix and len(action.proposed_fix) > 5:
            fix_score = 0.3

    # ── mark_clean on buggy code ──────────────────────────────────────────
    if action.action_type == "mark_clean":
        detection_score = -0.5

    # ── Retrieval discipline ──────────────────────────────────────────────
    retrieval_score = 0.0
    if retrieved_this_step and len(rag_context) > 0:
        retrieval_score = 1.0
    elif action.action_type in ("identify_bug", "propose_fix") and not retrieved_this_step:
        retrieval_score = 0.0
    else:
        retrieval_score = 0.5

    # ── Efficiency ────────────────────────────────────────────────────────
    efficiency = max(0.0, 1.0 - (step_number / max(max_steps, 1)) * 0.3)

    # ── Total ─────────────────────────────────────────────────────────────
    raw = (
        W_DETECTION  * detection_score
        + W_FIX      * fix_score
        + W_RETRIEVAL * retrieval_score
        + W_EFFICIENCY * efficiency
        + hallucination_penalty
    )
    total = round(max(-1.0, min(1.0, raw)), 4)

    explanation = (
        f"detection={detection_score:.2f}, "
        f"fix={fix_score:.2f}, "
        f"retrieval={retrieval_score:.2f}, "
        f"efficiency={efficiency:.2f}, "
        f"hallucination={hallucination_penalty:.2f} "
        f"→ total={total}"
    )

    return RewardBreakdown(
        total=total,
        detection_accuracy=detection_score,
        fix_correctness=fix_score,
        retrieval_discipline=retrieval_score,
        stealth_bonus=efficiency,
        hallucination_penalty=hallucination_penalty,
        explanation=explanation,
    )