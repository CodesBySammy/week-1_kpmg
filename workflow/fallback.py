"""
Safe Fallback Responses for Workflow Failures and Timeouts.
Guarantees consistent, helpful, and non-hallucinated outcomes when errors occur.
"""
from typing import Dict, Any


class WorkflowFallbackHandler:
    """Provides graceful fallback responses when tools, RAG, or models fail."""

    @staticmethod
    def on_timeout(tool_name: str, timeout_seconds: float) -> str:
        return (
            f"The operation '{tool_name}' timed out after {timeout_seconds:.1f} seconds. "
            f"Please verify network availability or try again shortly."
        )

    @staticmethod
    def on_unauthorized(user: str, role: str, action: str) -> str:
        return (
            f"Action blocked: User '{user}' with role '{role}' is not authorized "
            f"to perform '{action}'. Please contact your system administrator if access is required."
        )

    @staticmethod
    def on_rag_failure(reason: str) -> str:
        return (
            f"I was unable to retrieve official policy guidance at this time ({reason}). "
            f"Please refer directly to the Policy Portal or contact Human Resources."
        )

    @staticmethod
    def on_approval_required(approval_id: str, ticket_id: int, target_status: str) -> str:
        return (
            f"APPROVAL REQUIRED: Proposed update to ticket #{ticket_id} (status -> '{target_status}') "
            f"requires formal human approval before execution.\n"
            f"Approval Request ID: [{approval_id}]. A notification has been dispatched to authorized managers."
        )

    @staticmethod
    def on_retry_exhausted(tool_name: str, attempts: int, last_error: str) -> str:
        return (
            f"Operation '{tool_name}' failed after {attempts} retry attempts. "
            f"Final diagnostic error: {last_error}. An incident report has been logged."
        )
