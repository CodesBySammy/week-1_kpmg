"""
Case Service — Business Logic Layer

WHY THIS EXISTS:
    The service layer contains business rules and orchestration:
      - Validating that referenced users exist before creating a case
      - Applying business rules (e.g., can't reopen a CLOSED case)
      - Coordinating between repositories
      - Transforming data between schemas and models

    The route handler is THIN (receives request, calls service, returns response).
    The service is where the real logic lives.

SEPARATION EXAMPLE:
    Route handler:  "receive HTTP request, return HTTP response"
    Service:        "validate business rules, coordinate data operations"
    Repository:     "execute database queries"

    This means you can test business logic WITHOUT an HTTP server,
    and test database queries WITHOUT business rules.

CURRICULUM CONNECTION:
    Week 1 requires: modular Python code, separation of concerns, classes.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.exceptions import CaseNotFoundError, UserNotFoundError, ValidationError
from app.models.case import Case, CaseStatus, EscalationTier
from app.repositories.case_repository import CaseRepository, UserRepository
from app.schemas.case import CaseCreate, CaseUpdate

logger = logging.getLogger(__name__)


class CaseService:
    """
    Business logic for case management operations.

    Orchestrates validation, data access, and business rules.
    """

    def __init__(self) -> None:
        self.case_repo = CaseRepository()
        self.user_repo = UserRepository()

    def create_case(self, db: Session, case_data: CaseCreate) -> Case:
        """
        Create a new case after validating business rules.

        Business rules:
          1. The creator (created_by) must be an existing user
          2. If assigned_to is provided, that user must also exist
        """
        logger.info(
            "Creating new case",
            extra={
                "title": case_data.title,
                "created_by": case_data.created_by,
                "operation": "create_case",
            },
        )

        # Validate: creator must exist
        self.user_repo.get_by_id(db, case_data.created_by)

        # Validate: assignee must exist (if provided)
        if case_data.assigned_to is not None:
            self.user_repo.get_by_id(db, case_data.assigned_to)

        # Convert Pydantic schema → SQLAlchemy model
        case = Case(
            title=case_data.title,
            description=case_data.description,
            priority=case_data.priority,
            case_type=case_data.case_type,
            escalation_tier=case_data.escalation_tier or EscalationTier.STANDARD,
            department=case_data.department or "SUPPORT",
            created_by=case_data.created_by,
            assigned_to=case_data.assigned_to,
            status=CaseStatus.OPEN,
        )

        created_case = self.case_repo.create(db, case)
        logger.info(
            "Case created successfully",
            extra={
                "case_id": created_case.id,
                "status": created_case.status,
                "operation": "create_case",
            },
        )
        return created_case

    def get_case(self, db: Session, case_id: int) -> Case:
        """
        Retrieve a case by ID.

        Raises CaseNotFoundError if the case doesn't exist.
        """
        logger.debug(
            "Retrieving case",
            extra={"case_id": case_id, "operation": "get_case"},
        )
        return self.case_repo.get_by_id(db, case_id)

    def list_cases(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> tuple[list[Case], int]:
        """
        List cases with optional filtering and pagination.
        """
        logger.debug(
            "Listing cases",
            extra={
                "skip": skip,
                "limit": limit,
                "status_filter": status,
                "priority_filter": priority,
                "operation": "list_cases",
            },
        )
        return self.case_repo.get_all(
            db, skip=skip, limit=limit, status=status, priority=priority
        )

    def update_case(
        self, db: Session, case_id: int, case_data: CaseUpdate
    ) -> Case:
        """
        Update an existing case.

        Business rules:
          1. Case must exist
          2. If assigning to a user, that user must exist
          3. If resolving, set resolved_at timestamp
          4. Cannot reopen a CLOSED case
        """
        logger.info(
            "Updating case",
            extra={"case_id": case_id, "operation": "update_case"},
        )

        # Get existing case (raises CaseNotFoundError if missing)
        case = self.case_repo.get_by_id(db, case_id)

        # Build updates dict from non-None fields
        updates = case_data.model_dump(exclude_unset=True)

        if not updates:
            raise ValidationError("No fields to update were provided")

        # Business rule: validate assignee exists
        if "assigned_to" in updates and updates["assigned_to"] is not None:
            self.user_repo.get_by_id(db, updates["assigned_to"])

        # Business rule: can't reopen a CLOSED case
        if "status" in updates and case.status == CaseStatus.CLOSED:
            raise ValidationError(
                "Cannot change the status of a CLOSED case"
            )

        # Business rule: set resolved_at when resolving
        if (
            "status" in updates
            and updates["status"] == CaseStatus.RESOLVED
            and case.status != CaseStatus.RESOLVED
        ):
            updates["resolved_at"] = datetime.now(timezone.utc)

        updated_case = self.case_repo.update(db, case, updates)
        logger.info(
            "Case updated successfully",
            extra={
                "case_id": case_id,
                "updated_fields": list(updates.keys()),
                "operation": "update_case",
            },
        )
        return updated_case
