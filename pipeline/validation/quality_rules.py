"""
Automated Data Quality Rules Engine

Implements explicit, rule-based data quality controls.
Invalid records are captured with comprehensive quarantine metadata.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
import pandas as pd

from pipeline.schemas.case_schema import (
    ALLOWED_CASE_TYPES,
    ALLOWED_PRIORITIES,
    ALLOWED_STATUSES,
)


class RuleSeverity(str, Enum):
    CRITICAL = "CRITICAL"  # Record must be quarantined immediately
    WARNING = "WARNING"    # Record is processed with logged warning


class FailureBehavior(str, Enum):
    QUARANTINE = "QUARANTINE"
    WARN_AND_PASS = "WARN_AND_PASS"


@dataclass
class QualityRule:
    """Specification of an automated data quality control rule."""
    rule_id: str
    description: str
    affected_dataset: str
    severity: RuleSeverity
    failure_behavior: FailureBehavior
    evaluator: Callable[[pd.Series, Optional[Dict[str, Any]]], Tuple[bool, str]]


def check_required_title(row: pd.Series, context: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
    title = row.get("title")
    if pd.isna(title) or str(title).strip() == "":
        return False, "Title is null or empty"
    return True, ""


def check_valid_status(row: pd.Series, context: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
    status = str(row.get("status", "")).strip().upper()
    if status not in ALLOWED_STATUSES:
        return False, f"Status '{status}' not in allowed enum {ALLOWED_STATUSES}"
    return True, ""


def check_valid_priority(row: pd.Series, context: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
    priority = str(row.get("priority", "")).strip().upper()
    if priority not in ALLOWED_PRIORITIES:
        return False, f"Priority '{priority}' not in allowed enum {ALLOWED_PRIORITIES}"
    return True, ""


def check_valid_case_type(row: pd.Series, context: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
    ctype = str(row.get("case_type", "")).strip().upper()
    if ctype not in ALLOWED_CASE_TYPES:
        return False, f"Case type '{ctype}' not in allowed enum {ALLOWED_CASE_TYPES}"
    return True, ""


def check_positive_id(row: pd.Series, context: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
    val = row.get("case_id")
    try:
        int_val = int(val)
        if int_val <= 0:
            return False, f"Case ID {int_val} is not a positive integer"
    except (ValueError, TypeError):
        return False, f"Case ID '{val}' is not a valid integer"
    return True, ""


def check_referential_creator(row: pd.Series, context: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
    val = row.get("created_by")
    try:
        creator_id = int(val)
        if context and "valid_user_ids" in context:
            if creator_id not in context["valid_user_ids"]:
                return False, f"Creator user ID {creator_id} does not exist in reference data"
    except (ValueError, TypeError):
        return False, f"created_by '{val}' is not a valid integer"
    return True, ""


def check_referential_assignee(row: pd.Series, context: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
    val = row.get("assigned_to")
    if pd.isna(val) or str(val).strip() == "":
        return True, ""  # Unassigned case is valid
    try:
        assignee_id = int(val)
        if context and "valid_user_ids" in context:
            if assignee_id not in context["valid_user_ids"]:
                return False, f"Assignee user ID {assignee_id} does not exist in reference data"
    except (ValueError, TypeError):
        return False, f"assigned_to '{val}' is not a valid integer"
    return True, ""


def check_valid_created_at(row: pd.Series, context: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
    val = row.get("created_at")
    if pd.isna(val) or str(val).strip() == "":
        return False, "created_at timestamp is null or empty"
    try:
        pd.to_datetime(val)
    except Exception:
        return False, f"created_at timestamp '{val}' cannot be parsed into ISO datetime"
    return True, ""


# Standard Quality Rules Catalog for Case Management
CASE_QUALITY_RULES: List[QualityRule] = [
    QualityRule(
        rule_id="RULE-CASE-001",
        description="Case title must be non-null and non-empty",
        affected_dataset="cases",
        severity=RuleSeverity.CRITICAL,
        failure_behavior=FailureBehavior.QUARANTINE,
        evaluator=check_required_title,
    ),
    QualityRule(
        rule_id="RULE-CASE-002",
        description="Case status must match domain enum (OPEN, IN_PROGRESS, RESOLVED, CLOSED)",
        affected_dataset="cases",
        severity=RuleSeverity.CRITICAL,
        failure_behavior=FailureBehavior.QUARANTINE,
        evaluator=check_valid_status,
    ),
    QualityRule(
        rule_id="RULE-CASE-003",
        description="Case priority must match domain enum (LOW, MEDIUM, HIGH, CRITICAL)",
        affected_dataset="cases",
        severity=RuleSeverity.CRITICAL,
        failure_behavior=FailureBehavior.QUARANTINE,
        evaluator=check_valid_priority,
    ),
    QualityRule(
        rule_id="RULE-CASE-004",
        description="Case type must match domain enum (BUG, FEATURE_REQUEST, INQUIRY, COMPLAINT)",
        affected_dataset="cases",
        severity=RuleSeverity.CRITICAL,
        failure_behavior=FailureBehavior.QUARANTINE,
        evaluator=check_valid_case_type,
    ),
    QualityRule(
        rule_id="RULE-CASE-005",
        description="Case ID must be a positive integer greater than zero",
        affected_dataset="cases",
        severity=RuleSeverity.CRITICAL,
        failure_behavior=FailureBehavior.QUARANTINE,
        evaluator=check_positive_id,
    ),
    QualityRule(
        rule_id="RULE-CASE-006",
        description="Case creator must reference an existing user ID",
        affected_dataset="cases",
        severity=RuleSeverity.CRITICAL,
        failure_behavior=FailureBehavior.QUARANTINE,
        evaluator=check_referential_creator,
    ),
    QualityRule(
        rule_id="RULE-CASE-007",
        description="Case assignee must reference an existing user ID if assigned",
        affected_dataset="cases",
        severity=RuleSeverity.CRITICAL,
        failure_behavior=FailureBehavior.QUARANTINE,
        evaluator=check_referential_assignee,
    ),
    QualityRule(
        rule_id="RULE-CASE-008",
        description="created_at must be a valid parseable datetime",
        affected_dataset="cases",
        severity=RuleSeverity.CRITICAL,
        failure_behavior=FailureBehavior.QUARANTINE,
        evaluator=check_valid_created_at,
    ),
]


class QualityRulesEvaluator:
    """Evaluates rules against records and partitions into valid vs quarantined records."""

    def __init__(
        self,
        rules: Optional[List[QualityRule]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        self.rules = rules or CASE_QUALITY_RULES
        self.context = context or {}

    def evaluate(
        self,
        df: pd.DataFrame,
        run_id: str,
        source_name: str,
    ) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
        """
        Evaluates rules row by row.
        Returns:
            - valid_df: DataFrame containing only rows passing all critical rules.
            - rejected_records: List of quarantined records with full failure metadata.
        """
        valid_indices: List[Any] = []
        rejected_records: List[Dict[str, Any]] = []

        now_str = datetime.now(timezone.utc).isoformat()

        for idx, row in df.iterrows():
            row_failed = False
            for rule in self.rules:
                passed, reason = rule.evaluator(row, self.context)
                if not passed:
                    if rule.failure_behavior == FailureBehavior.QUARANTINE:
                        row_failed = True
                        rejected_records.append({
                            "original_record": row.to_dict(),
                            "source": source_name,
                            "run_id": run_id,
                            "rule_id": rule.rule_id,
                            "rule_description": rule.description,
                            "reason": reason,
                            "severity": rule.severity.value,
                            "rejected_at": now_str,
                        })
                        # Once quarantined by a critical rule, avoid duplicate re-quarantine of same row
                        break
            if not row_failed:
                valid_indices.append(idx)

        valid_df = df.loc[valid_indices].copy()
        return valid_df, rejected_records
