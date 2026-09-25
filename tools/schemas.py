"""
Pydantic Schemas and JSON Contracts for AI Tool Integrations.
Enforces strict argument validation, deterministic errors, and typed responses.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class ToolError(BaseModel):
    """Deterministic, structured error response for tool failures."""
    error_code: str = Field(..., description="Machine-readable error identifier")
    message: str = Field(..., description="Human-readable explanation")
    details: Dict[str, Any] = Field(default_factory=dict)
    retryable: bool = Field(default=False, description="Whether caller may retry with backoff")


class RetrieveCaseInput(BaseModel):
    """Input contract for TOOL 1: retrieve_case_details."""
    case_id: int = Field(..., gt=0, description="Positive integer identifier of the case")

    @field_validator("case_id")
    def validate_positive(cls, v):
        if v <= 0:
            raise ValueError("case_id must be a strictly positive integer")
        return v


class RetrieveCaseOutput(BaseModel):
    """Output contract for TOOL 1: retrieve_case_details."""
    case_id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    case_type: Optional[str] = "INQUIRY"
    created_by: int
    assigned_to: Optional[int] = None
    created_at: str
    resolved_at: Optional[str] = None
    escalation_tier: Optional[str] = "STANDARD"
    department: Optional[str] = "SUPPORT"
    audit_notes: Optional[str] = None


class UpdateTicketInput(BaseModel):
    """Input contract for TOOL 2: update_ticket (Write Operation)."""
    ticket_id: Optional[int] = Field(default=None, gt=0, description="Target ticket/case ID")
    case_id: Optional[int] = Field(default=None, gt=0, description="Alias for ticket_id")
    status: Optional[str] = Field(
        default=None,
        description="Target status: 'open', 'in_progress', 'resolved', 'closed'",
    )
    new_status: Optional[str] = Field(
        default=None,
        description="Alias for status",
    )
    comment: Optional[str] = Field(
        default="Status update",
        description="Justification note for the update",
    )
    escalation_tier: Optional[str] = Field(
        default=None,
        description="Target escalation tier: 'STANDARD', 'PRIORITY', 'CRITICAL_ESC'",
    )
    escalation_reason: Optional[str] = Field(
        default=None,
        description="Justification for escalation tier modification",
    )
    approval_id: Optional[str] = Field(
        default=None,
        description="Mandatory human approval token required before write execution",
    )
    approval_token: Optional[str] = Field(
        default=None,
        description="Alias for approval_id",
    )
    idempotency_key: Optional[str] = Field(
        default=None,
        description="Optional client-supplied idempotency key to prevent duplicate updates",
    )

    model_config = {"extra": "allow"}

    def __init__(self, **data):
        super().__init__(**data)
        if self.ticket_id is None and self.case_id is not None:
            self.ticket_id = self.case_id
        elif self.case_id is None and self.ticket_id is not None:
            self.case_id = self.ticket_id

        if self.status is None and self.new_status is not None:
            self.status = self.new_status
        elif self.new_status is None and self.status is not None:
            self.new_status = self.status

        if self.approval_id is None and self.approval_token is not None:
            self.approval_id = self.approval_token
        elif self.approval_token is None and self.approval_id is not None:
            self.approval_token = self.approval_id

        if self.ticket_id is None:
            raise ValueError("ticket_id (or case_id) is required")
        if self.status is None:
            raise ValueError("status (or new_status) is required")

        allowed = {"open", "in_progress", "resolved", "closed"}
        norm = self.status.lower().strip()
        if norm not in allowed:
            raise ValueError(f"Invalid status '{self.status}'. Allowed values are: {allowed}")
        self.status = norm
        self.new_status = norm


class UpdateTicketOutput(BaseModel):
    """Output contract for TOOL 2: update_ticket."""
    ticket_id: int
    case_id: Optional[int] = None
    previous_status: str
    new_status: str
    status: Optional[str] = None
    comment: Optional[str] = None
    escalation_tier: Optional[str] = None
    approval_id: Optional[str] = None
    updated_by: str
    updated_at: str
    is_idempotent_replay: bool = False
    audit_event_id: str

    def __init__(self, **data):
        super().__init__(**data)
        if self.case_id is None:
            self.case_id = self.ticket_id
        if self.status is None:
            self.status = self.new_status


