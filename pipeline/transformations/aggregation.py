"""
Aggregation and Analytical Summary Transformations

Aggregates curated case metrics for executive and operational reporting.
"""

from typing import Dict
import pandas as pd


def aggregate_department_sla_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregates case metrics by assignee department."""
    if len(df) == 0:
        return pd.DataFrame()

    dept_col = "assignee_department" if "assignee_department" in df.columns else "department"
    if dept_col not in df.columns:
        return pd.DataFrame()

    summary = (
        df.groupby(dept_col)
        .agg(
            total_cases=("case_id", "count"),
            sla_breaches=("sla_breached", lambda s: int(s.sum()) if "sla_breached" in df.columns else 0),
            avg_resolution_hours=("resolution_time_hours", lambda s: round(float(s.mean()), 2) if "resolution_time_hours" in df.columns else 0.0),
        )
        .reset_index()
    )

    summary["sla_compliance_pct"] = round(
        ((summary["total_cases"] - summary["sla_breaches"]) / summary["total_cases"]) * 100.0,
        2,
    )
    return summary


def aggregate_priority_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregates case metrics by priority level."""
    if len(df) == 0:
        return pd.DataFrame()

    summary = (
        df.groupby("priority")
        .agg(
            case_count=("case_id", "count"),
            avg_resolution_hours=("resolution_time_hours", lambda s: round(float(s.mean()), 2)),
        )
        .reset_index()
    )
    return summary
