"""
Database Session Management

WHY THIS EXISTS:
    Every database operation needs a "session" — a connection that tracks
    changes and commits them as a unit (transaction). This module:
      1. Creates the SQLAlchemy Engine (the connection pool)
      2. Creates a Session factory
      3. Provides a dependency (get_db) that FastAPI injects into routes

HOW IT WORKS:
    SQLAlchemy uses two core objects:
      - Engine: manages database connections (like a pool of phone lines)
      - Session: one conversation over one phone line — tracks changes
        and commits/rolls back as a unit

    The `get_db` generator function:
      1. Opens a session
      2. Yields it to the route handler
      3. Closes it when the request is done (even if an error occurred)

    This is called "dependency injection" — the route handler declares
    "I need a database session" and FastAPI provides one automatically.

CURRICULUM CONNECTION:
    Week 1 requires: database persistence, transactions, configuration-driven
    connection strings (not hardcoded).
"""

from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.

    WHY:
        SQLAlchemy needs a common base class to discover all models
        and create their tables. Every model inherits from this.
    """
    pass


def _create_engine():
    """Create the SQLAlchemy engine from configuration."""
    settings = get_settings()
    connect_args = {}

    # SQLite-specific: allow multi-threaded access
    if settings.database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    engine = create_engine(
        settings.database_url,
        connect_args=connect_args,
        echo=False,  # Set True to see SQL in logs (noisy)
    )

    # SQLite: enable foreign key enforcement (OFF by default!)
    if settings.database_url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


# ── Module-level engine and session factory ──────────────────────
engine = _create_engine()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.

    Usage in a route:
        @router.post("/cases")
        def create_case(db: Session = Depends(get_db)):
            ...

    The session is automatically closed after the request completes.
    If an exception occurs, the session is still closed (no leaked connections).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """
    Create all tables defined by ORM models.

    This reads every class that inherits from Base and creates
    the corresponding table if it doesn't exist yet.
    Also ensures backward-compatible column migration for SQLite.
    """
    Base.metadata.create_all(bind=engine)
    try:
        with engine.connect() as conn:
            cursor = conn.exec_driver_sql("PRAGMA table_info(cases)")
            cols = [row[1] for row in cursor.fetchall()]
            if cols and "escalation_tier" not in cols:
                conn.exec_driver_sql(
                    "ALTER TABLE cases ADD COLUMN escalation_tier VARCHAR(32) DEFAULT 'STANDARD'"
                )
            if cols and "department" not in cols:
                conn.exec_driver_sql(
                    "ALTER TABLE cases ADD COLUMN department VARCHAR(64) DEFAULT 'SUPPORT'"
                )
            conn.commit()
    except Exception:
        pass
