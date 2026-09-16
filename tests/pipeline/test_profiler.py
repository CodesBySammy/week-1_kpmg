"""
Unit Tests for Data Profiling Engine
"""

from pathlib import Path
import pandas as pd
import pytest

from pipeline.profiling.profiler import DataProfiler


@pytest.fixture
def sample_profiling_df() -> pd.DataFrame:
    return pd.DataFrame([
        {"case_id": "1", "title": "Crash", "status": "OPEN", "priority": "HIGH", "case_type": "BUG", "created_by": "1", "assigned_to": "2"},
        {"case_id": "2", "title": "Lag", "status": "IN_PROGRESS", "priority": "LOW", "case_type": "BUG", "created_by": "2", "assigned_to": "3"},
        {"case_id": "3", "title": "", "status": "INVALID_STATE", "priority": "CRITICAL", "case_type": "INQUIRY", "created_by": "1", "assigned_to": "999"},
        {"case_id": "3", "title": "Duplicate", "status": "OPEN", "priority": "MEDIUM", "case_type": "FEATURE_REQUEST", "created_by": "3", "assigned_to": ""},
    ])


def test_completeness_metrics(sample_profiling_df: pd.DataFrame):
    profiler = DataProfiler(dataset_name="test_cases")
    profile = profiler.profile_cases(sample_profiling_df, reference_user_ids=[1, 2, 3])

    completeness = profile["completeness"]
    # title has 1 empty string out of 4 rows -> 25% missing
    assert completeness["title"]["missing_count"] == 1
    assert completeness["title"]["missing_percentage"] == 25.0


def test_uniqueness_metrics(sample_profiling_df: pd.DataFrame):
    profiler = DataProfiler(dataset_name="test_cases")
    profile = profiler.profile_cases(sample_profiling_df, reference_user_ids=[1, 2, 3])

    uniqueness = profile["uniqueness"]["case_id"]
    # case_id "3" appears twice -> 3 unique, 1 duplicate
    assert uniqueness["unique_count"] == 3
    assert uniqueness["duplicate_count"] == 1


def test_validity_metrics(sample_profiling_df: pd.DataFrame):
    profiler = DataProfiler(dataset_name="test_cases")
    profile = profiler.profile_cases(sample_profiling_df, reference_user_ids=[1, 2, 3])

    validity = profile["validity"]
    # status has 1 invalid state "INVALID_STATE"
    assert validity["status"]["invalid_count"] == 1
    assert "INVALID_STATE" in validity["status"]["invalid_samples"]


def test_distribution_metrics(sample_profiling_df: pd.DataFrame):
    profiler = DataProfiler(dataset_name="test_cases")
    profile = profiler.profile_cases(sample_profiling_df, reference_user_ids=[1, 2, 3])

    distribution = profile["distribution"]
    assert distribution["case_type"]["BUG"] == 2
    assert distribution["case_type"]["INQUIRY"] == 1


def test_referential_integrity(sample_profiling_df: pd.DataFrame):
    profiler = DataProfiler(dataset_name="test_cases")
    # Reference users are [1, 2, 3]; row 3 has assigned_to = 999
    profile = profiler.profile_cases(sample_profiling_df, reference_user_ids=[1, 2, 3])

    ref_int = profile["referential_integrity"]
    assert ref_int["assigned_to"]["orphan_count"] == 1
    assert 999 in ref_int["assigned_to"]["orphan_samples"]


def test_profiler_save_reports(tmp_path: Path, sample_profiling_df: pd.DataFrame):
    profiler = DataProfiler(dataset_name="test_cases")
    profile = profiler.profile_cases(sample_profiling_df, reference_user_ids=[1, 2, 3])

    json_path, md_path = profiler.save_reports(
        profile_dict=profile,
        output_dir=tmp_path,
        run_id="TEST_RUN_001",
    )

    assert json_path.exists()
    assert md_path.exists()
    assert "Data Profiling Report" in md_path.read_text(encoding="utf-8")
