"""
Case ORM Model

WHY THIS EXISTS:
    This module defines the database tables as Python classes using SQLAlchemy's
    ORM (Object-Relational Mapping). Instead of writing raw SQL to create tables,
    we define them in Python and SQLAlchemy generates the SQL for us.

    Each class = one database table.
    Each attribute = one column.
    Relationships between classes = foreign keys between tables.

SCHEMA DESIGN DECISIONS:
    - `users` table: Stores case creators and assignees. Separated from cases
      to avoid data duplication (normalization).
    - `cases` table: Core entity. Has foreign keys to users for created_by
      and assigned_to relationships.
    - `case_history` table: Audit trail recording every change to a case.
      This enables CTEs and window functions for curriculum requirements.

    See docs/database-design.md and sql/schema.sql for the full design rationale.

CURRICULUM CONNECTION:
    Week 1 requires: normalized relational schema, foreign keys, relationships.
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database.session import Base


# ── Enums ────────────────────────────────────────────────────────
# Using Python enums ensures only valid values are stored in the database.


class CaseStatus(str, enum.Enum):
    """Valid statuses a case can have."""
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class CasePriority(str, enum.Enum):
    """Priority levels for cases."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CaseType(str, enum.Enum):
    """Classification of the case."""
    BUG = "BUG"
    FEATURE_REQUEST = "FEATURE_REQUEST"
    INQUIRY = "INQUIRY"
    COMPLAINT = "COMPLAINT"


# ── User Model ───────────────────────────────────────────────────


class User(Base):
    """
    Represents a system user (case creator or assignee).

    WHY A SEPARATE TABLE:
        Without this table, we'd store the user's name, email, and role
        directly in the cases table — repeated for every case. That's
        denormalized and leads to update anomalies (change a user's email
        and you must update every case row).
    """
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    username: str = Column(String(50), unique=True, nullable=False, index=True)
    email: str = Column(String(255), unique=True, nullable=False)
    full_name: str = Column(String(255), nullable=False)
    role: str = Column(String(50), nullable=False, default="analyst")
    created_at: datetime = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships (ORM-level only — not extra columns)
    created_cases = relationship(
        "Case", back_populates="creator", foreign_keys="Case.created_by"
    )
    assigned_cases = relationship(
        "Case", back_populates="assignee", foreign_keys="Case.assigned_to"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"


# ── Case Model ───────────────────────────────────────────────────


class Case(Base):
    """
    Core case entity.

    DESIGN:
        - `created_by` and `assigned_to` are foreign keys to users.
        - `status`, `priority`, `case_type` use enums for data integrity.
        - Timestamps use UTC (always store in UTC, convert for display).
    """
    __tablename__ = "cases"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    title: str = Column(String(255), nullable=False)
    description: str = Column(Text, nullable=True)
    status: str = Column(
        Enum(CaseStatus), nullable=False, default=CaseStatus.OPEN
    )
    priority: str = Column(
        Enum(CasePriority), nullable=False, default=CasePriority.MEDIUM
    )
    case_type: str = Column(
        Enum(CaseType), nullable=False, default=CaseType.INQUIRY
    )
    created_by: int = Column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    assigned_to: int = Column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    created_at: datetime = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Column(
        DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    resolved_at: datetime = Column(DateTime, nullable=True)

    # Relationships
    creator = relationship(
        "User", back_populates="created_cases", foreign_keys=[created_by]
    )
    assignee = relationship(
        "User", back_populates="assigned_cases", foreign_keys=[assigned_to]
    )
    history = relationship(
        "CaseHistory", back_populates="case", order_by="CaseHistory.changed_at"
    )

    def __repr__(self) -> str:
        return f"<Case(id={self.id}, title='{self.title}', status='{self.status}')>"


# ── Case History Model ───────────────────────────────────────────


class CaseHistory(Base):
    """
    Audit log for case changes.

    WHY THIS TABLE EXISTS:
        - Provides a full audit trail of every change
        - Enables SQL exercises: CTEs to build change timelines,
          window functions to find the Nth change or time between changes
        - Required by the curriculum for CTE and window function practice
    """
    __tablename__ = "case_history"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    case_id: int = Column(
        Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    changed_by: int = Column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    field_changed: str = Column(String(100), nullable=False)
    old_value: str = Column(Text, nullable=True)
    new_value: str = Column(Text, nullable=False)
    changed_at: datetime = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    case = relationship("Case", back_populates="history")
    user = relationship("User")

    def __repr__(self) -> str:
        return (
            f"<CaseHistory(case_id={self.case_id}, "
            f"field='{self.field_changed}')>"
        )
