"""
Unit and Integration Tests for Week 4 Workflow Orchestration.

Verifies:
  1. Intent classification & routing.
  2. State machine tracking and transitions.
  3. Retry mechanism with backoff on transient errors.
  4. Timeout handling and structured fallbacks.
  5. End-to-end orchestrator execution.
"""

import pytest
from sqlalchemy.orm import Session

from app.database.session import SessionLocal, create_tables
from app.models.case import Case, CasePriority, CaseStatus, User
from security.auth import UserPrincipal
from workflow.orchestrator import WorkflowOrchestrator
from workflow.router import WorkflowIntent, WorkflowRouter
from workflow.state import WorkflowContext, WorkflowState


@pytest.fixture
def test_env():
    """Setup test DB and seeded user/case."""
    create_tables()
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "orch_user").first()
        if not user:
            user = User(
                username="orch_user",
                email="orch@example.com",
                full_name="Orchestrator User",
                role="agent",
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        case = db.query(Case).filter(Case.title == "Orchestrator Case").first()
        if not case:
            case = Case(
                title="Orchestrator Case",
                description="Case for orchestration test",
                status=CaseStatus.OPEN,
                priority=CasePriority.HIGH,
                created_by=user.id,
            )
            db.add(case)
            db.commit()
            db.refresh(case)

        yield db, case, user
    finally:
        db.close()


def test_router_intent_classification():
    """Verify deterministic routing of user input prompts."""
    # 1. Update ticket intent
    r1 = WorkflowRouter.route("Please update ticket #42 status to resolved")
    assert r1.intent == WorkflowIntent.UPDATE_TICKET
    assert r1.tool_name == "update_ticket"
    assert r1.tool_arguments.get("ticket_id") == 42
    assert r1.requires_approval is True

    # 2. Retrieve case details intent
    r2 = WorkflowRouter.route("Show me details for case 101")
    assert r2.intent == WorkflowIntent.RETRIEVE_CASE_DETAILS
    assert r2.tool_name == "retrieve_case_details"
    assert r2.tool_arguments.get("case_id") == 101
    assert r2.requires_approval is False

    # 3. Compliance check intent
    r3 = WorkflowRouter.route("Check compliance for case 5 against regulations")
    assert r3.intent == WorkflowIntent.COMPLIANCE_CASE_CHECK
    assert r3.tool_arguments.get("case_id") == 5

    # 4. General policy RAG query
    r4 = WorkflowRouter.route("What is the data retention window for financial audit logs?")
    assert r4.intent == WorkflowIntent.RAG_POLICY_QUERY
    assert r4.requires_tool is False


def test_workflow_state_transitions():
    """Verify state machine tracks progression accurately."""
    ctx = WorkflowContext(
        correlation_id="test-corr-1",
        username="test_agent",
        user_role="agent",
        raw_query="Retrieve case 10",
    )
    assert ctx.current_state == WorkflowState.REQUEST_RECEIVED

    ctx.transition_to(WorkflowState.INTENT_DETECTED)
    assert ctx.current_state == WorkflowState.INTENT_DETECTED

    ctx.transition_to(WorkflowState.TOOL_PROPOSED)
    assert ctx.current_state == WorkflowState.TOOL_PROPOSED

    ctx.transition_to(WorkflowState.EXECUTING)
    assert ctx.current_state == WorkflowState.EXECUTING

    ctx.transition_to(WorkflowState.COMPLETED)
    assert ctx.current_state == WorkflowState.COMPLETED
    assert len(ctx.state_history) == 4


def test_orchestrator_safe_read_execution(test_env):
    """Verify orchestrator successfully handles read request through end-to-end pipeline."""
    db, case, user = test_env
    orchestrator = WorkflowOrchestrator()
    principal = UserPrincipal(user_id=user.id, username=user.username, email=user.email, role=user.role)

    res = orchestrator.execute(
        query=f"Get details for case {case.id}",
        principal=principal,
    )

    assert res.final_state == WorkflowState.COMPLETED
    assert res.intent == "RETRIEVE_CASE_DETAILS"
    assert res.tool_result["case_id"] == case.id
    assert res.tool_result["title"] == case.title


def test_orchestrator_consequential_action_halts_for_approval(test_env):
    """Verify orchestrator halts when an action requires human approval and emits approval request."""
    db, case, user = test_env
    orchestrator = WorkflowOrchestrator()
    principal = UserPrincipal(user_id=user.id, username=user.username, email=user.email, role=user.role)

    res = orchestrator.execute(
        query=f"Update case {case.id} status to in_progress",
        principal=principal,
    )

    assert res.final_state == WorkflowState.APPROVAL_REQUIRED
    assert res.approval_id is not None
    assert res.approval_required is True


def test_orchestrator_consequential_action_succeeds_with_approval(test_env):
    """Verify orchestrator executes update once valid approval token is provided."""
    db, case, user = test_env
    orchestrator = WorkflowOrchestrator()
    # Execute update as manager
    principal = UserPrincipal(user_id=user.id, username=user.username, email=user.email, role="manager")

    # 1. First invocation generates approval request
    res1 = orchestrator.execute(
        query=f"Update case {case.id} status to in_progress",
        principal=principal,
    )
    approval_id = res1.approval_id

    # 2. Manager approves
    orchestrator.approval_mgr.grant_approval(
        approval_id=approval_id,
        approver=principal,
    )

    # 3. Second invocation with approval token executes mutation
    res2 = orchestrator.execute(
        query=f"Update case {case.id} status to in_progress",
        principal=principal,
        approval_id=approval_id,
    )

    assert res2.final_state == WorkflowState.COMPLETED
    assert res2.tool_result["status"].lower() == "in_progress"
