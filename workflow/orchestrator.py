"""
Controlled AI Workflow Orchestrator.
Coordinates state transitions, guardrail checks, routing, tool executions,
human-in-the-loop approvals, retries, timeouts, and fallbacks.
"""
from typing import Dict, Any, Optional, Tuple
import time
import concurrent.futures
from pydantic import BaseModel, Field

from security.auth import UserPrincipal
from security.rbac import Permission, check_permission
from security.guardrails import InputGuardrail, GuardrailViolation
from security.access_aware_retrieval import AccessAwarePolicyFilter
from workflow.state import WorkflowState, WorkflowContext
from workflow.router import WorkflowRouter, WorkflowIntent
from workflow.approval import approval_manager, ApprovalManager
from workflow.fallback import WorkflowFallbackHandler
from tools.retrieve_case import retrieve_case_details
from tools.update_ticket import update_ticket
from tools.schemas import RetrieveCaseInput, UpdateTicketInput, ToolError
from rag.pipeline import RAGPipeline
from rag.schemas import RAGRequest


class WorkflowExecutionResult(BaseModel):
    request_id: str
    correlation_id: str
    initial_state: WorkflowState
    final_state: WorkflowState
    intent: str
    final_response: str
    selected_tool: Optional[str] = None
    tool_result: Optional[Dict[str, Any]] = None
    rag_result: Optional[Dict[str, Any]] = None
    approval_id: Optional[str] = None
    approval_required: bool = False
    execution_time_ms: float
    error: Optional[str] = None
    state_history: list = Field(default_factory=list)


class WorkflowOrchestrator:
    """
    Main orchestrator enforcing the controlled AI workflow.
    """

    def __init__(
        self,
        rag_pipeline: Optional[RAGPipeline] = None,
        approval_mgr: Optional[ApprovalManager] = None,
        max_retries: int = 2,
        tool_timeout_seconds: float = 3.0,
    ):
        self.rag_pipeline = rag_pipeline or RAGPipeline()
        self.approval_mgr = approval_mgr or approval_manager
        self.max_retries = max_retries
        self.tool_timeout_seconds = tool_timeout_seconds

    def execute(
        self,
        query: str,
        principal: UserPrincipal,
        approval_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> WorkflowExecutionResult:
        """
        Executes end-to-end controlled workflow for a user request.
        """
        start_time = time.perf_counter()
        ctx = WorkflowContext(
            username=principal.username,
            user_role=principal.role,
            raw_query=query,
            approval_id=approval_id,
        )
        if correlation_id:
            ctx.correlation_id = correlation_id

        try:
            # 1. Input Safety & Guardrail Check
            sanitized = InputGuardrail.sanitize(query, strict=True)
            cleaned_query = sanitized.cleaned_text

            # 2. State Transition: INTENT_DETECTED
            decision = WorkflowRouter.route(cleaned_query)
            ctx.intent = decision.intent.value
            ctx.selected_tool = decision.tool_name
            ctx.tool_arguments = decision.tool_arguments
            ctx.transition_to(WorkflowState.INTENT_DETECTED, reason=decision.reasoning)

            # 3. Branch: Pure Policy RAG Query
            if decision.intent == WorkflowIntent.RAG_POLICY_QUERY:
                ctx.transition_to(WorkflowState.EXECUTING, reason="Executing access-aware RAG search")
                
                # Check access-aware policy permissions
                rag_req = RAGRequest(
                    question=cleaned_query,
                    retrieval_mode="hybrid",
                    top_k=3,
                    use_reranker=True,
                )
                rag_resp = self.rag_pipeline.answer_question(rag_req)

                # Filter out citations and context user is not authorized to see
                allowed_docs = set(AccessAwarePolicyFilter.get_allowed_document_ids(principal))
                safe_citations = [c for c in rag_resp.citations if c.document_id in allowed_docs]

                if not safe_citations and rag_resp.citations:
                    # User asked about a policy that exists, but their role cannot view it
                    ctx.final_response = WorkflowFallbackHandler.on_unauthorized(
                        user=principal.username,
                        role=principal.role,
                        action="view restricted policy",
                    )
                else:
                    ctx.final_response = rag_resp.answer

                ctx.rag_result = {
                    "is_grounded": rag_resp.is_grounded,
                    "citations": [c.model_dump() for c in safe_citations],
                    "latency_ms": rag_resp.execution_time_ms,
                }
                ctx.transition_to(WorkflowState.COMPLETED, reason="Policy guidance generated")

            # 4. Branch: Read Tool (retrieve_case_details)
            elif decision.intent == WorkflowIntent.RETRIEVE_CASE_DETAILS:
                ctx.transition_to(WorkflowState.TOOL_PROPOSED, reason="Safe read tool proposed")
                ctx.transition_to(WorkflowState.EXECUTING, reason="Dispatching retrieve_case_details")

                tool_out, tool_err = self._execute_tool_with_retry_and_timeout(
                    tool_func=retrieve_case_details,
                    input_data=decision.tool_arguments,
                    principal=principal,
                    tool_name="retrieve_case_details",
                )

                if tool_err:
                    ctx.error = tool_err.error_code
                    ctx.final_response = f"Failed to retrieve case: {tool_err.message}"
                    ctx.transition_to(WorkflowState.FAILED, reason=tool_err.message)
                else:
                    ctx.tool_result = tool_out.model_dump()
                    ctx.final_response = (
                        f"Case #{tool_out.case_id} Details:\n"
                        f"Title: {tool_out.title}\n"
                        f"Status: {tool_out.status.upper()} | Priority: {tool_out.priority.upper()}\n"
                        f"Description: {tool_out.description or 'No description provided.'}"
                    )
                    ctx.transition_to(WorkflowState.COMPLETED, reason="Case retrieved successfully")

            # 5. Branch: Write Tool (update_ticket) - Human Approval Required
            elif decision.intent == WorkflowIntent.UPDATE_TICKET:
                ctx.transition_to(WorkflowState.TOOL_PROPOSED, reason="Consequential write tool proposed")
                ticket_id = decision.tool_arguments.get("ticket_id")
                target_status = decision.tool_arguments.get("status")

                # If no approval_id provided, PAUSE and request Human Approval
                if not approval_id:
                    ctx.transition_to(WorkflowState.APPROVAL_REQUIRED, reason="Write action requires human approval")
                    appr_req = self.approval_mgr.request_approval(
                        ticket_id=ticket_id,
                        target_status=target_status,
                        proposed_by=principal.username,
                        justification=decision.tool_arguments.get("comment", ""),
                    )
                    ctx.approval_id = appr_req.approval_id
                    ctx.approval_status = appr_req.status.value
                    ctx.final_response = WorkflowFallbackHandler.on_approval_required(
                        approval_id=appr_req.approval_id,
                        ticket_id=ticket_id,
                        target_status=target_status,
                    )
                else:
                    # An approval_id was provided - verify it!
                    is_valid, reason = self.approval_mgr.verify_approval(
                        approval_id=approval_id,
                        expected_ticket_id=ticket_id,
                        expected_status=target_status,
                    )
                    if not is_valid:
                        ctx.transition_to(WorkflowState.APPROVAL_REQUIRED, reason=reason)
                        ctx.error = "APPROVAL_INVALID"
                        ctx.final_response = f"Approval check failed: {reason}"
                    else:
                        ctx.transition_to(WorkflowState.APPROVED, reason="Human approval verified")
                        ctx.transition_to(WorkflowState.EXECUTING, reason="Executing update_ticket tool")

                        args_with_appr = dict(decision.tool_arguments)
                        args_with_appr["approval_id"] = approval_id

                        tool_out, tool_err = self._execute_tool_with_retry_and_timeout(
                            tool_func=update_ticket,
                            input_data=args_with_appr,
                            principal=principal,
                            tool_name="update_ticket",
                            extra_kwargs={"approval_verifier": self.approval_mgr},
                        )

                        if tool_err:
                            ctx.error = tool_err.error_code
                            ctx.final_response = f"Update failed: {tool_err.message}"
                            ctx.transition_to(WorkflowState.FAILED, reason=tool_err.message)
                        else:
                            ctx.tool_result = tool_out.model_dump()
                            replay_note = " (Idempotent Replay)" if tool_out.is_idempotent_replay else ""
                            ctx.final_response = (
                                f"Ticket #{tool_out.ticket_id} successfully updated from "
                                f"'{tool_out.previous_status}' to '{tool_out.new_status}'.{replay_note}\n"
                                f"Approved by: {principal.username} (Token: {tool_out.approval_id})\n"
                                f"Audit Event ID: {tool_out.audit_event_id}"
                            )
                            ctx.transition_to(WorkflowState.COMPLETED, reason="Ticket updated successfully")

            # 6. Branch: Combined Case Compliance Check
            elif decision.intent == WorkflowIntent.COMPLIANCE_CASE_CHECK:
                ctx.transition_to(WorkflowState.TOOL_PROPOSED, reason="Fetching case for compliance check")
                ctx.transition_to(WorkflowState.EXECUTING, reason="Reading case details")

                c_out, c_err = retrieve_case_details(decision.tool_arguments, principal)
                if c_err:
                    ctx.final_response = f"Could not verify compliance: {c_err.message}"
                    ctx.transition_to(WorkflowState.FAILED, reason=c_err.message)
                else:
                    ctx.tool_result = c_out.model_dump()
                    # Now formulate policy question
                    compliance_q = (
                        f"Case: {c_out.title}. Description: {c_out.description or c_out.title}. "
                        f"Identify applicable policies and compliance requirements."
                    )
                    rag_req = RAGRequest(question=compliance_q, retrieval_mode="hybrid", top_k=3)
                    rag_resp = self.rag_pipeline.answer_question(rag_req)
                    ctx.rag_result = {"is_grounded": rag_resp.is_grounded, "citations": [c.model_dump() for c in rag_resp.citations]}
                    ctx.final_response = (
                        f"Compliance Assessment for Case #{c_out.case_id} ({c_out.title}):\n\n"
                        f"{rag_resp.answer}"
                    )
                    ctx.transition_to(WorkflowState.COMPLETED, reason="Compliance assessment completed")

        except GuardrailViolation as gv:
            ctx.error = "GUARDRAIL_VIOLATION"
            ctx.final_response = f"Security Violation: {gv.detail.get('reason')}"
            if ctx.current_state != WorkflowState.FAILED:
                ctx.transition_to(WorkflowState.FAILED, reason=gv.detail.get("reason"))

        except Exception as ex:
            ctx.error = str(ex)
            ctx.final_response = f"Workflow encountered an unexpected error: {str(ex)}"
            if ctx.current_state != WorkflowState.FAILED:
                ctx.transition_to(WorkflowState.FAILED, reason=str(ex))

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return WorkflowExecutionResult(
            request_id=ctx.request_id,
            correlation_id=ctx.correlation_id,
            initial_state=WorkflowState.REQUEST_RECEIVED,
            final_state=ctx.current_state,
            intent=ctx.intent or "UNKNOWN",
            final_response=ctx.final_response or "No response generated.",
            selected_tool=ctx.selected_tool,
            tool_result=ctx.tool_result,
            rag_result=ctx.rag_result,
            approval_id=ctx.approval_id,
            approval_required=(ctx.current_state == WorkflowState.APPROVAL_REQUIRED),
            execution_time_ms=round(elapsed_ms, 2),
            error=ctx.error,
            state_history=ctx.state_history,
        )

    def _execute_tool_with_retry_and_timeout(
        self,
        tool_func: Any,
        input_data: Dict[str, Any],
        principal: UserPrincipal,
        tool_name: str,
        extra_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Optional[Any], Optional[ToolError]]:
        """
        Executes a tool with timeout monitoring and exponential backoff on retryable errors.
        """
        kwargs = {"input_data": input_data, "principal": principal}
        if extra_kwargs:
            kwargs.update(extra_kwargs)

        attempts = 0
        backoff = 0.1

        while attempts <= self.max_retries:
            attempts += 1
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(tool_func, **kwargs)
                    output, err = future.result(timeout=self.tool_timeout_seconds)

                if err is not None:
                    if err.retryable and attempts <= self.max_retries:
                        time.sleep(backoff)
                        backoff *= 2.0
                        continue
                    return None, err

                return output, None

            except concurrent.futures.TimeoutError:
                if attempts <= self.max_retries:
                    time.sleep(backoff)
                    backoff *= 2.0
                    continue
                return None, ToolError(
                    error_code="TIMEOUT",
                    message=f"Tool '{tool_name}' timed out after {self.tool_timeout_seconds}s.",
                    retryable=False,
                )
            except Exception as ex:
                return None, ToolError(
                    error_code="TOOL_EXCEPTION",
                    message=f"Unhandled tool error: {str(ex)}",
                    retryable=False,
                )

        return None, ToolError(
            error_code="RETRY_EXHAUSTED",
            message=f"Tool '{tool_name}' exhausted {self.max_retries} retries.",
            retryable=False,
        )


workflow_orchestrator = WorkflowOrchestrator()
