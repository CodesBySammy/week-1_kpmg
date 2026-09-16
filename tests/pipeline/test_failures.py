"""
Failure Recovery and Boundary Condition Tests for Enterprise Pipeline
"""

from pathlib import Path
import pandas as pd
import pytest

from pipeline.config import PipelineSettings
from pipeline.orchestration.pipeline import CaseManagementPipeline
from pipeline.sources.api_source import APISource
from pipeline.sources.csv_source import CSVSource
from pipeline.sources.parquet_source import ParquetSource


def test_missing_input_file_handling(tmp_path: Path):
    source = CSVSource(file_path=tmp_path / "does_not_exist.csv")
    with pytest.raises(FileNotFoundError):
        source.read()


def test_corrupted_parquet_handling(tmp_path: Path):
    corrupted_file = tmp_path / "bad.parquet"
    corrupted_file.write_bytes(b"NOT_A_VALID_PARQUET_FILE_CONTENT")

    source = ParquetSource(file_path=corrupted_file)
    with pytest.raises(Exception):
        source.read()


def test_api_source_unreachable_endpoint_uses_fallback():
    fallback_data = [{"policy_id": "FALLBACK-01", "target_resolution_hours": 24.0}]
    source = APISource(
        endpoint_url="http://127.0.0.1:59999/non_existent_api_endpoint",
        timeout_seconds=0.5,
        fallback_data=fallback_data,
    )

    df = source.read()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df.iloc[0]["policy_id"] == "FALLBACK-01"


def test_pipeline_execution_with_malformed_input(tmp_path: Path):
    # Test pipeline execution when given intentionally malformed cases
    malformed_csv = Path("data/test_inputs/malformed_cases.csv")
    assert malformed_csv.exists()

    custom_settings = PipelineSettings(
        app_env="test",
        base_dir=tmp_path,
        data_dir=tmp_path / "data",
        input_dir=Path("data/input"),
        raw_dir=tmp_path / "data" / "raw",
        standardized_dir=tmp_path / "data" / "standardized",
        curated_dir=tmp_path / "data" / "curated",
        rejected_dir=tmp_path / "data" / "rejected",
        reports_dir=tmp_path / "reports",
        profiling_dir=tmp_path / "reports" / "profiling",
        reconciliation_dir=tmp_path / "reports" / "reconciliation",
        audit_dir=tmp_path / "audit",
        watermark_file=tmp_path / "audit" / "watermark.json",
        database_url=f"sqlite:///{tmp_path}/test_malformed.db",
        run_mode="full",
    )

    pipeline = CaseManagementPipeline(config=custom_settings)
    summary = pipeline.run(cases_file=malformed_csv, run_id="TEST_MALFORMED")

    # In malformed_cases.csv, there are 10 rows: 8 invalid, 2 valid (1 of which is duplicate) -> 1 curated
    assert summary["reconciliation_status"] == "PASS"
    assert summary["source_count"] == 10
    assert summary["quarantined_count"] == 8
    assert summary["valid_count"] == 2
    assert summary["duplicates_removed"] == 1
    assert summary["curated_count"] == 1
