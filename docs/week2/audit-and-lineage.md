# Audit Manifests, Execution Ledgers & Data Lineage

## 1. Overview & Architecture

The `AuditManager` (`pipeline/audit/audit_manager.py`) guarantees full regulatory compliance, data provenance, and non-repudiation by generating two distinct artifacts:
1. **Run Manifest (`manifest_<run_id>.json`)**: Complete execution snapshot.
2. **Execution Ledger (`execution_ledger.jsonl`)**: Continuous append-only operational log.

---

## 2. Run Manifest Schema (`manifest_<run_id>.json`)

```json
{
  "run_id": "RUN_20260916_120000",
  "batch_id": "BATCH_20260916_1200",
  "start_time": "2026-09-16T12:00:00.000000+00:00",
  "end_time": "2026-09-16T12:00:00.540000+00:00",
  "duration_seconds": 0.54,
  "status": "PASS",
  "error_message": null,
  "sources_ingested": [
    {"source": "cases_csv", "format": "CSV", "count": 20},
    {"source": "reference_json", "format": "JSON", "count": 13},
    {"source": "policy_parquet", "format": "PARQUET", "count": 9}
  ],
  "counts": {
    "source_count": 20,
    "quarantined_count": 5,
    "valid_count": 15,
    "duplicates_removed": 1,
    "curated_count": 14
  },
  "output_locations": {
    "raw_file": "data/raw/cases/ingest_date=2026-09-16/raw_cases.parquet",
    "standardized_file": "data/standardized/cases/std_cases.parquet",
    "curated_file": "data/curated/cases/curated_cases.parquet",
    "rejected_file": "data/rejected/rejected_RUN_20260916_120000.json",
    "reconciliation_report": "reports/reconciliation/reconciliation_RUN_20260916_120000.md"
  }
}
```

---

## 3. Data Lineage Tracking

By capturing source file paths, ingestion timestamps, transformation stages, and output locations in the run manifest, any record in `curated_cases.parquet` can be traced back to its raw bronze landing file and source CSV input.
