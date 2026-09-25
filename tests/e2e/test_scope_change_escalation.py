"""
End-to-End Test Suite for Week 5 Scope Change (SCR-2026-05):
Case Escalation Tiering & Multi-Department Segregation.
"""
import pytest
from app.database.session import SessionLocal, create_tables
from app.models.case import Case, CasePriority, CaseStatus, CaseType, EscalationTier, User
from app.schemas.case import CaseCreate, CaseUpdate
from app.services.case_service import CaseService
from security.auth import UserPrincipal
from security.rbac import check_department_access, require_department_access
from tools.retrieve_case import retrieve_case_details
from tools.update_ticket import update_ticket
from tools.schemas import UpdateTicketInput, RetrieveCaseInput
from workflow.approval import approval_manager
from fastapi import HTTPException


@pytest.fixture(scope="module")
def setup_db():
    create_tables()
    db = SessionLocal()
    # Ensure creator and assignee users exist
    creator = db.query(User).filter(User.username == "esc_creator").first()
    if not creator:
        creator = User(username="esc_creator", email="esc_creator@example.com", full_name="Esc Creator", role="operator")
        db.add(creator)
    
    supervisor = db.query(User).filter(User.username == "esc_supervisor").first()
    if not supervisor:
        supervisor = User(username="esc_supervisor", email="esc_supervisor@example.com", full_name="Esc Supervisor", role="supervisor")
        db.add(supervisor)

    db.commit()
    yield db
    db.close()


def test_scope_change_create_case_with_escalation_tier(setup_db):
    db = setup_db
    service = CaseService()
    creator = db.query(User).filter(User.username == "esc_creator").first()

    case_in = CaseCreate(
        title="High Severity Payment Gateway Timeout",
        description="Transactions failing with HTTP 504 on checkout.",
        priority=CasePriority.HIGH,
        case_type=CaseType.BUG,
        created_by=creator.id,
        escalation_tier=EscalationTier.PRIORITY,
        department="BILLING",
    )

    created = service.create_case(db, case_in)
    assert created.id is not None
    assert created.escalation_tier == EscalationTier.PRIORITY
    assert created.department == "BILLING"

    # Verify retrieval tool returns the new fields
    principal = UserPrincipal(
        user_id=creator.id, username=creator.username, email=creator.email, role="agent", extra_permissions=["case:read"]
    )
    tool_out, err = retrieve_case_details(RetrieveCaseInput(case_id=created.id), principal, db=db)
    assert err is None
    assert tool_out is not None
    assert tool_out.escalation_tier == "PRIORITY"
    assert tool_out.department == "BILLING"


def test_scope_change_escalation_to_critical_unauthorized_for_operator(setup_db):
    db = setup_db
    service = CaseService()
    creator = db.query(User).filter(User.username == "esc_creator").first()

    case_in = CaseCreate(
        title="Standard Network Glitch",
        description="Minor lag reported in EMEA cluster.",
        priority=CasePriority.MEDIUM,
        case_type=CaseType.INQUIRY,
        created_by=creator.id,
        escalation_tier=EscalationTier.STANDARD,
        department="SUPPORT",
    )
    case_obj = service.create_case(db, case_in)

    # Operator principal tries to escalate to CRITICAL_ESC
    operator_principal = UserPrincipal(
        user_id=101, username="operator_bob", email="bob@example.com", role="operator", extra_permissions=["ticket:update"]
    )

    # Generate approval token using correct ApprovalManager API
    approval_req = approval_manager.request_approval(
        ticket_id=case_obj.id,
        target_status="in_progress",
        proposed_by=operator_principal.username,
        justification="Escalating case to critical",
    )
    # Grant approval as manager
    from security.auth import UserPrincipal as UP
    mgr_principal = UP(user_id=999, username="manager_sys", email="sys@example.com", role="manager")
    approval_manager.grant_approval(approval_req.approval_id, approver=mgr_principal)
    token = approval_req.approval_id

    tool_input = UpdateTicketInput(
        ticket_id=case_obj.id,
        status="in_progress",
        escalation_tier="CRITICAL_ESC",
        escalation_reason="Mass outage in region",
        approval_token=token,
    )

    # Operator role executing the update tool should be rejected (CRITICAL_ESC requires supervisor)
    tool_out, err = update_ticket(tool_input, operator_principal, db=db)
    assert tool_out is None
    assert err is not None
    assert err.error_code == "UNAUTHORIZED_ESCALATION"
    assert "requires supervisor or admin" in err.message


def test_scope_change_escalation_to_critical_succeeds_for_supervisor(setup_db):
    db = setup_db
    service = CaseService()
    creator = db.query(User).filter(User.username == "esc_creator").first()

    case_in = CaseCreate(
        title="Database Deadlock Outage",
        description="Deadlocks cascading across billing tables.",
        priority=CasePriority.CRITICAL,
        case_type=CaseType.BUG,
        created_by=creator.id,
        escalation_tier=EscalationTier.PRIORITY,
        department="BILLING",
    )
    case_obj = service.create_case(db, case_in)

    # Supervisor principal
    supervisor_principal = UserPrincipal(
        user_id=202, username="supervisor_alice", email="alice@example.com", role="supervisor", extra_permissions=["ticket:update"]
    )

    # Generate valid approval token using correct ApprovalManager API
    approval_req = approval_manager.request_approval(
        ticket_id=case_obj.id,
        target_status="in_progress",
        proposed_by=supervisor_principal.username,
        justification="Executive escalation authorized",
    )
    # Grant approval as manager
    from security.auth import UserPrincipal as UP
    mgr_principal = UP(user_id=999, username="manager_sys", email="sys@example.com", role="manager")
    approval_manager.grant_approval(approval_req.approval_id, approver=mgr_principal)
    token = approval_req.approval_id

    tool_input = UpdateTicketInput(
        ticket_id=case_obj.id,
        status="in_progress",
        escalation_tier="CRITICAL_ESC",
        escalation_reason="Production billing system down",
        approval_token=token,
    )

    tool_out, err = update_ticket(tool_input, supervisor_principal, db=db)
    assert err is None
    assert tool_out is not None
    assert tool_out.escalation_tier == "CRITICAL_ESC"

    # Confirm in DB
    refetched = service.get_case(db, case_obj.id)
    assert refetched.escalation_tier == EscalationTier.CRITICAL_ESC


def test_department_access_boundaries():
    # Support agent
    support_agent = UserPrincipal(
        user_id=301, username="support_jim", email="jim@example.com", role="agent", department="SUPPORT"
    )
    # Billing agent
    billing_agent = UserPrincipal(
        user_id=302, username="billing_sara", email="sara@example.com", role="agent", department="BILLING"
    )
    # Admin
    admin_user = UserPrincipal(
        user_id=1, username="admin", email="admin@example.com", role="admin", department="SUPPORT"
    )

    # Support agent can access SUPPORT, but NOT BILLING or LEGAL
    assert check_department_access(support_agent, "SUPPORT") is True
    assert check_department_access(support_agent, "BILLING") is False
    assert check_department_access(support_agent, "LEGAL") is False

    with pytest.raises(HTTPException) as exc_info:
        require_department_access(support_agent, "BILLING")
    assert exc_info.value.status_code == 403

    # Billing agent can access BILLING, but NOT SUPPORT
    assert check_department_access(billing_agent, "BILLING") is True
    assert check_department_access(billing_agent, "SUPPORT") is False

    # Admin can access any department
    assert check_department_access(admin_user, "SUPPORT") is True
    assert check_department_access(admin_user, "BILLING") is True
    assert check_department_access(admin_user, "LEGAL") is True
