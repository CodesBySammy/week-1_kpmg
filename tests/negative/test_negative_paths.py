"""
Week 5 Negative-Path Test Suite.
Tests boundary conditions, invalid inputs, unauthorized access, and error contract compliance.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from pydantic import ValidationError as PydanticValidationError

client = TestClient(app)


# ─── NEGATIVE: Invalid Schema Inputs ──────────────────────────────────────────

class TestInvalidSchemas:

    def test_neg_case_title_too_long_422(self):
        """Negative: POST /cases/ with title > 255 chars returns 422."""
        from app.schemas.case import CaseCreate
        with pytest.raises(PydanticValidationError):
            CaseCreate(title="X" * 256, created_by=1)

    def test_neg_case_title_empty_422(self):
        """Negative: Empty title is rejected."""
        from app.schemas.case import CaseCreate
        with pytest.raises(PydanticValidationError):
            CaseCreate(title="", created_by=1)

    def test_neg_invalid_priority_enum(self):
        """Negative: Invalid priority enum value is rejected."""
        from app.schemas.case import CaseCreate
        with pytest.raises(PydanticValidationError):
            CaseCreate(title="Test", created_by=1, priority="SUPER_HIGH")

    def test_neg_invalid_status_enum(self):
        """Negative: Invalid status enum value is rejected."""
        from app.schemas.case import CaseUpdate
        with pytest.raises(PydanticValidationError):
            CaseUpdate(status="PENDING")

    def test_neg_invalid_escalation_tier(self):
        """Negative: Invalid escalation_tier enum is rejected."""
        from app.schemas.case import CaseCreate
        with pytest.raises(PydanticValidationError):
            CaseCreate(title="Test", created_by=1, escalation_tier="ULTRA_CRITICAL")


# ─── NEGATIVE: API Boundary Violations ────────────────────────────────────────

class TestApiBoundaries:

    def test_neg_get_case_nonexistent_returns_404(self):
        """Negative: Nonexistent case ID returns 404."""
        resp = client.get("/api/v1/cases/999999")
        assert resp.status_code == 404

    def test_neg_get_case_string_id_returns_422(self):
        """Negative: String case ID returns 422 Unprocessable Entity."""
        resp = client.get("/api/v1/cases/not-a-number")
        assert resp.status_code == 422

    def test_neg_update_case_no_body_returns_422(self):
        """Negative: PUT /cases/{id} with empty body returns 422."""
        resp = client.put("/api/v1/cases/1", json={})
        assert resp.status_code in (400, 422)

    def test_neg_rag_query_empty_body_returns_422(self):
        """Negative: POST /rag/query with no body returns 422."""
        resp = client.post("/api/v1/rag/query", json={})
        assert resp.status_code == 422


# ─── NEGATIVE: Authentication / Authorization ─────────────────────────────────

class TestAuthNegative:

    def test_neg_workflow_no_auth_returns_401(self):
        """Negative: Workflow execute without Authorization header returns 401."""
        resp = client.post("/api/v1/workflow/execute", json={"query": "show case 1"})
        assert resp.status_code == 401

    def test_neg_workflow_invalid_jwt_returns_401(self):
        """Negative: Workflow execute with fake JWT returns 401."""
        resp = client.post(
            "/api/v1/workflow/execute",
            json={"query": "show case 1"},
            headers={"Authorization": "Bearer totally.fake.jwt"}
        )
        assert resp.status_code == 401

    def test_neg_viewer_cannot_use_workflow(self):
        """Negative: Viewer role is rejected from consequential workflow actions."""
        from tools.update_ticket import update_ticket
        from tools.schemas import UpdateTicketInput
        from security.auth import UserPrincipal
        viewer = UserPrincipal(user_id=1, username="v", email="v@x.com", role="viewer")
        t = UpdateTicketInput(ticket_id=1, status="closed", approval_token="tok")
        out, err = update_ticket(t, viewer)
        assert out is None
        assert err.error_code == "UNAUTHORIZED"

    def test_neg_tampered_approval_token_rejected(self):
        """Negative: Tampered approval token string is not found and rejected."""
        from workflow.approval import ApprovalManager
        mgr = ApprovalManager()
        is_valid, msg = mgr.verify_approval("tampered-token-that-doesnt-exist")
        assert is_valid is False

    def test_neg_expired_approval_token_rejected(self):
        """Negative: Expired approval token is detected and rejected."""
        import time
        from workflow.approval import ApprovalManager, ApprovalStatus
        from security.auth import UserPrincipal

        mgr = ApprovalManager()
        req = mgr.request_approval(
            ticket_id=10, target_status="closed",
            proposed_by="test", justification="expiry test", ttl_seconds=1
        )
        manager = UserPrincipal(user_id=99, username="mgr", email="m@x.com", role="manager")
        mgr.grant_approval(req.approval_id, approver=manager)
        time.sleep(1.2)
        is_valid, msg = mgr.verify_approval(req.approval_id)
        assert is_valid is False
        assert "expired" in msg.lower()


# ─── NEGATIVE: Tool Contract Violations ───────────────────────────────────────

class TestToolNegative:

    def test_neg_retrieve_case_zero_id_rejected(self):
        """Negative: case_id=0 is rejected at schema level."""
        from tools.schemas import RetrieveCaseInput
        with pytest.raises(PydanticValidationError):
            RetrieveCaseInput(case_id=0)

    def test_neg_update_ticket_missing_ticket_id(self):
        """Negative: UpdateTicketInput without ticket_id raises ValueError."""
        from tools.schemas import UpdateTicketInput
        with pytest.raises((PydanticValidationError, ValueError)):
            UpdateTicketInput(status="closed")

    def test_neg_update_ticket_invalid_status_string(self):
        """Negative: UpdateTicketInput with completely invalid status is rejected."""
        from tools.schemas import UpdateTicketInput
        with pytest.raises((PydanticValidationError, ValueError)):
            UpdateTicketInput(ticket_id=1, status="PENDING_REVIEW")

    def test_neg_escalation_tier_invalid_string_in_tool(self):
        """Negative: update_ticket with invalid escalation_tier string returns INVALID_ESCALATION_TIER error."""
        from tools.update_ticket import update_ticket
        from tools.schemas import UpdateTicketInput
        from security.auth import UserPrincipal
        from workflow.approval import approval_manager  # global singleton

        principal = UserPrincipal(user_id=1, username="sup", email="s@x.com", role="supervisor",
                                  extra_permissions=["ticket:update"])
        approver = UserPrincipal(user_id=99, username="manager_y", email="y@x.com", role="manager")

        from app.database.session import SessionLocal, create_tables
        from app.models.case import User
        from app.schemas.case import CaseCreate, CasePriority, CaseType
        from app.services.case_service import CaseService
        create_tables()
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == "neg_sup2").first()
            if not user:
                user = User(username="neg_sup2", email="negsup2@x.com", full_name="Neg Sup2", role="supervisor")
                db.add(user)
                db.commit()
                db.refresh(user)
            svc = CaseService()
            case = svc.create_case(db, CaseCreate(
                title="Neg Tier Test2", created_by=user.id,
                priority=CasePriority.MEDIUM, case_type=CaseType.INQUIRY,
            ))
            # Must use global approval_manager so update_ticket can verify it
            req = approval_manager.request_approval(
                ticket_id=case.id, target_status="in_progress",
                proposed_by="sup", justification="tier test"
            )
            approval_manager.grant_approval(req.approval_id, approver=approver)

            tool_input = UpdateTicketInput(
                ticket_id=case.id, status="in_progress",
                escalation_tier="NOT_A_REAL_TIER",
                approval_token=req.approval_id,
            )
            out, err = update_ticket(tool_input, principal, db=db)
            assert out is None
            assert err is not None
            assert err.error_code == "INVALID_ESCALATION_TIER"
        finally:
            db.close()
