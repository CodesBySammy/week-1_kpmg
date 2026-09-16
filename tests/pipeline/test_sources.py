"""
Unit Tests for Heterogeneous Source Ingestion Components
"""

from pathlib import Path
import pandas as pd
import pytest

from pipeline.sources.api_source import APISource
from pipeline.sources.csv_source import CSVSource
from pipeline.sources.database_source import DatabaseSource
from pipeline.sources.json_source import JSONSource
from pipeline.sources.parquet_source import ParquetSource


def test_csv_ingestion(tmp_path: Path):
    test_csv = tmp_path / "test_cases.csv"
    test_csv.write_text("case_id,title,status\n1,Test Bug,OPEN\n2,Test Feature,RESOLVED\n", encoding="utf-8")

    source = CSVSource(file_path=test_csv)
    df = source.read()

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == ["case_id", "title", "status"]
    assert df.loc[0, "case_id"] == "1"


def test_csv_ingestion_file_not_found():
    source = CSVSource(file_path="non_existent_file.csv")
    with pytest.raises(FileNotFoundError):
        source.read()


def test_json_ingestion(tmp_path: Path):
    test_json = tmp_path / "test_reference.json"
    test_json.write_text('{"users": [{"user_id": 1, "tier": "L1"}, {"user_id": 2, "tier": "L2"}]}', encoding="utf-8")

    source = JSONSource(file_path=test_json, record_path="users")
    df = source.read()

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert "user_id" in df.columns
    assert df.loc[0, "tier"] == "L1"


def test_parquet_ingestion(tmp_path: Path):
    test_parquet = tmp_path / "test_policy.parquet"
    sample_df = pd.DataFrame([
        {"policy_id": "P1", "case_type": "BUG", "sla_hours": 4},
        {"policy_id": "P2", "case_type": "INQUIRY", "sla_hours": 24},
    ])
    sample_df.to_parquet(test_parquet, engine="pyarrow")

    source = ParquetSource(file_path=test_parquet)
    df = source.read()

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert df.loc[0, "policy_id"] == "P1"


def test_api_ingestion_with_fallback():
    fallback_records = [{"policy_id": "MOCK-01", "sla_hours": 12.0}]
    source = APISource(
        endpoint_url="http://invalid-unreachable-domain-123.org/api",
        fallback_data=fallback_records,
    )
    df = source.read()

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df.loc[0, "policy_id"] == "MOCK-01"


def test_database_source_ingestion(tmp_path: Path):
    db_file = tmp_path / "test_db.sqlite"
    db_url = f"sqlite:///{db_file}"

    # Setup dummy table
    from sqlalchemy import create_engine
    engine = create_engine(db_url)
    with engine.connect() as conn:
        conn.exec_driver_sql("CREATE TABLE test_table (id INT, name TEXT);")
        conn.exec_driver_sql("INSERT INTO test_table VALUES (10, 'Alpha'), (20, 'Beta');")
        conn.commit()

    source = DatabaseSource(connection_url=db_url, table_name="test_table")
    df = source.read()

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df["id"]) == [10, 20]
