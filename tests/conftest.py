"""
Test Configuration (conftest.py)

WHY THIS EXISTS:
    conftest.py is a special pytest file that provides SHARED test fixtures.
    Any fixture defined here is automatically available to ALL test files
    in this directory and its subdirectories — no imports needed.

WHAT IS A FIXTURE:
    A fixture is a reusable piece of test setup. Instead of repeating
    "create a test database and client" in every test function, you
    define it once as a fixture and pytest injects it automatically.

KEY FIXTURES HERE:
    - db_session: A fresh database session for each test (isolated)
    - client: A FastAPI test client that uses the test database
    - sample_user: A pre-created user (many tests need one)
    - sample_case: A pre-created case (for update/retrieve tests)

WHY EACH TEST GETS ITS OWN DATABASE:
    Tests must be independent. If test A creates data and test B
    reads it, test B depends on test A running first — fragile.
    Each test gets a fresh in-memory SQLite database so tests
    never interfere with each other.

CURRICULUM CONNECTION:
    Week 1 requires: pytest fixtures, test isolation, automated tests.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.database.session import Base, get_db
from app.main import app
from app.models.case import User, Case, CaseStatus, CasePriority, CaseType


# ── Test Database Engine ─────────────────────────────────────────
# Use an in-memory SQLite database for tests (fast, disposable).
TEST_DATABASE_URL = "sqlite:///./test_case_management.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Enable foreign keys for SQLite in tests too
@event.listens_for(test_engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)


# ── Fixtures ─────────────────────────────────────────────────────


@pytest.fixture(scope="function")
def db_session():
    """
    Provide a clean database session for each test.

    - Creates all tables before the test
    - Yields a session
    - Drops all tables after the test (clean slate for next test)

    scope="function" means this runs for EVERY test function (isolation).
    """
    Base.metadata.create_all(bind=test_engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Provide a FastAPI test client that uses the test database.

    HOW IT WORKS:
        We override FastAPI's `get_db` dependency to return our test
        session instead of the production session. This is dependency
        injection — the route code doesn't change, but the database
        it talks to is different.

    WHY TestClient:
        TestClient makes HTTP requests WITHOUT starting a real server.
        It's fast and runs in the same process as the tests.
    """

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def sample_user(db_session) -> User:
    """
    Create and return a sample user for tests that need one.

    Many tests need a user to exist (e.g., creating a case requires
    a valid created_by ID). This fixture avoids repeating user
    creation code in every test.
    """
    user = User(
        username="testuser",
        email="testuser@example.com",
        full_name="Test User",
        role="analyst",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def second_user(db_session) -> User:
    """A second user for assignment/transfer tests."""
    user = User(
        username="assignee",
        email="assignee@example.com",
        full_name="Test Assignee",
        role="senior_analyst",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def sample_case(db_session, sample_user) -> Case:
    """
    Create and return a sample case for update/retrieve tests.

    Depends on sample_user fixture (pytest resolves this automatically).
    """
    case = Case(
        title="Test Case",
        description="A test case for unit testing",
        status=CaseStatus.OPEN,
        priority=CasePriority.MEDIUM,
        case_type=CaseType.BUG,
        created_by=sample_user.id,
    )
    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)
    return case
