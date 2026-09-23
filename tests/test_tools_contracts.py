"""
Unit Tests for Week 4 Typed AI Tools and Contracts.

Verifies:
  1. Input/output Pydantic schema validation.
  2. Deterministic ToolError structures and error codes.
  3. Safe read tool (retrieve_case_details) functionality and error handling.
  4. Consequential write tool (update_ticket) requiring human approval.
  5. Idempotent execution and replay protection.
"""

import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database.session import SessionLocal, create_tables
from app.models.case import Case, CasePriority, CaseStatus, User
from security.auth import UserPrincipal
from tools.retrieve_case import retrieve_case_details
from tools.schemas import (
    RetrieveCaseInput,
    RetrieveCaseOutput,
    ToolError,
    UpdateTicketInput,
    UpdateTicketOutput,
)
from tools.update_ticket import IdempotencyStore, update_ticket


@pytest.fixture
def db_session():
    """Provide a clean database session with initialized tables and seed data."""
    create_tables()
    db: Session = SessionLocal()
    try:
        # Create a test creator user if not exists
        user = db.query(User).filter(User.username == "tool_test_user").first()
        if not user:
            user = User(
                username="tool_test_user",
                email="tool_user@example.com",
                full_name="Tool User",
                role="agent",
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Create a test case
        test_case = db.query(Case).filter(Case.title == "Test Case for Tools").first()
        if not test_case:
            test_case = Case(
                title="Test Case for Tools",
                description="A case to test tool integrations",
                status=CaseStatus.OPEN,
                priority=CasePriority.MEDIUM,
                created_by=user.id,
            )
            db.add(test_case)
            db.commit()
            db.refresh(test_case)
        else:
            test_case.status = CaseStatus.OPEN
            db.commit()
            db.refresh(test_case)

        yield db, test_case, user
    finally:
        db.close()


def test_tool_input_schema_validation():
    """Verify strict type validation on tool inputs."""
    # Valid input
    valid_input = RetrieveCaseInput(case_id=1)
    assert valid_input.case_id == 1

    # Invalid case_id (must be > 0)
    with pytest.raises(ValidationError):
        RetrieveCaseInput(case_id=-5)


def test_tool_error_model():
    """Verify deterministic ToolError structure."""
    err = ToolError(
        error_code="CASE_NOT_FOUND",
        message="Case ID 999 does not exist",
        details={"case_id": 999},
        retryable=False,
    )
    assert err.error_code == "CASE_NOT_FOUND"
    assert err.retryable is False
    assert err.details["case_id"] == 999


def test_retrieve_case_success(db_session):
    """Verify safe read tool retrieves an existing case correctly."""
    db, test_case, user = db_session
    principal = UserPrincipal(user_id=user.id, username=user.username, email=user.email, role="agent")
    inp = RetrieveCaseInput(case_id=test_case.id)
    out, err = retrieve_case_details(inp, principal=principal, db=db)

    assert err is None
    assert isinstance(out, RetrieveCaseOutput)
    assert out.case_id == test_case.id
    assert out.title == test_case.title
    assert out.status.upper() == "OPEN"


def test_retrieve_case_not_found(db_session):
    """Verify read tool returns deterministic ToolError when case does not exist."""
    db, _, user = db_session
    principal = UserPrincipal(user_id=user.id, username=user.username, email=user.email, role="agent")
    inp = RetrieveCaseInput(case_id=999999)
    out, err = retrieve_case_details(inp, principal=principal, db=db)

    assert out is None
    assert isinstance(err, ToolError)
    assert err.error_code == "CASE_NOT_FOUND"
    assert err.retryable is False


def test_update_ticket_without_approval_fails(db_session):
    """Verify consequential write tool strictly rejects execution when approval is missing."""
    db, test_case, user = db_session
    manager_principal = UserPrincipal(user_id=user.id, username=user.username, email=user.email, role="manager")
    inp = UpdateTicketInput(
        case_id=test_case.id,
        new_status="in_progress",
        comment="Beginning investigation",
        approval_token=None,  # Missing approval token!
    )
    out, err = update_ticket(inp, principal=manager_principal, db=db)

    assert out is None
    assert isinstance(err, ToolError)
    assert err.error_code == "APPROVAL_REQUIRED"
    assert "Human approval token is required" in err.message


def test_update_ticket_with_invalid_approval_fails(db_session):
    """Verify consequential write tool rejects unverified approval tokens."""
    db, test_case, user = db_session
    manager_principal = UserPrincipal(user_id=user.id, username=user.username, email=user.email, role="manager")
    inp = UpdateTicketInput(
        case_id=test_case.id,
        new_status="in_progress",
        approval_token="bogus-invalid-token",
    )
    out, err = update_ticket(inp, principal=manager_principal, db=db)

    assert out is None
    assert isinstance(err, ToolError)
    assert err.error_code == "INVALID_APPROVAL"


def test_update_ticket_with_valid_approval_and_idempotency(db_session):
    """Verify consequential write tool succeeds with valid approval and is idempotent."""
    from workflow.approval import ApprovalManager

    db, test_case, user = db_session
    mgr = ApprovalManager()
    manager_principal = UserPrincipal(user_id=user.id, username=user.username, email=user.email, role="manager")

    # Create approval request
    req = mgr.create_approval_request(
        action_type="update_ticket",
        payload={"case_id": test_case.id, "new_status": "in_progress"},
        requested_by=user.username,
        user_role="agent",
    )
    # Manager approves it
    token = mgr.approve_request(req.request_id, reviewer="manager_alice")

    inp = UpdateTicketInput(
        case_id=test_case.id,
        new_status="in_progress",
        comment="Approved status update",
        approval_token=token,
        idempotency_key="idemp-key-12345",
    )

    # First execution - should succeed
    res1, err1 = update_ticket(inp, principal=manager_principal, approval_verifier=mgr, db=db)
    assert err1 is None
    assert isinstance(res1, UpdateTicketOutput)
    assert res1.case_id == test_case.id
    assert res1.status.lower() == "in_progress"

    # Second execution with same idempotency key - should return cached result without duplicate update
    res2, err2 = update_ticket(inp, principal=manager_principal, approval_verifier=mgr, db=db)
    assert err2 is None
    assert isinstance(res2, UpdateTicketOutput)
    assert res2.case_id == test_case.id
    assert res2.status.lower() == "in_progress"
