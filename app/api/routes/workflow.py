"""
REST API Routes for Controlled AI Workflows.
Exposes endpoints for workflow execution, human approval management, and metrics.
"""
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field

from security.auth import UserPrincipal, get_current_user, create_access_token
from security.rbac import Permission, check_permission
from workflow.orchestrator import workflow_orchestrator, WorkflowExecutionResult
from workflow.approval import approval_manager, ApprovalRequest
from observability.correlation import get_correlation_id
from observability.events import event_logger, EventType
from observability.tracer import trace_collector
from observability.metrics import metrics_collector

router = APIRouter(prefix="/workflow", tags=["Controlled AI Workflow"])


class WorkflowExecuteRequest(BaseModel):
    query: Optional[str] = Field(default=None, description="User prompt or workflow request")
    prompt: Optional[str] = Field(default=None, description="Alias for user prompt")
    approval_id: Optional[str] = Field(default=None, description="Approved approval ID for write execution")
    approval_token: Optional[str] = Field(default=None, description="Alias for approval_id")

    def get_query(self) -> str:
        return self.query or self.prompt or ""

    def get_approval_id(self) -> Optional[str]:
        return self.approval_id or self.approval_token


class ApprovalActionRequest(BaseModel):
    reason: Optional[str] = Field(default="Approved by authorized reviewer", description="Reviewer comments or justification")


class TokenRequest(BaseModel):
    user_id: int = 1
    username: str = "test_user"
    email: str = "test@company.internal"
    role: str = "agent"
    department: str = "Operations"


@router.post("/execute", response_model=WorkflowExecutionResult, summary="Execute Controlled AI Workflow")
def execute_workflow(
    request: WorkflowExecuteRequest,
    principal: UserPrincipal = Depends(get_current_user),
    correlation_id: str = Depends(get_correlation_id),
):
    """
    Executes controlled AI workflow with guardrail verification, intent routing,
    approval gating, tool execution, and observability tracing.
    """
    query_text = request.get_query()
    if not query_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request must contain 'query' or 'prompt'.",
        )

    metrics_collector.increment_request_count()
    event_logger.record(
        event_type=EventType.REQUEST_RECEIVED,
        correlation_id=correlation_id,
        username=principal.username,
        payload={"query": query_text, "role": principal.role},
    )

    with trace_collector.trace(trace_id=correlation_id, name="workflow_request", tags={"role": principal.role}):
        result = workflow_orchestrator.execute(
            query=query_text,
            principal=principal,
            approval_id=request.get_approval_id(),
            correlation_id=correlation_id,
        )

    metrics_collector.record_latency("workflow_total", result.execution_time_ms)
    if result.error:
        metrics_collector.record_error("workflow_failures")
        event_logger.record(
            event_type=EventType.WORKFLOW_FAILED,
            correlation_id=correlation_id,
            request_id=result.request_id,
            username=principal.username,
            payload={"error": result.error},
        )
    else:
        event_logger.record(
            event_type=EventType.WORKFLOW_COMPLETED,
            correlation_id=correlation_id,
            request_id=result.request_id,
            username=principal.username,
            payload={"final_state": result.final_state.value},
        )

    return result


@router.get("/approvals", summary="List Pending Approval Requests")
def list_pending_approvals(
    principal: UserPrincipal = Depends(get_current_user),
):
    """Returns all pending human approval requests awaiting manager review."""
    pending = approval_manager.list_pending()
    return {"approvals": [p.model_dump() for p in pending]}


@router.post("/approval/{approval_id}/approve", summary="Grant Human Approval")
def grant_approval(
    approval_id: str,
    action: ApprovalActionRequest = ApprovalActionRequest(),
    principal: UserPrincipal = Depends(get_current_user),
    correlation_id: str = Depends(get_correlation_id),
):
    """
    Manager endpoint to formally approve a consequential action.
    Requires Permission.APPROVE_TICKET (role: manager or admin).
    """
    try:
        req = approval_manager.grant_approval(approval_id=approval_id, approver=principal)
        event_logger.record(
            event_type=EventType.APPROVAL_GRANTED,
            correlation_id=correlation_id,
            username=principal.username,
            payload={"approval_id": approval_id, "ticket_id": req.ticket_id},
        )
        data = req.model_dump()
        data["approval_token"] = req.approval_id
        return data
    except PermissionError as pe:
        metrics_collector.record_error("authorization_failures")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
    except (KeyError, ValueError, TimeoutError) as ex:
        metrics_collector.record_error("approval_rejections")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex))


@router.post("/approval/{approval_id}/reject", summary="Reject Approval Request")
def reject_approval(
    approval_id: str,
    action: ApprovalActionRequest = ApprovalActionRequest(reason="Rejected by manager review"),
    principal: UserPrincipal = Depends(get_current_user),
    correlation_id: str = Depends(get_correlation_id),
):
    """Rejects a pending approval request."""
    try:
        req = approval_manager.reject_approval(
            approval_id=approval_id, approver=principal, reason=action.reason
        )
        event_logger.record(
            event_type=EventType.APPROVAL_REJECTED,
            correlation_id=correlation_id,
            username=principal.username,
            payload={"approval_id": approval_id, "reason": action.reason},
        )
        metrics_collector.record_error("approval_rejections")
        return req
    except PermissionError as pe:
        metrics_collector.record_error("authorization_failures")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
    except KeyError as ke:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ke))


@router.get("/metrics", summary="Get Operational Telemetry Metrics")
def get_metrics():
    """Returns real-time telemetry metrics: latencies, token counts, and error rates."""
    return metrics_collector.get_summary()


@router.post("/auth/token", summary="Generate JWT Bearer Token for Development/Testing")
def generate_dev_token(
    request: TokenRequest,
):
    """Utility endpoint to generate signed bearer tokens for testing roles."""
    token = create_access_token(
        user_id=request.user_id,
        username=request.username,
        email=request.email,
        role=request.role,
        department=request.department,
    )
    return {
        "access_token": token,
        "token_type": "Bearer",
        "role": request.role,
        "username": request.username,
    }
