# Incident Report: INC-01 - Ingestion Data Failure

## 1. Symptom & Description
During raw batch ingestion into the Bronze/Silver lakehouse pipeline, incoming CSV/JSON records contained corrupted rows: missing mandatory `client_id`, null `created_at` timestamps, and negative `transaction_amount` values. Without hardening, these corrupted rows could trigger unhandled Pydantic validation exceptions or corrupt downstream analytics.

## 2. Expected Behavior
- The pipeline must validate each record against `SOURCE_CASE_SCHEMA`.
- Invalid rows must be intercepted before transformation.
- Corrupted records must be diverted to the `quarantine` zone with structured failure reasons (`MISSING_MANDATORY_FIELD`, `INVALID_DATA_TYPE`).
- The pipeline execution must complete successfully for all valid records without data loss.

## 3. Reproduction & Automated Test
Executed via `tests/failure-scenarios/test_failure_scenarios.py::test_data_failure_quarantine_malformed_case`.

```python
def test_data_failure_quarantine_malformed_case():
    corrupted_data = {"title": "Missing client and negative amount", "amount": -500.0}
    # Ingestion validator routes record to quarantine
    result = quarantine_service.process_record(corrupted_data)
    assert result.is_quarantined is True
    assert "client_id" in result.validation_errors
```

## 4. Root Cause Analysis
External batch feeds lacked upstream schema validation before dropping files into the ingest bucket. The ingestion worker was assuming schema conformance.

## 5. Remediation & Hardening
- Implemented strict pre-transformation schema checks in `pipeline/validation.py`.
- Automated quarantine routing with partition by date and failure reason in `pipeline/quarantine.py`.
- Added Prometheus counter `pipeline_quarantined_records_total`.
