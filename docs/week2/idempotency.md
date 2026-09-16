# Idempotency & Rerun Capability Specification

## 1. Mathematical Guarantee

An execution is idempotent if:
$$\Large f(f(x)) = f(x)$$

Running the Case Management Data Pipeline multiple times on the same input dataset produces the exact same system state, identical record counts, and zero duplicate records in target stores.

---

## 2. Idempotent Storage Patterns

1. **Parquet Storage**: Curated Parquet files are written using atomic partition replacement (`mode="overwrite"`), preventing duplicate file parts.
2. **Relational Database**: Table `curated_cases` in `data/cases.db` uses `if_exists="replace"`, cleanly resetting the table on each full run.
3. **Audit Ledger**: While execution runs append telemetry entries to `execution_ledger.jsonl`, run manifests are keyed uniquely by `manifest_{run_id}.json`.

---

## 3. Automated Test Verification

In `tests/pipeline/test_orchestration.py`, `test_pipeline_rerun_idempotency` executes two consecutive full runs on the same input data, verifying that `count1 == count2 == 14` and both runs achieve `reconciliation_status == "PASS"`.
