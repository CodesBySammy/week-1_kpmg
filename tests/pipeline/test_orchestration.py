"""
Integration & End-to-End Tests for CaseManagementPipeline Orchestrator
"""

from pathlib import Path
import pandas as pd
import pytest

from pipeline.config import PipelineSettings
from pipeline.orchestration.pipeline import CaseManagementPipeline


@pytest.fixture
def test_pipeline(tmp_path: Path):
    """Creates an isolated pipeline environment with temporary output directories."""
    # Create an isolated settings instance
    custom_settings = PipelineSettings(
        app_env="test",
        base_dir=tmp_path,
        data_dir=tmp_path / "data",
        input_dir=Path("data/input"),  # Use real input files
        raw_dir=tmp_path / "data" / "raw",
        standardized_dir=tmp_path / "data" / "standardized",
        curated_dir=tmp_path / "data" / "curated",
        rejected_dir=tmp_path / "data" / "rejected",
        reports_dir=tmp_path / "reports",
        profiling_dir=tmp_path / "reports" / "profiling",
        reconciliation_dir=tmp_path / "reports" / "reconciliation",
        audit_dir=tmp_path / "audit",
        watermark_file=tmp_path / "audit" / "watermark.json",
        database_url=f"sqlite:///{tmp_path}/test_orchestration.db",
        run_mode="full",
    )
    return CaseManagementPipeline(config=custom_settings)


def test_pipeline_full_run(test_pipeline: CaseManagementPipeline):
    summary = test_pipeline.run(mode="full", run_id="TEST_RUN_FULL")

    assert summary["run_id"] == "TEST_RUN_FULL"
    assert summary["reconciliation_status"] == "PASS"
    assert summary["source_count"] == 20
    assert summary["quarantined_count"] == 5
    assert summary["valid_count"] == 15
    assert summary["duplicates_removed"] == 1
    assert summary["curated_count"] == 14

    # Verify curated files exist
    curated_dir = test_pipeline.config.curated_dir
    parquet_files = list(curated_dir.glob("*.parquet"))
    csv_files = list(curated_dir.glob("*.csv"))
    assert len(parquet_files) > 0
    assert len(csv_files) > 0

    # Verify audit manifest and ledger exist
    audit_dir = test_pipeline.config.audit_dir
    assert (audit_dir / "manifest_TEST_RUN_FULL.json").exists()
    assert (audit_dir / "execution_ledger.jsonl").exists()


def test_pipeline_rerun_idempotency(test_pipeline: CaseManagementPipeline):
    # Run 1
    summary1 = test_pipeline.run(mode="full", run_id="TEST_RUN_IDEMP_1")
    count1 = summary1["curated_count"]

    # Run 2 (exact same input)
    summary2 = test_pipeline.run(mode="full", run_id="TEST_RUN_IDEMP_2")
    count2 = summary2["curated_count"]

    assert count1 == count2
    assert summary2["reconciliation_status"] == "PASS"


def test_pipeline_incremental_mode(test_pipeline: CaseManagementPipeline):
    # 1. First run establishes watermark
    summary1 = test_pipeline.run(mode="incremental", run_id="TEST_RUN_INC_1")
    assert summary1["reconciliation_status"] == "PASS"
    assert test_pipeline.watermark_tracker.get_watermark() is not None

    # 2. Immediate second run with no new data
    summary2 = test_pipeline.run(mode="incremental", run_id="TEST_RUN_INC_2")
    assert summary2["reconciliation_status"] == "PASS"
    assert summary2["source_count"] == 0
    assert summary2["curated_count"] == 0
