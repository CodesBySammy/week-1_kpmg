"""
Declared Schemas for Reference Lookup Data
"""

from typing import Dict

USER_REFERENCE_SCHEMA: Dict[str, str] = {
    "user_id": "int64",
    "department_id": "string",
    "tier": "string",
    "region": "string",
    "active": "bool",
}

DEPARTMENT_REFERENCE_SCHEMA: Dict[str, str] = {
    "department_id": "string",
    "department_name": "string",
    "lead_user_id": "int64",
}
