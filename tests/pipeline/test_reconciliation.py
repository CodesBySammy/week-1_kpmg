"""
Unit Tests for Source-to-Target Reconciliation Engine
"""

import json
from pathlib import Path
import pytest

from pipeline.reconciliation.reconciler import ReconciliationEngine


def test_reconciliation_pass():
    engine = ReconciliationEngine(reports_dir=Path("/tmp"))
    report = engine.reconcile(
        run_id="RUN_REC_01",
        source_name="cases.csv",
        source_count=100,
        quarantined_count=20,
        valid_count=80,
        duplicates_removed=5,
        curated_count=75,
    )

    assert report["overall_status"] == "PASS"
    assert report["balance_check"]["source_balanced"] is True
    assert report["balance_check"]["curated_balanced"] is True
    assert report["variance"]["source_variance"] == 0
    assert report["variance"]["curated_variance"] == 0


def test_reconciliation_fail_source_leak():
    engine = ReconciliationEngine(reports_dir=Path("/tmp"))
    # Ingested 100, but valid 70 + quarantined 20 = 90 (10 records mysteriously lost)
    report = engine.reconcile(
        run_id="RUN_REC_02",
        source_name="cases.csv",
        source_count=100,
        quarantined_count=20,
        valid_count=70,
        duplicates_removed=5,
        curated_count=65,
    )

    assert report["overall_status"] == "FAIL"
    assert report["balance_check"]["source_balanced"] is False
    assert report["variance"]["source_variance"] == 10


def test_reconciliation_fail_curated_mismatch():
    engine = ReconciliationEngine(reports_dir=Path("/tmp"))
    # Valid 80, duplicates 5 => expected curated 75, but curated is 70
    report = engine.reconcile(
        run_id="RUN_REC_03",
        source_name="cases.csv",
        source_count=100,
        quarantined_count=20,
        valid_count=80,
        duplicates_removed=5,
        curated_count=70,
    )

    assert report["overall_status"] == "FAIL"
    assert report["balance_check"]["curated_balanced"] is False
    assert report["variance"]["curated_variance"] == -5


def test_reconciliation_save_reports(tmp_path: Path):
    engine = ReconciliationEngine(reports_dir=tmp_path)
    report = engine.reconcile(
        run_id="RUN_REC_04",
        source_name="cases.csv",
        source_count=50,
        quarantined_count=10,
        valid_count=40,
        duplicates_removed=2,
        curated_count=38,
    )

    json_path, md_path = engine.save_reports(report, run_id="RUN_REC_04")

    assert json_path.exists()
    assert md_path.exists()

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["run_id"] == "RUN_REC_04"
    assert data["overall_status"] == "PASS"

    md_text = md_path.read_text(encoding="utf-8")
    assert "RUN_REC_04" in md_text
    assert "🟢 PASS" in md_text
