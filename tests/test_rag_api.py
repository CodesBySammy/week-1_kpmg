"""
Tests for RAG REST API endpoints in FastAPI.
"""
import pytest
from fastapi.testclient import TestClient


def test_api_list_policies(client: TestClient):
    response = client.get("/api/v1/rag/policies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 6
    doc_ids = [d["document_id"] for d in data]
    assert "HR-POLICY-001" in doc_ids
    assert "IT-SECURITY-005" in doc_ids


def test_api_ingest_policies(client: TestClient):
    response = client.post("/api/v1/rag/ingest")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["documents_indexed"] >= 6
    assert data["chunks_indexed"] > 0


def test_api_retrieve_chunks(client: TestClient):
    payload = {
        "query": "What is the policy regarding password expiration and complexity?",
        "top_k": 3,
        "retrieval_mode": "hybrid",
        "use_reranker": True,
    }
    response = client.post("/api/v1/rag/retrieve", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["retrieval_mode"] == "hybrid"
    assert len(data["results"]) <= 3
    assert len(data["results"]) > 0
    top_doc = data["results"][0]["chunk"]["document_id"]
    assert top_doc == "IT-SECURITY-005"


def test_api_retrieve_with_filter(client: TestClient):
    payload = {
        "query": "allowance limits and reimbursement",
        "top_k": 5,
        "retrieval_mode": "vector",
        "filters": {"category": "Finance"},
    }
    response = client.post("/api/v1/rag/retrieve", json=payload)
    assert response.status_code == 200
    data = response.json()
    for item in data["results"]:
        assert item["chunk"]["metadata"]["category"] == "Finance"


def test_api_query_grounded_answer(client: TestClient):
    payload = {
        "question": "What are the rules regarding corporate password complexity?",
        "retrieval_mode": "hybrid",
        "top_k": 3,
        "use_reranker": True,
    }
    response = client.post("/api/v1/rag/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_grounded"] is True
    assert data["refusal"] is False
    assert len(data["citations"]) >= 1
    assert "IT-SECURITY-005" in data["answer"] or "password" in data["answer"].lower()


def test_api_query_unanswerable_refusal(client: TestClient):
    payload = {
        "question": "How do I build a nuclear reactor in my backyard?",
        "retrieval_mode": "hybrid",
        "top_k": 2,
    }
    response = client.post("/api/v1/rag/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["refusal"] is True
    assert any(w in data["answer"].lower() for w in ["unable", "cannot", "do not contain", "no relevant"])


def test_api_benchmark_endpoint(client: TestClient):
    response = client.get("/api/v1/rag/benchmark")
    assert response.status_code == 200
    data = response.json()
    assert "strategy_a_metrics" in data
    assert "strategy_b_metrics" in data
    assert data["strategy_b_metrics"]["hit_rate"] >= 0.5
    assert data["strategy_b_metrics"]["mrr"] > 0.0


def test_api_case_policy_check(client: TestClient, sample_case):
    response = client.post(f"/api/v1/rag/cases/{sample_case.id}/policy-check")
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == sample_case.id
    assert "policy_advice" in data
    assert "is_grounded" in data
    assert isinstance(data["citations"], list)


def test_api_case_policy_check_missing_case(client: TestClient):
    response = client.post("/api/v1/rag/cases/999999/policy-check")
    assert response.status_code == 404
