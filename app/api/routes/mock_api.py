"""
Mock REST API Routes for Week 2 Pipeline Integration

WHY THIS EXISTS:
    The Week 2 curriculum requires the data pipeline to ingest:
    "case records, reference data, and policy metadata from files and a mock REST API."
    This router provides a deterministic, mock REST API serving enterprise
    compliance policies and SLA definitions for downstream ingestion.
"""

from typing import Any, List, Optional
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/mock", tags=["Mock Data Pipeline Source"])

# ── Deterministic In-Memory Mock Policy Dataset ──────────────────────
MOCK_POLICIES: List[dict[str, Any]] = [
    {
        "policy_id": "POL-BUG-CRIT",
        "case_type": "BUG",
        "priority": "CRITICAL",
        "sla_hours": 4,
        "escalation_tier": "tier_3_lead",
        "compliance_framework": "SOC2_TYPE2",
        "auto_escalate": True,
        "updated_at": "2026-09-01T00:00:00Z",
    },
    {
        "policy_id": "POL-BUG-HIGH",
        "case_type": "BUG",
        "priority": "HIGH",
        "sla_hours": 24,
        "escalation_tier": "tier_2_senior",
        "compliance_framework": "SOC2_TYPE2",
        "auto_escalate": False,
        "updated_at": "2026-09-01T00:00:00Z",
    },
    {
        "policy_id": "POL-BUG-MED",
        "case_type": "BUG",
        "priority": "MEDIUM",
        "sla_hours": 72,
        "escalation_tier": "tier_1_analyst",
        "compliance_framework": "INTERNAL_SLA",
        "auto_escalate": False,
        "updated_at": "2026-09-01T00:00:00Z",
    },
    {
        "policy_id": "POL-BUG-LOW",
        "case_type": "BUG",
        "priority": "LOW",
        "sla_hours": 168,
        "escalation_tier": "tier_1_analyst",
        "compliance_framework": "INTERNAL_SLA",
        "auto_escalate": False,
        "updated_at": "2026-09-01T00:00:00Z",
    },
    {
        "policy_id": "POL-FEAT-ALL",
        "case_type": "FEATURE_REQUEST",
        "priority": "MEDIUM",
        "sla_hours": 360,
        "escalation_tier": "product_owner",
        "compliance_framework": "PRODUCT_GOVERNANCE",
        "auto_escalate": False,
        "updated_at": "2026-09-01T00:00:00Z",
    },
    {
        "policy_id": "POL-INQ-ALL",
        "case_type": "INQUIRY",
        "priority": "LOW",
        "sla_hours": 48,
        "escalation_tier": "tier_1_analyst",
        "compliance_framework": "SUPPORT_SLA",
        "auto_escalate": False,
        "updated_at": "2026-09-01T00:00:00Z",
    },
    {
        "policy_id": "POL-COMP-CRIT",
        "case_type": "COMPLAINT",
        "priority": "CRITICAL",
        "sla_hours": 8,
        "escalation_tier": "compliance_officer",
        "compliance_framework": "ISO_27001",
        "auto_escalate": True,
        "updated_at": "2026-09-01T00:00:00Z",
    },
]


@router.get("/policies", response_model=List[dict[str, Any]])
def get_mock_policies(
    case_type: Optional[str] = Query(None, description="Optional case type filter"),
    priority: Optional[str] = Query(None, description="Optional priority filter"),
) -> List[dict[str, Any]]:
    """
    Retrieve mock policy metadata for pipeline ingestion.
    Supports optional query filtering by case_type and priority.
    """
    results = MOCK_POLICIES
    if case_type:
        results = [p for p in results if p["case_type"].upper() == case_type.upper()]
    if priority:
        results = [p for p in results if p["priority"].upper() == priority.upper()]
    return results


@router.get("/policies/{policy_id}", response_model=dict[str, Any])
def get_mock_policy_by_id(policy_id: str) -> dict[str, Any]:
    """Retrieve a single policy by its unique identifier."""
    for policy in MOCK_POLICIES:
        if policy["policy_id"].upper() == policy_id.upper():
            return policy
    raise HTTPException(
        status_code=404,
        detail=f"Policy with ID '{policy_id}' not found in mock catalog",
    )
