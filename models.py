# models.py
from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class BugType(str, Enum):
    OFF_BY_ONE        = "off_by_one"
    WRONG_OPERATOR    = "wrong_operator"
    NULL_POINTER      = "null_pointer"
    INTEGER_OVERFLOW  = "integer_overflow"
    SQL_INJECTION     = "sql_injection"
    PATH_TRAVERSAL    = "path_traversal"
    RACE_CONDITION    = "race_condition"
    MUTABLE_DEFAULT   = "mutable_default"
    WRONG_COMPARISON  = "wrong_comparison"
    INSECURE_RANDOM   = "insecure_random"
    NO_BUG            = "no_bug"


class Severity(str, Enum):
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    CRITICAL = "critical"


class AgentRole(str, Enum):
    BUG_INJECTOR   = "bug_injector"
    CODE_REVIEWER  = "code_reviewer"
    PATCH_VERIFIER = "patch_verifier"


class BugPattern(BaseModel):
    """A bug pattern in the knowledge base — retrieved via RAG."""
    bug_id:          str
    name:            str
    description:     str
    example_buggy:   str
    example_fixed:   str
    severity:        Severity
    detection_hint:  str
    score:           float = 0.0

    def to_context_string(self) -> str:
        return (
            f"[{self.bug_id}] {self.name}\n"
            f"Description: {self.description}\n"
            f"Detection hint: {self.detection_hint}\n"
            f"Example buggy: {self.example_buggy}\n"
            f"Example fixed: {self.example_fixed}"
        )


class CodeSnippet(BaseModel):
    """A code snippet in the review queue."""
    id:               str
    title:            str
    language:         str = "python"
    clean_code:       str
    buggy_code:       str
    bug_type:         BugType
    bug_line:         int
    severity:         Severity
    is_reviewed:      bool = False
    is_hallucination_trap: bool = False


class InjectorAction(BaseModel):
    """Action taken by the BugInjector agent."""
    action_type:  str   # "inject" or "skip"
    snippet_id:   str
    bug_type:     Optional[BugType] = None
    bug_line:     Optional[int]     = None
    modified_code: Optional[str]   = None


class ReviewerAction(BaseModel):
    """Action taken by the CodeReviewer agent."""
    action_type:   str  # "retrieve", "identify_bug", "propose_fix",
                        # "mark_clean", "escalate"
    snippet_id:    str
    bug_type:      Optional[BugType] = None
    bug_line:      Optional[int]     = None
    proposed_fix:  Optional[str]     = None
    cve_reference: Optional[str]     = None   # hallucination trap field
    severity:      Optional[Severity] = None


class VerifierAction(BaseModel):
    """Action taken by the PatchVerifier agent."""
    action_type:    str   # "approve", "reject", "request_revision"
    snippet_id:     str
    verdict:        str   # "correct", "incorrect", "introduces_new_bug"
    explanation:    str   = ""


class CodeReviewObservation(BaseModel):
    """Full observation returned after every reset() or step()."""
    queue:                List[CodeSnippet]
    current_snippet:      Optional[CodeSnippet]
    current_snippet_idx:  int = 0
    rag_context:          List[BugPattern] = Field(default_factory=list)
    step_number:          int = 0
    snippets_processed:   int = 0
    snippets_remaining:   int = 0
    last_action:          Optional[str] = None
    last_reward:          float = 0.0
    cumulative_reward:    float = 0.0
    retrieved_this_step:  bool = False
    current_agent_role:   AgentRole = AgentRole.CODE_REVIEWER
    difficulty_level:     int = 1
    arms_race_stats:      Dict[str, Any] = Field(default_factory=dict)
    info_message:         str = ""


class RewardBreakdown(BaseModel):
    """Structured reward breakdown."""
    total:                float = Field(ge=-1.0, le=1.0)
    detection_accuracy:   float = 0.0
    fix_correctness:      float = 0.0
    retrieval_discipline: float = 0.0
    stealth_bonus:        float = 0.0
    hallucination_penalty: float = 0.0
    verification_accuracy: float = 0.0
    explanation:          str = ""