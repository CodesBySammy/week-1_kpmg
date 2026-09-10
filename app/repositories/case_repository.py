"""
Case Repository — Data Access Layer

WHY THIS EXISTS (Repository Pattern):
    The repository isolates all database operations in one place.
    The service layer calls repository methods instead of writing SQL/ORM
    queries directly. Benefits:
      1. If you switch databases, only this file changes
      2. Database queries are testable in isolation
      3. The service layer stays focused on business logic
      4. SQL/ORM complexity is contained

DEPENDENCY DIRECTION:
    Routes → Services → Repositories → Database
    
    Each layer only knows about the one directly below it.
    Routes never touch the database. The database never knows about routes.

CURRICULUM CONNECTION:
    Week 1 requires: modular code, separation of concerns, database persistence.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.exceptions import CaseNotFoundError, DatabaseError, UserNotFoundError
from app.models.case import Case, CaseHistory, User

logger = logging.getLogger(__name__)


class CaseRepository:
    """
    Data access methods for Case entities.

    Every method takes a `db` session parameter — the session is managed
    by the caller (service or FastAPI dependency), not by the repository.
    """

    def create(self, db: Session, case: Case) -> Case:
        """
        Insert a new case into the database.

        Raises DatabaseError if the insert fails.
        """
        try:
            db.add(case)
            db.commit()
            db.refresh(case)  # Reload to get auto-generated fields (id, timestamps)
            logger.info(
                "Case created in database",
                extra={"case_id": case.id, "operation": "create"},
            )
            return case
        except Exception as e:
            db.rollback()
            logger.error(
                "Failed to create case",
                extra={"error": str(e), "operation": "create"},
            )
            raise DatabaseError(f"Failed to create case: {e}") from e

    def get_by_id(self, db: Session, case_id: int) -> Case:
        """
        Retrieve a single case by ID.

        Raises CaseNotFoundError if no case with that ID exists.
        """
        case = db.query(Case).filter(Case.id == case_id).first()
        if case is None:
            raise CaseNotFoundError(case_id)
        return case

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> tuple[list[Case], int]:
        """
        Retrieve a paginated list of cases with optional filters.

        Returns (list_of_cases, total_count).
        """
        query = db.query(Case)

        if status:
            query = query.filter(Case.status == status)
        if priority:
            query = query.filter(Case.priority == priority)

        total = query.count()
        cases = query.order_by(Case.created_at.desc()).offset(skip).limit(limit).all()
        return cases, total

    def update(self, db: Session, case: Case, updates: dict) -> Case:
        """
        Update case fields and record changes in history.

        Only updates fields that are explicitly provided (not None).
        Records each change in case_history for audit trail.
        """
        try:
            for field, new_value in updates.items():
                old_value = getattr(case, field, None)
                if old_value != new_value:
                    setattr(case, field, new_value)

                    # Record the change in history
                    history = CaseHistory(
                        case_id=case.id,
                        changed_by=case.created_by,  # Simplified; real app would use current user
                        field_changed=field,
                        old_value=str(old_value) if old_value is not None else None,
                        new_value=str(new_value),
                    )
                    db.add(history)

            case.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(case)
            logger.info(
                "Case updated in database",
                extra={
                    "case_id": case.id,
                    "fields_updated": list(updates.keys()),
                    "operation": "update",
                },
            )
            return case
        except Exception as e:
            db.rollback()
            logger.error(
                "Failed to update case",
                extra={"case_id": case.id, "error": str(e), "operation": "update"},
            )
            raise DatabaseError(f"Failed to update case: {e}") from e


class UserRepository:
    """Data access methods for User entities."""

    def create(self, db: Session, user: User) -> User:
        """Insert a new user."""
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(
                "User created in database",
                extra={"user_id": user.id, "operation": "create_user"},
            )
            return user
        except Exception as e:
            db.rollback()
            logger.error(
                "Failed to create user",
                extra={"error": str(e), "operation": "create_user"},
            )
            raise DatabaseError(f"Failed to create user: {e}") from e

    def get_by_id(self, db: Session, user_id: int) -> User:
        """Retrieve a user by ID. Raises UserNotFoundError if missing."""
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise UserNotFoundError(user_id)
        return user

    def get_all(self, db: Session) -> list[User]:
        """Retrieve all users."""
        return db.query(User).all()
