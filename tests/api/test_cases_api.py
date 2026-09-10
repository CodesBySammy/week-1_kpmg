"""
API Integration Tests for Case Management Endpoints

WHY API TESTS:
    API tests exercise the complete HTTP request/response cycle:
      1. HTTP routing & method dispatch (POST, GET, PUT)
      2. Request body JSON deserialization and Pydantic validation
      3. FastAPI Dependency Injection (database sessions)
      4. Service layer orchestration and business rules
      5. Repository persistence into the relational database
      6. Consistent JSON response formatting and HTTP status codes
      7. Exception handling & error contract compliance (404, 422, 500)

We use FastAPI's `TestClient` which makes real in-process HTTP calls.
"""

import pytest
from app.models.case import CasePriority, CaseStatus, CaseType


class TestCaseAPI:
    """Test suite for /api/v1/cases endpoints."""

    def test_health_check(self, client):
        """Verify the GET /health endpoint returns 200 OK and healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "app" in data
        assert "version" in data

    def test_create_user_api(self, client):
        """Verify POST /api/v1/users successfully creates a user with 201 Created."""
        payload = {
            "username": "api_user",
            "email": "api_user@kpmg.com",
            "full_name": "API Test User",
            "role": "analyst",
        }
        response = client.post("/api/v1/users", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["username"] == "api_user"
        assert data["email"] == "api_user@kpmg.com"

    def test_create_case_valid(self, client, sample_user):
        """
        Verify valid case creation returns HTTP 201 Created,
        proper response body, and auto-generated fields.
        """
        payload = {
            "title": "API Gateway Connection Refused",
            "description": "Downstream microservice connection drops intermittently.",
            "priority": "HIGH",
            "case_type": "BUG",
            "created_by": sample_user.id,
        }
        response = client.post("/api/v1/cases", json=payload)
        assert response.status_code == 201
        data = response.json()

        assert data["id"] is not None
        assert data["title"] == payload["title"]
        assert data["description"] == payload["description"]
        assert data["priority"] == "HIGH"
        assert data["case_type"] == "BUG"
        assert data["status"] == "OPEN"
        assert data["created_by"] == sample_user.id
        assert data["assigned_to"] is None
        assert data["created_at"] is not None
        assert data["updated_at"] is not None

    def test_create_case_missing_required_title(self, client, sample_user):
        """
        Verify request validation failure: missing 'title' field
        returns HTTP 422 Unprocessable Entity with structured error response.
        """
        payload = {
            "created_by": sample_user.id,
            # Missing "title"
        }
        response = client.post("/api/v1/cases", json=payload)
        assert response.status_code == 422
        data = response.json()

        assert "error" in data
        assert data["error"]["code"] == "REQUEST_VALIDATION_ERROR"
        assert "details" in data["error"]
        # Confirm that the specific field in error is identified
        error_fields = [d["field"] for d in data["error"]["details"]]
        assert any("title" in field for field in error_fields)

    def test_create_case_invalid_title_length(self, client, sample_user):
        """Verify empty string title fails min_length validation with 422."""
        payload = {
            "title": "",  # min_length is 1
            "created_by": sample_user.id,
        }
        response = client.post("/api/v1/cases", json=payload)
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "REQUEST_VALIDATION_ERROR"

    def test_create_case_nonexistent_creator(self, client):
        """
        Verify domain rule: creating a case with a non-existent creator ID
        returns HTTP 404 with standard error contract.
        """
        payload = {
            "title": "Unassigned System Failure",
            "created_by": 999999,  # Does not exist
        }
        response = client.post("/api/v1/cases", json=payload)
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "USER_NOT_FOUND"
        assert "User with id 999999 not found" in data["error"]["message"]

    def test_get_case_existing(self, client, sample_case):
        """Verify retrieving an existing case returns HTTP 200 OK and accurate JSON."""
        response = client.get(f"/api/v1/cases/{sample_case.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_case.id
        assert data["title"] == sample_case.title
        assert data["status"] == sample_case.status.value

    def test_get_case_missing(self, client):
        """Verify retrieving a non-existent case returns HTTP 404 Not Found."""
        response = client.get("/api/v1/cases/99999")
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "CASE_NOT_FOUND"
        assert "Case with id 99999 not found" in data["error"]["message"]

    def test_update_case_valid(self, client, sample_case, second_user):
        """
        Verify PUT /api/v1/cases/{id} successfully updates fields,
        returns HTTP 200 OK with updated data.
        """
        update_payload = {
            "title": "Updated Title: Service Disruption",
            "status": "IN_PROGRESS",
            "priority": "CRITICAL",
            "assigned_to": second_user.id,
        }
        response = client.put(f"/api/v1/cases/{sample_case.id}", json=update_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_case.id
        assert data["title"] == "Updated Title: Service Disruption"
        assert data["status"] == "IN_PROGRESS"
        assert data["priority"] == "CRITICAL"
        assert data["assigned_to"] == second_user.id

    def test_update_case_empty_body_rejected(self, client, sample_case):
        """Verify that updating with an empty payload returns 422 VALIDATION_ERROR."""
        response = client.put(f"/api/v1/cases/{sample_case.id}", json={})
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "No fields to update were provided" in data["error"]["message"]

    def test_update_case_nonexistent_case(self, client):
        """Verify updating a non-existent case returns HTTP 404."""
        response = client.put("/api/v1/cases/88888", json={"title": "New Title"})
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "CASE_NOT_FOUND"

    def test_update_case_cannot_reopen_closed(self, client, sample_case):
        """
        Verify business rule: cannot alter or reopen a CLOSED case.
        """
        # First close the case
        close_payload = {"status": "CLOSED"}
        res1 = client.put(f"/api/v1/cases/{sample_case.id}", json=close_payload)
        assert res1.status_code == 200
        assert res1.json()["status"] == "CLOSED"

        # Try to reopen or modify
        reopen_payload = {"status": "OPEN"}
        res2 = client.put(f"/api/v1/cases/{sample_case.id}", json=reopen_payload)
        assert res2.status_code == 422
        data = res2.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "Cannot change the status of a CLOSED case" in data["error"]["message"]

    def test_list_cases_pagination_and_filter(self, client, sample_user):
        """Verify GET /api/v1/cases returns list and responds to query filters."""
        # Create a few cases with different statuses
        client.post("/api/v1/cases", json={"title": "Case A", "priority": "LOW", "created_by": sample_user.id})
        client.post("/api/v1/cases", json={"title": "Case B", "priority": "CRITICAL", "created_by": sample_user.id})

        response = client.get("/api/v1/cases?limit=10&priority=CRITICAL")
        assert response.status_code == 200
        data = response.json()
        assert "cases" in data
        assert "total" in data
        for c in data["cases"]:
            assert c["priority"] == "CRITICAL"
