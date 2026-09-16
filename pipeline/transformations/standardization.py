"""
Data Standardization Transformations

Standardizes raw heterogeneous data into consistent types, casings, and formats.
"""

from typing import Optional
import pandas as pd


def standardize_case_records(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardizes raw case DataFrame:
    - Strips whitespace from text fields
    - Converts status, priority, and case_type to uppercase
    - Coerces case_id and user IDs to integer types
    - Parses timestamps to UTC datetime64[ns, UTC]
    - Imputes null descriptions with default text
    """
    cleaned = df.copy()

    # 1. Clean string columns
    str_cols = ["title", "description", "status", "priority", "case_type"]
    for col in str_cols:
        if col in cleaned.columns:
            cleaned[col] = cleaned[col].astype(str).str.strip()

    # Normalize enums to uppercase
    for col in ["status", "priority", "case_type"]:
        if col in cleaned.columns:
            cleaned[col] = cleaned[col].str.upper()

    # 2. Impute null/empty descriptions
    if "description" in cleaned.columns:
        empty_mask = (cleaned["description"] == "") | cleaned["description"].isna()
        cleaned.loc[empty_mask, "description"] = "No description provided"

    # 3. Cast numeric identifiers
    if "case_id" in cleaned.columns:
        cleaned["case_id"] = pd.to_numeric(cleaned["case_id"], errors="coerce").astype("Int64")

    if "created_by" in cleaned.columns:
        cleaned["created_by"] = pd.to_numeric(cleaned["created_by"], errors="coerce").astype("Int64")

    if "assigned_to" in cleaned.columns:
        cleaned["assigned_to"] = pd.to_numeric(cleaned["assigned_to"], errors="coerce").astype("Int64")

    # 4. Standardize Timestamps to UTC
    time_cols = ["created_at", "updated_at", "resolved_at"]
    for col in time_cols:
        if col in cleaned.columns:
            cleaned[col] = pd.to_datetime(cleaned[col], errors="coerce", utc=True)

    return cleaned


def standardize_reference_users(df: pd.DataFrame) -> pd.DataFrame:
    """Standardizes user reference lookup data."""
    cleaned = df.copy()
    if "user_id" in cleaned.columns:
        cleaned["user_id"] = pd.to_numeric(cleaned["user_id"], errors="coerce").astype("int64")
    if "username" in cleaned.columns:
        cleaned["username"] = cleaned["username"].astype(str).str.strip()
    if "department_id" in cleaned.columns:
        cleaned["department_id"] = cleaned["department_id"].astype(str).str.strip().str.upper()
    if "tier" in cleaned.columns:
        cleaned["tier"] = cleaned["tier"].astype(str).str.strip().str.upper()
    if "region" in cleaned.columns:
        cleaned["region"] = cleaned["region"].astype(str).str.strip().str.upper()
    if "active" in cleaned.columns:
        cleaned["active"] = cleaned["active"].astype(bool)
    return cleaned


def standardize_departments(df: pd.DataFrame) -> pd.DataFrame:
    """Standardizes department reference data."""
    cleaned = df.copy()
    if "department_id" in cleaned.columns:
        cleaned["department_id"] = cleaned["department_id"].astype(str).str.strip().str.upper()
    if "department_name" in cleaned.columns:
        cleaned["department_name"] = cleaned["department_name"].astype(str).str.strip()
    if "lead_user_id" in cleaned.columns:
        cleaned["lead_user_id"] = pd.to_numeric(cleaned["lead_user_id"], errors="coerce").astype("Int64")
    return cleaned


def standardize_policy_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """Standardizes policy metadata from Parquet or REST API."""
    cleaned = df.copy()
    if "policy_id" in cleaned.columns:
        cleaned["policy_id"] = cleaned["policy_id"].astype(str).str.strip().str.upper()
    if "case_type" in cleaned.columns:
        cleaned["case_type"] = cleaned["case_type"].astype(str).str.strip().str.upper()
    if "priority" in cleaned.columns:
        cleaned["priority"] = cleaned["priority"].astype(str).str.strip().str.upper()
    
    # SLA hours column name normalization (handles either sla_hours or max_resolution_hours)
    if "max_resolution_hours" in cleaned.columns and "sla_hours" not in cleaned.columns:
        cleaned["sla_hours"] = cleaned["max_resolution_hours"]
    if "sla_hours" in cleaned.columns:
        cleaned["sla_hours"] = pd.to_numeric(cleaned["sla_hours"], errors="coerce").astype(float)

    if "regulatory_body" in cleaned.columns and "compliance_framework" not in cleaned.columns:
        cleaned["compliance_framework"] = cleaned["regulatory_body"]
    if "compliance_framework" in cleaned.columns:
        cleaned["compliance_framework"] = cleaned["compliance_framework"].astype(str).str.strip().str.upper()

    if "escalation_level" in cleaned.columns and "escalation_tier" not in cleaned.columns:
        cleaned["escalation_tier"] = cleaned["escalation_level"]
    return cleaned
