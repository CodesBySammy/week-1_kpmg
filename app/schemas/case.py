"""
Pydantic Schemas for Cases

WHY SCHEMAS ≠ MODELS:
    - Models (app/models/case.py) = database table structure (SQLAlchemy)
    - Schemas (this file) = API request/response structure (Pydantic)

    They are separate because:
      1. The database might have columns you don't want in the API (internal IDs)
      2. The API request might not include auto-generated fields (id, created_at)
      3. Update requests are different from create requests (all fields optional)
      4. You might need different response formats for different endpoints

    This separation is called the "DTO pattern" (Data Transfer Object).

HOW PYDANTIC WORKS:
    Pydantic validates data automatically. If you declare:
        title: str = Field(min_length=1, max_length=255)
    Then Pydantic will reject:
        - title=123 (wrong type)
        - title="" (too short)
        - title="x" * 300 (too long)
    And return a 422 error with details about what went wrong.

CURRICULUM CONNECTION:
    Week 1 requires: request validation, response models, validated
    input/output contracts.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.models.case import CasePriority, CaseStatus, CaseType, EscalationTier


# ── Request Schemas ──────────────────────────────────────────────


class CaseCreate(BaseModel):
    """
    Schema for creating a new case (POST /cases request body).

    Required fields: title, created_by
    Optional fields: description, priority, case_type, assigned_to
    Fields NOT in request: id, status (defaults to OPEN), timestamps
    """
    title: str = Field(
        ...,  # ... means required
        min_length=1,
        max_length=255,
        description="Brief summary of the case",
        examples=["Login page returns 500 error"],
    )
    description: Optional[str] = Field(
        None,
        max_length=5000,
        description="Detailed description of the case",
        examples=["Users clicking the login button on Chrome see a 500 error page."],
    )
    priority: CasePriority = Field(
        CasePriority.MEDIUM,
        description="Priority level",
    )
    case_type: CaseType = Field(
        CaseType.INQUIRY,
        description="Type of case",
    )
    created_by: int = Field(
        ...,
        gt=0,
        description="ID of the user creating the case",
    )
    assigned_to: Optional[int] = Field(
        None,
        gt=0,
        description="ID of the user assigned to the case",
    )
    escalation_tier: Optional[EscalationTier] = Field(
        EscalationTier.STANDARD,
        description="SLA Escalation Tier",
    )
    department: Optional[str] = Field(
        "SUPPORT",
        max_length=64,
        description="Operating Department",
    )


class CaseUpdate(BaseModel):
    """
    Schema for updating a case (PUT /cases/{case_id} request body).

    All fields are optional — only send what you want to change.
    This is the "partial update" pattern (common in REST APIs).
    """
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Updated title",
    )
    description: Optional[str] = Field(
        None,
        max_length=5000,
        description="Updated description",
    )
    status: Optional[CaseStatus] = Field(
        None,
        description="Updated status",
    )
    priority: Optional[CasePriority] = Field(
        None,
        description="Updated priority",
    )
    case_type: Optional[CaseType] = Field(
        None,
        description="Updated type",
    )
    assigned_to: Optional[int] = Field(
        None,
        gt=0,
        description="Updated assignee user ID",
    )
    escalation_tier: Optional[EscalationTier] = Field(
        None,
        description="Updated SLA Escalation Tier",
    )
    department: Optional[str] = Field(
        None,
        max_length=64,
        description="Updated Operating Department",
    )


# ── Response Schemas ─────────────────────────────────────────────


class CaseResponse(BaseModel):
    """
    Schema for a case in API responses.

    model_config with from_attributes=True tells Pydantic to read
    data from SQLAlchemy model attributes (not just dicts).
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    status: CaseStatus
    priority: CasePriority
    case_type: CaseType
    escalation_tier: EscalationTier = EscalationTier.STANDARD
    department: str = "SUPPORT"
    created_by: int
    assigned_to: Optional[int]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]


class CaseListResponse(BaseModel):
    """Response schema for listing multiple cases."""
    cases: list[CaseResponse]
    total: int


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    username: str = Field(
        ..., min_length=2, max_length=50,
        description="Unique username",
        examples=["jdoe"],
    )
    email: str = Field(
        ..., max_length=255,
        description="Email address",
        examples=["jdoe@example.com"],
    )
    full_name: str = Field(
        ..., min_length=1, max_length=255,
        description="Full name",
        examples=["Jane Doe"],
    )
    role: str = Field(
        "analyst",
        max_length=50,
        description="User role",
        examples=["analyst", "manager", "admin"],
    )


class UserResponse(BaseModel):
    """Schema for user in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    full_name: str
    role: str
    created_at: datetime
