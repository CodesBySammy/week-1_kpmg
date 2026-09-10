"""
Tests for User Endpoints and Global Error Handlers
"""

from unittest.mock import patch
from app.exceptions import DatabaseError


def test_list_users_api(client, sample_user, second_user):
    """Verify GET /api/v1/users returns all users."""
    response = client.get("/api/v1/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    usernames = [u["username"] for u in data]
    assert sample_user.username in usernames
    assert second_user.username in usernames


def test_database_error_handler(client, sample_user):
    """
    Verify that when a DatabaseError occurs, the global exception handler
    returns HTTP 500 without leaking internal database traceback details.
    """
    with patch("app.services.case_service.CaseRepository.create") as mock_create:
        mock_create.side_effect = DatabaseError("Disk failure or unique constraint")
        payload = {
            "title": "Trigger DB Error",
            "created_by": sample_user.id,
        }
        response = client.post("/api/v1/cases", json=payload)
        assert response.status_code == 500
        data = response.json()
        assert data["error"]["code"] == "INTERNAL_ERROR"
        assert data["error"]["message"] == "An internal error occurred"
        # Crucial security assertion: real exception message is not leaked
        assert "Disk failure" not in data["error"]["message"]
