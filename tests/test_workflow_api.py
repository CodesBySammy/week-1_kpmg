"""
Integration Tests for Week 4 Workflow REST API Endpoints.

Verifies:
  1. Readiness probe /ready.
  2. Authentication token generation /auth/token.
  3. Workflow execution /execute with safe read and consequential actions.
  4. Human approval approval flow (/approvals, /approve, /reject).
  5. X-Correlation-ID middleware propagation.
"""

import pytest
from fastapi.testclient import TestClient

from app.database.session import SessionLocal, create_tables
from app.main import app
from app.models.case import Case, CasePriority, CaseStatus, User

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_api_data():
    """Ensure database has seeded users and test cases."""
    create_tables()
    db = SessionLocal()
    try:
        # Seed test agent
        agent = db.query(User).filter(User.username == "api_agent").first()
        if not agent:
            agent = User(
                username="api_agent",
                email="agent@example.com",
                full_name="API Agent",
                role="agent",
            )
            db.add(agent)
            db.commit()
            db.refresh(agent)

        # Seed test manager
        manager = db.query(User).filter(User.username == "api_manager").first()
        if not manager:
            manager = User(
                username="api_manager",
                email="manager@example.com",
                full_name="API Manager",
                role="manager",
            )
            db.add(manager)
            db.commit()
            db.refresh(manager)

        # Seed test case
        case = db.query(Case).filter(Case.title == "API Test Case").first()
        if not case:
            case = Case(
                title="API Test Case",
                description="Case for API testing",
                status=CaseStatus.OPEN,
                priority=CasePriority.MEDIUM,
                created_by=agent.id,
            )
            db.add(case)
            db.commit()
            db.refresh(case)

        yield
    finally:
        db.close()


def test_readiness_probe():
    """Verify /ready endpoint returns healthy dependency status."""
    resp = client.get("/ready")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ready"
    assert data["checks"]["database"] is True
    assert data["checks"]["workflow_engine"] is True


def test_correlation_id_propagation():
    """Verify X-Correlation-ID header is propagated back in response."""
    test_cid = "corr-client-custom-12345"
    resp = client.get("/health", headers={"X-Correlation-ID": test_cid})
    assert resp.status_code == 200
    assert resp.headers.get("X-Correlation-ID") == test_cid


def test_workflow_token_issuance():
    """Verify /auth/token endpoint generates valid JWT tokens."""
    resp = client.post(
        "/api/v1/workflow/auth/token",
        json={"username": "api_agent", "role": "agent", "user_id": 10},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["role"] == "agent"


def test_workflow_execute_unauthenticated():
    """Verify executing workflow without auth bearer token is rejected with 401."""
    resp = client.post(
        "/api/v1/workflow/execute",
        json={"prompt": "Retrieve case 1"},
    )
    assert resp.status_code == 401


def test_workflow_execute_safe_read():
    """Verify authenticated agent can execute safe read operation."""
    # Obtain token
    token_resp = client.post(
        "/api/v1/workflow/auth/token",
        json={"username": "api_agent", "role": "agent", "user_id": 1},
    )
    token = token_resp.json()["access_token"]

    resp = client.post(
        "/api/v1/workflow/execute",
        json={"prompt": "Show me details for case 1"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["final_state"] == "COMPLETED"
    assert data["intent"] == "RETRIEVE_CASE_DETAILS"
    assert data["tool_result"]["case_id"] == 1


def test_workflow_consequential_approval_roundtrip():
    """Verify full human-in-the-loop lifecycle: execute -> approval required -> manager approves -> re-execute."""
    # 1. Agent token
    agent_token = client.post(
        "/api/v1/workflow/auth/token",
        json={"username": "api_agent", "role": "agent", "user_id": 1},
    ).json()["access_token"]

    # 2. Manager token
    manager_token = client.post(
        "/api/v1/workflow/auth/token",
        json={"username": "api_manager", "role": "manager", "user_id": 2},
    ).json()["access_token"]

    # 3. Agent requests consequential update
    exec_resp1 = client.post(
        "/api/v1/workflow/execute",
        json={"prompt": "Please update case 1 status to in_progress"},
        headers={"Authorization": f"Bearer {agent_token}"},
    )
    assert exec_resp1.status_code == 200
    res_data1 = exec_resp1.json()
    assert res_data1["final_state"] == "APPROVAL_REQUIRED"
    req_id = res_data1["approval_id"]

    # 4. Check pending approvals
    list_resp = client.get(
        "/api/v1/workflow/approvals",
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert list_resp.status_code == 200
    approvals = list_resp.json()["approvals"]
    assert any(a["approval_id"] == req_id for a in approvals)

    # 5. Manager approves
    approve_resp = client.post(
        f"/api/v1/workflow/approval/{req_id}/approve",
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert approve_resp.status_code == 200
    approval_token = approve_resp.json()["approval_token"]

    # 6. Manager executes with approval token
    exec_resp2 = client.post(
        "/api/v1/workflow/execute",
        json={
            "prompt": "Please update case 1 status to in_progress",
            "approval_token": approval_token,
        },
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert exec_resp2.status_code == 200
    res_data2 = exec_resp2.json()
    assert res_data2["final_state"] == "COMPLETED"
    assert res_data2["tool_result"]["status"].lower() == "in_progress"


def test_workflow_metrics_endpoint():
    """Verify /metrics returns system operational metrics."""
    resp = client.get("/api/v1/workflow/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_requests" in data
    assert "latency_metrics" in data
