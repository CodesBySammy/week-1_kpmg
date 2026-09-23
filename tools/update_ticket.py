"""
TOOL 2: update_ticket (Consequential Write Operation).
Requires mandatory human approval, enforces role authorization, and guarantees idempotency.
"""
from typing import Union, Dict, Any, Tuple, Optional
from datetime import datetime, timezone
import uuid
import threading
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.database.session import SessionLocal
from app.exceptions import CaseNotFoundError
from app.repositories.case_repository import CaseRepository
from app.schemas.case import CaseUpdate
from app.models.case import CaseStatus
from security.auth import UserPrincipal
from security.rbac import Permission, check_permission
from tools.schemas import UpdateTicketInput, UpdateTicketOutput, ToolError


class IdempotencyStore:
    """Thread-safe in-memory cache for idempotent write replays."""

    def __init__(self):
        self._cache: Dict[str, UpdateTicketOutput] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[UpdateTicketOutput]:
        with self._lock:
            return self._cache.get(key)

    def set(self, key: str, output: UpdateTicketOutput):
        with self._lock:
            self._cache[key] = output

    def clear(self):
        with self._lock:
            self._cache.clear()


idempotency_store = IdempotencyStore()


def update_ticket(
    input_data: Union[UpdateTicketInput, Dict[str, Any]],
    principal: UserPrincipal,
    approval_verifier: Any = None,  # Workflow ApprovalManager
    db: Session = None,
) -> Tuple[Optional[UpdateTicketOutput], Optional[ToolError]]:
    """
    Executes TOOL 2: update_ticket.
    Consequential write operation requiring Human Approval, Authorization, and Idempotency.
    Returns: (output, error). Exactly one of the two will be non-None.
    """
    # 1. Authorize operation
    if not check_permission(principal, Permission.EXECUTE_TICKET_UPDATE):
        return None, ToolError(
            error_code="UNAUTHORIZED",
            message=f"User '{principal.username}' with role '{principal.role}' lacks permission to execute ticket updates.",
            details={"required_permission": Permission.EXECUTE_TICKET_UPDATE.value},
            retryable=False,
        )

    # 2. Validate input schema
    if isinstance(input_data, dict):
        try:
            params = UpdateTicketInput(**input_data)
        except ValidationError as e:
            return None, ToolError(
                error_code="VALIDATION_ERROR",
                message="Tool input arguments failed schema validation.",
                details={"errors": e.errors()},
                retryable=False,
            )
    else:
        params = input_data

    # 3. Check Idempotency Key
    idempotency_key = params.idempotency_key or (f"approval:{params.approval_id}" if params.approval_id else None)
    if idempotency_key:
        cached_replay = idempotency_store.get(idempotency_key)
        if cached_replay is not None:
            # Replay cached outcome safely without duplicating database mutation
            replay_copy = cached_replay.model_copy()
            replay_copy.is_idempotent_replay = True
            return replay_copy, None

    # 4. Mandatory Human Approval Verification
    if not params.approval_id:
        return None, ToolError(
            error_code="APPROVAL_REQUIRED",
            message="Human approval token is required before executing ticket update.",
            details={"ticket_id": params.ticket_id},
            retryable=False,
        )

    if approval_verifier is None:
        from workflow.approval import approval_manager
        approval_verifier = approval_manager

    is_approved, reason = approval_verifier.verify_approval(
        approval_id=params.approval_id,
        expected_ticket_id=params.ticket_id,
        expected_status=params.status,
    )
    if not is_approved:
        return None, ToolError(
            error_code="INVALID_APPROVAL",
            message=f"Ticket write action rejected: {reason}",
            details={"approval_id": params.approval_id, "reason": reason},
            retryable=False,
        )

    # 5. Execute Relational Database Mutation
    own_session = False
    if db is None:
        db = SessionLocal()
        own_session = True

    try:
        repo = CaseRepository()
        try:
            case_entity = repo.get_by_id(db, params.ticket_id)
        except CaseNotFoundError:
            return None, ToolError(
                error_code="TICKET_NOT_FOUND",
                message=f"Target ticket ID {params.ticket_id} does not exist in database.",
                details={"ticket_id": params.ticket_id},
                retryable=False,
            )

        prev_status = case_entity.status.value if hasattr(case_entity.status, "value") else str(case_entity.status)
        
        # Target CaseStatus enum
        try:
            target_status_enum = CaseStatus(params.status.upper())
        except ValueError:
            try:
                target_status_enum = CaseStatus(params.status.lower())
            except ValueError:
                return None, ToolError(
                    error_code="INVALID_STATUS",
                    message=f"Invalid target status '{params.status}'.",
                    retryable=False,
                )

        # Update case entity with audit comment
        updates = {"status": target_status_enum}
        if params.comment:
            existing_desc = case_entity.description or ""
            updates["description"] = f"{existing_desc}\n[Update Note ({datetime.now(timezone.utc).isoformat()} by {principal.username})]: {params.comment}".strip()
        
        updated_entity = repo.update(db, case_entity, updates)

        event_id = f"evt_{uuid.uuid4().hex[:12]}"
        now_iso = datetime.now(timezone.utc).isoformat()

        output = UpdateTicketOutput(
            ticket_id=updated_entity.id,
            previous_status=prev_status,
            new_status=updated_entity.status.value if hasattr(updated_entity.status, "value") else str(updated_entity.status),
            comment=params.comment,
            approval_id=params.approval_id,
            updated_by=principal.username,
            updated_at=now_iso,
            is_idempotent_replay=False,
            audit_event_id=event_id,
        )

        # Store in idempotency cache
        if idempotency_key:
            idempotency_store.set(idempotency_key, output)

        return output, None
    finally:
        if own_session:
            db.close()

