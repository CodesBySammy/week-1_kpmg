"""
Relational Join and Enrichment Transformations

Joins case records with reference datasets (users, departments) and policy metadata.
Computes SLA resolution intervals and compliance breaches.
"""

from datetime import datetime, timezone
from typing import Optional
import numpy as np
import pandas as pd


def join_case_reference_and_policies(
    cases_df: pd.DataFrame,
    users_df: pd.DataFrame,
    depts_df: pd.DataFrame,
    policies_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Enriches cases by joining:
    1. Users reference data (assignee tier, region, department_id)
    2. Department reference data (assignee department name)
    3. Policy metadata (SLA target hours, policy ID, compliance framework)
    Computes business metrics:
    - resolution_time_hours
    - sla_breached flag
    """
    if len(cases_df) == 0:
        return cases_df.copy()

    enriched = cases_df.copy()

    # 1. Join Assignee Reference Info
    if not users_df.empty and "assigned_to" in enriched.columns:
        user_subset = users_df[["user_id", "department_id", "tier", "region"]].copy()
        user_subset.rename(
            columns={
                "department_id": "assignee_department_id",
                "tier": "assignee_tier",
                "region": "assignee_region",
            },
            inplace=True,
        )
        enriched = enriched.merge(
            user_subset,
            left_on="assigned_to",
            right_on="user_id",
            how="left",
        )
        if "user_id" in enriched.columns:
            enriched.drop(columns=["user_id"], inplace=True)

    # 2. Join Department Name
    if not depts_df.empty and "assignee_department_id" in enriched.columns:
        dept_subset = depts_df[["department_id", "department_name"]].copy()
        dept_subset.rename(columns={"department_name": "assignee_department"}, inplace=True)
        enriched = enriched.merge(
            dept_subset,
            left_on="assignee_department_id",
            right_on="department_id",
            how="left",
        )
        for col_to_drop in ["assignee_department_id", "department_id"]:
            if col_to_drop in enriched.columns:
                enriched.drop(columns=[col_to_drop], inplace=True)

    # Fill defaults for unassigned cases
    if "assignee_department" in enriched.columns:
        enriched["assignee_department"] = enriched["assignee_department"].fillna("Unassigned Pool")
    if "assignee_tier" in enriched.columns:
        enriched["assignee_tier"] = enriched["assignee_tier"].fillna("N/A")
    if "assignee_region" in enriched.columns:
        enriched["assignee_region"] = enriched["assignee_region"].fillna("GLOBAL")

    # 3. Join Policy Metadata (on case_type and priority)
    if not policies_df.empty:
        available_policy_cols = [
            c for c in ["policy_id", "sla_hours", "target_resolution_hours", "sla_target_hours", "compliance_framework", "regulatory_body", "escalation_tier"]
            if c in policies_df.columns
        ]
        policy_subset = policies_df[
            ["case_type", "priority"] + available_policy_cols
        ].drop_duplicates(subset=["case_type", "priority"]).copy()
        
        if "sla_hours" in policy_subset.columns:
            policy_subset.rename(columns={"sla_hours": "sla_target_hours"}, inplace=True)
        elif "target_resolution_hours" in policy_subset.columns:
            policy_subset.rename(columns={"target_resolution_hours": "sla_target_hours"}, inplace=True)

        enriched = enriched.merge(
            policy_subset,
            on=["case_type", "priority"],
            how="left",
        )

    if "sla_target_hours" not in enriched.columns:
        enriched["sla_target_hours"] = 72.0  # Default fallback SLA
    else:
        enriched["sla_target_hours"] = enriched["sla_target_hours"].fillna(72.0)

    # 4. Compute Resolution Time and SLA Breach
    now = datetime.now(timezone.utc)
    
    # Calculate hours to resolution
    if "resolved_at" in enriched.columns and "created_at" in enriched.columns:
        resolved_mask = enriched["resolved_at"].notna()
        # For resolved cases: resolved_at - created_at
        diff_resolved = (enriched.loc[resolved_mask, "resolved_at"] - enriched.loc[resolved_mask, "created_at"]).dt.total_seconds() / 3600.0
        enriched.loc[resolved_mask, "resolution_time_hours"] = diff_resolved.round(2)
        
        # For open cases: now - created_at
        open_mask = ~resolved_mask
        diff_open = (pd.Timestamp(now) - enriched.loc[open_mask, "created_at"]).dt.total_seconds() / 3600.0
        enriched.loc[open_mask, "resolution_time_hours"] = diff_open.round(2)
        
        # SLA Breach boolean
        enriched["sla_breached"] = enriched["resolution_time_hours"] > enriched["sla_target_hours"]

    return enriched
