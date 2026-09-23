"""
Workflow State Machine and Execution Context.
Maintains state explicitly across all workflow transitions.
"""
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field


class WorkflowState(str, Enum):
    REQUEST_RECEIVED = "REQUEST_RECEIVED"
    INTENT_DETECTED = "INTENT_DETECTED"
    TOOL_PROPOSED = "TOOL_PROPOSED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    APPROVED = "APPROVED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    APPROVAL_REJECTED = "APPROVAL_REJECTED"
    APPROVAL_EXPIRED = "APPROVAL_EXPIRED"
    TIMED_OUT = "TIMED_OUT"
    FAILED = "FAILED"


# Valid state transitions graph
VALID_TRANSITIONS: Dict[WorkflowState, List[WorkflowState]] = {
    WorkflowState.REQUEST_RECEIVED: [
        WorkflowState.INTENT_DETECTED,
        WorkflowState.FAILED,
    ],
    WorkflowState.INTENT_DETECTED: [
        WorkflowState.TOOL_PROPOSED,
        WorkflowState.EXECUTING,  # Direct execution for pure RAG query
        WorkflowState.FAILED,
    ],
    WorkflowState.TOOL_PROPOSED: [
        WorkflowState.APPROVAL_REQUIRED,
        WorkflowState.APPROVED,
        WorkflowState.EXECUTING,  # Safe read tools execute directly
        WorkflowState.FAILED,
    ],
    WorkflowState.APPROVAL_REQUIRED: [
        WorkflowState.APPROVED,
        WorkflowState.APPROVAL_REJECTED,
        WorkflowState.APPROVAL_EXPIRED,
        WorkflowState.FAILED,
    ],
    WorkflowState.APPROVED: [
        WorkflowState.EXECUTING,
        WorkflowState.FAILED,
    ],
    WorkflowState.EXECUTING: [
        WorkflowState.COMPLETED,
        WorkflowState.TIMED_OUT,
        WorkflowState.FAILED,
    ],
    WorkflowState.APPROVAL_REJECTED: [],
    WorkflowState.APPROVAL_EXPIRED: [],
    WorkflowState.TIMED_OUT: [WorkflowState.FAILED],
    WorkflowState.COMPLETED: [],
    WorkflowState.FAILED: [],
}


class WorkflowContext(BaseModel):
    """
    Serializable execution state tracking request progress,
    decisions, tool parameters, approvals, and outcomes.
    """
    request_id: str = Field(default_factory=lambda: f"req_{uuid.uuid4().hex[:12]}")
    correlation_id: str = Field(default_factory=lambda: f"corr_{uuid.uuid4().hex[:12]}")
    username: str
    user_role: str
    raw_query: str
    intent: Optional[str] = None
    current_state: WorkflowState = WorkflowState.REQUEST_RECEIVED
    selected_tool: Optional[str] = None
    tool_arguments: Optional[Dict[str, Any]] = None
    approval_id: Optional[str] = None
    approval_status: Optional[str] = None
    tool_result: Optional[Dict[str, Any]] = None
    rag_result: Optional[Dict[str, Any]] = None
    final_response: Optional[str] = None
    error: Optional[str] = None
    retry_count: int = 0
    state_history: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def transition_to(self, new_state: WorkflowState, reason: Optional[str] = None):
        """Validates and applies a state transition."""
        allowed = VALID_TRANSITIONS.get(self.current_state, [])
        if new_state not in allowed:
            raise ValueError(
                f"Invalid workflow state transition: cannot move from {self.current_state} to {new_state}."
            )

        now_iso = datetime.now(timezone.utc).isoformat()
        self.state_history.append({
            "from_state": self.current_state.value,
            "to_state": new_state.value,
            "timestamp": now_iso,
            "reason": reason,
        })
        self.current_state = new_state
        self.updated_at = now_iso
