"""
Unit Tests for Data Quality Controls and Quarantine Handling
"""

import json
from pathlib import Path
import pandas as pd
import pytest

from pipeline.quarantine.quarantine_manager import QuarantineManager
from pipeline.validation.quality_rules import (
    CASE_QUALITY_RULES,
    QualityRulesEvaluator,
    check_positive_id,
    check_referential_creator,
    check_required_title,
    check_valid_status,
)


def test_individual_rule_evaluators():
    # Title rule
    passed, reason = check_required_title(pd.Series({"title": "Fix crash"}))
    assert passed is True
    passed, reason = check_required_title(pd.Series({"title": ""}))
    assert passed is False
    assert "null or empty" in reason

    # Status rule
    passed, reason = check_valid_status(pd.Series({"status": "OPEN"}))
    assert passed is True
    passed, reason = check_valid_status(pd.Series({"status": "PENDING_REVIEW"}))
    assert passed is False
    assert "not in allowed enum" in reason

    # Positive ID rule
    passed, reason = check_positive_id(pd.Series({"case_id": 15}))
    assert passed is True
    passed, reason = check_positive_id(pd.Series({"case_id": -5}))
    assert passed is False
    assert "positive integer" in reason

    # Referential integrity creator rule
    context = {"valid_user_ids": {1, 2, 3}}
    passed, reason = check_referential_creator(pd.Series({"created_by": 2}), context)
    assert passed is True
    passed, reason = check_referential_creator(pd.Series({"created_by": 99}), context)
    assert passed is False
    assert "does not exist in reference data" in reason


def test_quality_rules_evaluator_partitioning():
    df = pd.DataFrame([
        # Valid row
        {
            "case_id": 1,
            "title": "Valid Case",
            "status": "OPEN",
            "priority": "HIGH",
            "case_type": "BUG",
            "created_by": 1,
            "assigned_to": 2,
            "created_at": "2026-03-01T10:00:00Z",
        },
        # Invalid row: title empty
        {
            "case_id": 2,
            "title": "",
            "status": "OPEN",
            "priority": "LOW",
            "case_type": "BUG",
            "created_by": 1,
            "assigned_to": 2,
            "created_at": "2026-03-01T10:00:00Z",
        },
        # Invalid row: unknown status
        {
            "case_id": 3,
            "title": "Bad Status",
            "status": "UNKNOWN",
            "priority": "LOW",
            "case_type": "BUG",
            "created_by": 1,
            "assigned_to": 2,
            "created_at": "2026-03-01T10:00:00Z",
        },
    ])

    context = {"valid_user_ids": {1, 2}}
    evaluator = QualityRulesEvaluator(rules=CASE_QUALITY_RULES, context=context)

    valid_df, rejected = evaluator.evaluate(df, run_id="RUN_TEST_01", source_name="cases.csv")

    assert len(valid_df) == 1
    assert valid_df.iloc[0]["case_id"] == 1
    assert len(rejected) == 2
    assert rejected[0]["rule_id"] == "RULE-CASE-001"
    assert rejected[1]["rule_id"] == "RULE-CASE-002"


def test_quarantine_manager_persistence(tmp_path: Path):
    manager = QuarantineManager(quarantine_dir=tmp_path)

    rejected_records = [
        {
            "original_record": {"case_id": 999, "title": ""},
            "source": "cases.csv",
            "run_id": "RUN_TEST_02",
            "rule_id": "RULE-CASE-001",
            "reason": "Title is null or empty",
            "severity": "CRITICAL",
            "rejected_at": "2026-03-01T10:00:00Z",
        }
    ]

    out_file = manager.quarantine_records(
        rejected_records=rejected_records,
        run_id="RUN_TEST_02",
        batch_id="BATCH_01",
    )

    assert out_file.exists()
    assert manager.get_quarantined_count("RUN_TEST_02") == 1
    assert manager.get_quarantined_count("NON_EXISTENT") == 0

    with open(out_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["run_id"] == "RUN_TEST_02"
    assert data["total_quarantined"] == 1
    assert len(data["rejected_records"]) == 1
    assert data["rejected_records"][0]["rule_id"] == "RULE-CASE-001"
