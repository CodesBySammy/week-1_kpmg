"""
Declared Schemas for Case Records across Data Layers
"""

from typing import Dict, List

# Allowed Enum values strictly aligned with Week 1 domain rules
ALLOWED_STATUSES: List[str] = ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"]
ALLOWED_PRIORITIES: List[str] = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
ALLOWED_CASE_TYPES: List[str] = ["BUG", "FEATURE_REQUEST", "INQUIRY", "COMPLAINT"]

# Source Schema (Raw Ingestion Contract)
SOURCE_CASE_SCHEMA: Dict[str, type] = {
    "case_id": str,
    "title": str,
    "description": str,
    "status": str,
    "priority": str,
    "case_type": str,
    "created_by": str,
    "assigned_to": str,
    "created_at": str,
    "updated_at": str,
    "resolved_at": str,
}

# Standardized Schema (Normalized Types & Formats)
STANDARDIZED_CASE_SCHEMA: Dict[str, str] = {
    "case_id": "int64",
    "title": "string",
    "description": "string",
    "status": "string",
    "priority": "string",
    "case_type": "string",
    "created_by": "int64",
    "assigned_to": "Int64",  # Nullable integer
    "created_at": "datetime64[ns, UTC]",
    "updated_at": "datetime64[ns, UTC]",
    "resolved_at": "datetime64[ns, UTC]",
}

# Curated Schema (Business-Ready & Enriched with Reference & Policy Data)
CURATED_CASE_SCHEMA: Dict[str, str] = {
    "case_id": "int64",
    "title": "string",
    "description": "string",
    "status": "string",
    "priority": "string",
    "case_type": "string",
    "created_by": "int64",
    "assigned_to": "Int64",
    "assignee_department": "string",
    "assignee_tier": "string",
    "assignee_region": "string",
    "sla_target_hours": "float64",
    "policy_id": "string",
    "compliance_framework": "string",
    "created_at": "datetime64[ns, UTC]",
    "updated_at": "datetime64[ns, UTC]",
    "resolved_at": "datetime64[ns, UTC]",
    "resolution_time_hours": "float64",
    "sla_breached": "boolean",
}
