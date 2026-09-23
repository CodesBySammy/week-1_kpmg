"""
TOOL 1: retrieve_case_details.
Safe, read-only tool to fetch case metadata from the relational database.
"""
from typing import Union, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.database.session import SessionLocal
from app.exceptions import CaseNotFoundError
from app.repositories.case_repository import CaseRepository
from security.auth import UserPrincipal
from security.rbac import Permission, check_permission
from tools.schemas import RetrieveCaseInput, RetrieveCaseOutput, ToolError


def retrieve_case_details(
    input_data: Union[RetrieveCaseInput, Dict[str, Any]],
    principal: UserPrincipal,
    db: Session = None,
) -> Tuple[Optional[RetrieveCaseOutput], Optional[ToolError]]:
    """
    Executes TOOL 1: retrieve_case_details.
    Returns: (output, error). Exactly one of the two will be non-None.
    """
    # 1. Authorize operation
    if not check_permission(principal, Permission.READ_CASE):
        return None, ToolError(
            error_code="UNAUTHORIZED",
            message=f"User '{principal.username}' with role '{principal.role}' is not authorized to read cases.",
            details={"required_permission": Permission.READ_CASE.value},
            retryable=False,
        )

    # 2. Validate input schema
    if isinstance(input_data, dict):
        try:
            params = RetrieveCaseInput(**input_data)
        except ValidationError as e:
            return None, ToolError(
                error_code="INVALID_CASE_ID",
                message="Case ID failed validation.",
                details={"errors": e.errors()},
                retryable=False,
            )
    else:
        params = input_data

    # 3. Query Database
    own_session = False
    if db is None:
        db = SessionLocal()
        own_session = True

    try:
        repo = CaseRepository()
        try:
            case_entity = repo.get_by_id(db, params.case_id)
        except CaseNotFoundError:
            return None, ToolError(
                error_code="CASE_NOT_FOUND",
                message=f"Case with ID {params.case_id} was not found in the database.",
                details={"case_id": params.case_id},
                retryable=False,
            )

        case_type_val = "INQUIRY"
        if hasattr(case_entity, "case_type") and case_entity.case_type is not None:
            case_type_val = case_entity.case_type.value if hasattr(case_entity.case_type, "value") else str(case_entity.case_type)

        output = RetrieveCaseOutput(
            case_id=case_entity.id,
            title=case_entity.title,
            description=case_entity.description,
            status=case_entity.status.value if hasattr(case_entity.status, "value") else str(case_entity.status),
            priority=case_entity.priority.value if hasattr(case_entity.priority, "value") else str(case_entity.priority),
            case_type=case_type_val,
            created_by=case_entity.created_by,
            assigned_to=case_entity.assigned_to,
            created_at=case_entity.created_at.isoformat() if hasattr(case_entity.created_at, "isoformat") else str(case_entity.created_at),
            resolved_at=case_entity.resolved_at.isoformat() if case_entity.resolved_at and hasattr(case_entity.resolved_at, "isoformat") else None,
            audit_notes="Retrieved via authorized AI read tool",
        )
        return output, None
    finally:
        if own_session:
            db.close()

