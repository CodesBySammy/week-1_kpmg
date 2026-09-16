"""
Unit Tests for Pipeline Transformation Modules
"""

from datetime import datetime, timezone
import pandas as pd
import pytest

from pipeline.transformations.aggregation import (
    aggregate_department_sla_summary,
    aggregate_priority_summary,
)
from pipeline.transformations.deduplication import deduplicate_cases
from pipeline.transformations.joins import join_case_reference_and_policies
from pipeline.transformations.standardization import (
    standardize_case_records,
    standardize_reference_users,
)
from pipeline.transformations.windowing import apply_window_metrics


def test_standardize_case_records():
    raw_df = pd.DataFrame([
        {
            "case_id": "101",
            "title": "  Bug in Login Flow  ",
            "description": None,
            "status": "open",
            "priority": "high",
            "case_type": "incident",
            "created_by": "1",
            "assigned_to": "2",
            "created_at": "2026-03-01 10:00:00",
            "updated_at": "2026-03-01 12:00:00",
            "resolved_at": None,
        }
    ])

    std_df = standardize_case_records(raw_df)

    assert std_df.loc[0, "case_id"] == 101
    assert std_df.loc[0, "title"] == "Bug in Login Flow"
    assert std_df.loc[0, "description"] == "No description provided"
    assert std_df.loc[0, "status"] == "OPEN"
    assert std_df.loc[0, "priority"] == "HIGH"
    assert std_df.loc[0, "case_type"] == "INCIDENT"
    assert std_df.loc[0, "created_at"].tzinfo == timezone.utc


def test_standardize_reference_users():
    raw_df = pd.DataFrame([
        {
            "user_id": "1",
            "username": "  alice  ",
            "department_id": "2",
            "tier": "l1",
            "region": "emea",
        }
    ])

    std_df = standardize_reference_users(raw_df)
    assert std_df.loc[0, "user_id"] == 1
    assert std_df.loc[0, "username"] == "alice"
    assert std_df.loc[0, "tier"] == "L1"
    assert std_df.loc[0, "region"] == "EMEA"


def test_deduplicate_cases():
    # Record with duplicate case_id: 1 older, 1 newer
    df = pd.DataFrame([
        {"case_id": 1, "title": "Older", "updated_at": "2026-03-01T10:00:00Z"},
        {"case_id": 1, "title": "Newer", "updated_at": "2026-03-01T12:00:00Z"},
        {"case_id": 2, "title": "Unique", "updated_at": "2026-03-01T11:00:00Z"},
    ])

    deduped_df, dup_count = deduplicate_cases(df, primary_key="case_id", order_by_col="updated_at")

    assert dup_count == 1
    assert len(deduped_df) == 2
    # Ensure latest record kept
    case1_record = deduped_df[deduped_df["case_id"] == 1].iloc[0]
    assert case1_record["title"] == "Newer"


def test_join_case_reference_and_policies():
    cases_df = pd.DataFrame([
        {
            "case_id": 1,
            "priority": "HIGH",
            "case_type": "SECURITY",
            "assigned_to": 10,
            "created_at": pd.to_datetime("2026-03-01T08:00:00Z"),
            "resolved_at": pd.to_datetime("2026-03-01T14:00:00Z"),  # 6 hours
            "status": "RESOLVED",
        }
    ])

    users_df = pd.DataFrame([
        {"user_id": 10, "department_id": 5, "tier": "L2", "region": "APAC"}
    ])

    depts_df = pd.DataFrame([
        {"department_id": 5, "department_name": "Cybersecurity"}
    ])

    policies_df = pd.DataFrame([
        {
            "policy_id": "POL-SEC-01",
            "priority": "HIGH",
            "case_type": "SECURITY",
            "target_resolution_hours": 4.0,  # 4h SLA vs 6h actual => Breached!
            "compliance_framework": "ISO27001",
        }
    ])

    enriched = join_case_reference_and_policies(cases_df, users_df, depts_df, policies_df)

    assert len(enriched) == 1
    row = enriched.iloc[0]
    assert row["assignee_department"] == "Cybersecurity"
    assert row["assignee_tier"] == "L2"
    assert row["resolution_time_hours"] == 6.0
    assert row["sla_breached"] is True or row["sla_breached"] == 1


def test_apply_window_metrics():
    df = pd.DataFrame([
        {"case_id": 1, "priority": "HIGH", "assignee_department": "Engineering", "resolution_time_hours": 10.0},
        {"case_id": 2, "priority": "HIGH", "assignee_department": "Engineering", "resolution_time_hours": 5.0},
        {"case_id": 3, "priority": "HIGH", "assignee_department": "Support", "resolution_time_hours": 8.0},
    ])

    windowed = apply_window_metrics(df)

    assert "priority_duration_rank" in windowed.columns
    assert "department_case_seq" in windowed.columns
    # The 5.0 hour case should have rank 1
    fastest_case = windowed[windowed["case_id"] == 2].iloc[0]
    assert fastest_case["priority_duration_rank"] == 1


def test_aggregation_summaries():
    df = pd.DataFrame([
        {"case_id": 1, "priority": "HIGH", "assignee_department": "Engineering", "resolution_time_hours": 4.0, "sla_breached": False},
        {"case_id": 2, "priority": "HIGH", "assignee_department": "Engineering", "resolution_time_hours": 8.0, "sla_breached": True},
        {"case_id": 3, "priority": "LOW", "assignee_department": "Support", "resolution_time_hours": 2.0, "sla_breached": False},
    ])

    dept_summary = aggregate_department_sla_summary(df)
    assert len(dept_summary) == 2
    eng_row = dept_summary[dept_summary["assignee_department"] == "Engineering"].iloc[0]
    assert eng_row["total_cases"] == 2
    assert eng_row["sla_breaches"] == 1
    assert eng_row["sla_compliance_pct"] == 50.0

    priority_summary = aggregate_priority_summary(df)
    assert len(priority_summary) == 2
    high_row = priority_summary[priority_summary["priority"] == "HIGH"].iloc[0]
    assert high_row["case_count"] == 2
    assert high_row["avg_resolution_hours"] == 6.0
