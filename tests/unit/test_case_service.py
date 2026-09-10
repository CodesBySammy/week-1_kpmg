"""
Unit Tests for CaseService

WHY UNIT TESTS:
    Unit tests isolate the business logic layer from external dependencies
    (like a live database or an HTTP server).
    Here we test:
      - Valid case creation flow
      - Validation rules (creator must exist, assignee must exist)
      - Status transition rules (e.g. cannot reopen a CLOSED case)
      - Setting resolved_at when changing status to RESOLVED
      - Error raising for missing entities

WHY AND WHEN WE USE MOCKS HERE:
    In these unit tests, we want to verify the SERVICE layer's decision-making
    logic in pure isolation. By mocking the UserRepository and CaseRepository,
    we can test how CaseService handles various scenarios (e.g., user not found,
    database errors, repository return values) without needing to populate or
    execute database queries.
    Mocks verify the contract between Service and Repository.
"""

from unittest.mock import MagicMock
import pytest

from app.exceptions import CaseNotFoundError, UserNotFoundError, ValidationError
from app.models.case import Case, CasePriority, CaseStatus, CaseType, User
from app.schemas.case import CaseCreate, CaseUpdate
from app.services.case_service import CaseService


class TestCaseServiceUnit:
    """Unit tests for CaseService logic using mocks."""

    def test_create_case_success(self):
        """
        Verify that create_case verifies creator existence,
        creates the Case model with default OPEN status, and calls repository create.
        """
        # Arrange
        service = CaseService()
        mock_db = MagicMock()

        mock_user = User(id=1, username="testuser", email="test@example.com", full_name="Test")
        service.user_repo.get_by_id = MagicMock(return_value=mock_user)

        expected_case = Case(
            id=10,
            title="Database Connection Timeout",
            description="Intermittent timeouts under load",
            status=CaseStatus.OPEN,
            priority=CasePriority.HIGH,
            case_type=CaseType.BUG,
            created_by=1,
            assigned_to=None,
        )
        service.case_repo.create = MagicMock(return_value=expected_case)

        case_input = CaseCreate(
            title="Database Connection Timeout",
            description="Intermittent timeouts under load",
            priority=CasePriority.HIGH,
            case_type=CaseType.BUG,
            created_by=1,
        )

        # Act
        result = service.create_case(mock_db, case_input)

        # Assert
        assert result.id == 10
        assert result.status == CaseStatus.OPEN
        assert result.title == "Database Connection Timeout"
        service.user_repo.get_by_id.assert_called_once_with(mock_db, 1)
        service.case_repo.create.assert_called_once()

    def test_create_case_fails_when_creator_not_found(self):
        """Verify that create_case raises UserNotFoundError if creator ID is invalid."""
        service = CaseService()
        mock_db = MagicMock()
        service.user_repo.get_by_id = MagicMock(side_effect=UserNotFoundError(user_id=999))

        case_input = CaseCreate(
            title="Some Bug",
            created_by=999,
        )

        with pytest.raises(UserNotFoundError) as exc_info:
            service.create_case(mock_db, case_input)

        assert exc_info.value.user_id == 999
        service.user_repo.get_by_id.assert_called_once_with(mock_db, 999)

    def test_create_case_fails_when_assignee_not_found(self):
        """Verify that create_case raises UserNotFoundError if assignee ID does not exist."""
        service = CaseService()
        mock_db = MagicMock()

        # Creator exists (id=1), but assignee (id=999) does not exist
        def mock_get_user(db, user_id):
            if user_id == 1:
                return User(id=1, username="admin", email="a@b.com", full_name="Admin")
            raise UserNotFoundError(user_id=user_id)

        service.user_repo.get_by_id = MagicMock(side_effect=mock_get_user)

        case_input = CaseCreate(
            title="Task with invalid assignee",
            created_by=1,
            assigned_to=999,
        )

        with pytest.raises(UserNotFoundError) as exc_info:
            service.create_case(mock_db, case_input)

        assert exc_info.value.user_id == 999

    def test_update_case_fails_if_closed(self):
        """
        Business rule test:
        A closed case cannot have its status updated or changed.
        """
        service = CaseService()
        mock_db = MagicMock()

        closed_case = Case(
            id=5,
            title="Archived issue",
            status=CaseStatus.CLOSED,
            created_by=1,
        )
        service.case_repo.get_by_id = MagicMock(return_value=closed_case)

        update_data = CaseUpdate(status=CaseStatus.OPEN)

        with pytest.raises(ValidationError) as exc_info:
            service.update_case(mock_db, 5, update_data)

        assert "Cannot change the status of a CLOSED case" in exc_info.value.message

    def test_update_case_sets_resolved_at(self):
        """
        Business rule test:
        Transitioning status to RESOLVED automatically sets resolved_at timestamp.
        """
        service = CaseService()
        mock_db = MagicMock()

        existing_case = Case(
            id=12,
            title="Active issue",
            status=CaseStatus.IN_PROGRESS,
            created_by=1,
            resolved_at=None,
        )
        service.case_repo.get_by_id = MagicMock(return_value=existing_case)

        # Mock repo update to return the updated case
        def fake_update(db, case, updates):
            for k, v in updates.items():
                setattr(case, k, v)
            return case

        service.case_repo.update = MagicMock(side_effect=fake_update)

        update_data = CaseUpdate(status=CaseStatus.RESOLVED)
        updated = service.update_case(mock_db, 12, update_data)

        assert updated.status == CaseStatus.RESOLVED
        assert updated.resolved_at is not None
