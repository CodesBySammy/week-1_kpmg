"""
Unit Tests for Data Contracts and Schema Validation
"""

import pandas as pd
import pytest

from pipeline.schemas.contracts import DataContract
from pipeline.validation.schema_validator import SchemaValidator


@pytest.fixture
def sample_case_contract():
    return DataContract(
        dataset_name="cases",
        version="1.0.0",
        required_columns=["case_id", "title", "status", "priority"],
        primary_keys=["case_id"],
        allowed_values={
            "status": ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"],
            "priority": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
        },
        nullable_columns=["description"],
        description="Core case contract",
    )


def test_contract_validation_success(sample_case_contract):
    df = pd.DataFrame([
        {"case_id": 1, "title": "Payment gateway latency", "status": "OPEN", "priority": "HIGH"},
        {"case_id": 2, "title": "Fix navbar alignment", "status": "RESOLVED", "priority": "LOW"},
    ])

    validator = SchemaValidator(contract=sample_case_contract)
    is_valid, violations = validator.validate(df)

    assert is_valid is True
    assert len(violations) == 0


def test_contract_validation_missing_required_column(sample_case_contract):
    df = pd.DataFrame([
        {"case_id": 1, "title": "Missing status column", "priority": "HIGH"}
    ])

    validator = SchemaValidator(contract=sample_case_contract)
    is_valid, violations = validator.validate(df)

    assert is_valid is False
    assert any("Missing required contract column: 'status'" in v for v in violations)


def test_contract_validation_null_primary_key(sample_case_contract):
    df = pd.DataFrame([
        {"case_id": 1, "title": "Valid case", "status": "OPEN", "priority": "HIGH"},
        {"case_id": None, "title": "Null PK case", "status": "OPEN", "priority": "LOW"},
    ])

    validator = SchemaValidator(contract=sample_case_contract)
    is_valid, violations = validator.validate(df)

    assert is_valid is False
    assert any("Primary key column 'case_id' contains null values" in v for v in violations)


def test_contract_validation_invalid_enum_values(sample_case_contract):
    df = pd.DataFrame([
        {"case_id": 1, "title": "Invalid enum case", "status": "UNKNOWN_STATUS", "priority": "URGENT"},
    ])

    validator = SchemaValidator(contract=sample_case_contract)
    is_valid, violations = validator.validate(df)

    assert is_valid is False
    assert any("violating allowed values" in v for v in violations)


def test_contract_validation_empty_string_in_non_nullable_column(sample_case_contract):
    df = pd.DataFrame([
        {"case_id": 1, "title": "   ", "status": "OPEN", "priority": "HIGH"},
    ])

    validator = SchemaValidator(contract=sample_case_contract)
    is_valid, violations = validator.validate(df)

    assert is_valid is False
    assert any("Non-nullable column 'title' contains 1 null/empty values" in v for v in violations)


def test_contract_schema_evolution_tolerance(sample_case_contract):
    # Backward-compatible schema evolution: upstream adds extra new column 'tags'
    df = pd.DataFrame([
        {"case_id": 1, "title": "Evolution case", "status": "OPEN", "priority": "HIGH", "tags": "billing,urgent"},
    ])

    validator = SchemaValidator(contract=sample_case_contract)
    is_valid, violations = validator.validate(df)

    # By design, extra additive columns do not break the contract
    assert is_valid is True
    assert len(violations) == 0
