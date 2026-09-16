"""
Declared Schemas for Policy Metadata (Parquet and REST API Sources)
"""

from typing import Dict

POLICY_METADATA_SCHEMA: Dict[str, str] = {
    "policy_id": "string",
    "case_type": "string",
    "priority": "string",
    "sla_hours": "float64",
    "escalation_tier": "string",
    "compliance_framework": "string",
    "auto_escalate": "bool",
}
