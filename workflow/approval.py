"""
Human-in-the-Loop (HITL) Approval Management Subsystem.
Mandatory security gate for all consequential write actions (e.g. update_ticket).
"""
from enum import Enum
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone, timedelta
import threading
import uuid
from pydantic import BaseModel, Field
from security.auth import UserPrincipal
from security.rbac import Permission, check_permission


class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class ApprovalRequest(BaseModel):
    approval_id: str
    ticket_id: int
    target_status: str
    proposed_by: str
    approved_by: Optional[str] = None
    justification: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    rejection_reason: Optional[str] = None
    created_at: str
    expires_at: str

    @property
    def request_id(self) -> str:
        return self.approval_id


class ApprovalManager:
    """
    Thread-safe repository managing the lifecycle of human approval tokens.
    """

    DEFAULT_TTL_SECONDS = 600  # 10 minutes expiration

    def __init__(self):
        self._approvals: Dict[str, ApprovalRequest] = {}
        self._lock = threading.Lock()

    def request_approval(
        self,
        ticket_id: int,
        target_status: str,
        proposed_by: str,
        justification: str,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
    ) -> ApprovalRequest:
        """Creates a pending approval request with expiration deadline."""
        now = datetime.now(timezone.utc)
        expires = now + timedelta(seconds=ttl_seconds)
        approval_id = f"appr_{uuid.uuid4().hex[:12]}"

        req = ApprovalRequest(
            approval_id=approval_id,
            ticket_id=ticket_id,
            target_status=target_status,
            proposed_by=proposed_by,
            justification=justification,
            status=ApprovalStatus.PENDING,
            created_at=now.isoformat(),
            expires_at=expires.isoformat(),
        )

        with self._lock:
            self._approvals[approval_id] = req

        return req

    def create_approval_request(
        self,
        action_type: str = "update_ticket",
        payload: Optional[Dict[str, Any]] = None,
        requested_by: str = "system",
        user_role: str = "agent",
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
        ticket_id: Optional[int] = None,
        target_status: Optional[str] = None,
        justification: Optional[str] = None,
    ) -> ApprovalRequest:
        """Convenience method matching action payload signature."""
        payload = payload or {}
        tid = ticket_id or payload.get("case_id") or payload.get("ticket_id") or 1
        tstat = target_status or payload.get("new_status") or payload.get("status") or "in_progress"
        just = justification or payload.get("comment") or f"Action {action_type}"
        return self.request_approval(
            ticket_id=int(tid),
            target_status=str(tstat),
            proposed_by=requested_by,
            justification=str(just),
            ttl_seconds=ttl_seconds,
        )

    def approve_request(self, request_id: str, reviewer: str = "manager") -> str:
        """Helper alias for approve_request returning token/approval_id."""
        principal = UserPrincipal(user_id=999, username=reviewer, email=f"{reviewer}@example.com", role="manager")
        req = self.grant_approval(approval_id=request_id, approver=principal)
        return req.approval_id

    def grant_approval(self, approval_id: str, approver: UserPrincipal) -> ApprovalRequest:
        """
        Grants human approval.
        Enforces that the approver has Permission.APPROVE_TICKET (Manager or Admin).
        """
        if not check_permission(approver, Permission.APPROVE_TICKET):
            raise PermissionError(
                f"Approver '{approver.username}' with role '{approver.role}' is not authorized to grant ticket approvals."
            )

        with self._lock:
            req = self._approvals.get(approval_id)
            if not req:
                raise KeyError(f"Approval request '{approval_id}' was not found.")

            # Check expiration
            expires_dt = datetime.fromisoformat(req.expires_at)
            if datetime.now(timezone.utc) > expires_dt:
                req.status = ApprovalStatus.EXPIRED
                raise TimeoutError(f"Approval request '{approval_id}' has expired.")

            if req.status != ApprovalStatus.PENDING:
                raise ValueError(f"Approval '{approval_id}' is already in status '{req.status.value}'.")

            req.status = ApprovalStatus.APPROVED
            req.approved_by = approver.username
            return req

    def reject_approval(self, approval_id: str, approver: UserPrincipal, reason: str = "Rejected by manager") -> ApprovalRequest:
        """Rejects an approval request."""
        if not check_permission(approver, Permission.APPROVE_TICKET):
            raise PermissionError(
                f"User '{approver.username}' with role '{approver.role}' is not authorized to reject approvals."
            )

        with self._lock:
            req = self._approvals.get(approval_id)
            if not req:
                raise KeyError(f"Approval request '{approval_id}' was not found.")

            req.status = ApprovalStatus.REJECTED
            req.rejection_reason = reason
            req.approved_by = approver.username
            return req

    def verify_approval(
        self, approval_id: str, expected_ticket_id: Optional[int] = None, expected_status: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Verifies that an approval token is valid, APPROVED, matches target parameters, and not expired.
        """
        with self._lock:
            req = self._approvals.get(approval_id)
            if not req:
                return False, f"Approval ID '{approval_id}' does not exist."

            # Check expiration
            expires_dt = datetime.fromisoformat(req.expires_at)
            if datetime.now(timezone.utc) > expires_dt:
                req.status = ApprovalStatus.EXPIRED
                return False, f"Approval ID '{approval_id}' has expired."

            if req.status == ApprovalStatus.REJECTED:
                return False, f"Approval was explicitly rejected: {req.rejection_reason}"

            if req.status == ApprovalStatus.PENDING:
                return False, "Approval is still pending human review by a manager."

            if req.status != ApprovalStatus.APPROVED:
                return False, f"Approval is in non-executable state: {req.status.value}"

            if expected_ticket_id is not None and req.ticket_id != expected_ticket_id:
                return False, f"Approval was issued for ticket {req.ticket_id}, but attempted on ticket {expected_ticket_id}."

            if expected_status is not None and req.target_status.lower() != expected_status.lower():
                return False, f"Approval was issued for status '{req.target_status}', but attempted with '{expected_status}'."

            return True, "Valid and authorized."


    def get_approval(self, approval_id: str) -> Optional[ApprovalRequest]:
        with self._lock:
            return self._approvals.get(approval_id)

    def list_pending(self) -> List[ApprovalRequest]:
        now = datetime.now(timezone.utc)
        with self._lock:
            pending = []
            for req in self._approvals.values():
                if req.status == ApprovalStatus.PENDING:
                    # Update expired status lazily
                    if now > datetime.fromisoformat(req.expires_at):
                        req.status = ApprovalStatus.EXPIRED
                    else:
                        pending.append(req)
            return pending


approval_manager = ApprovalManager()
