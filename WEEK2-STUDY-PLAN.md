# Week 2 Master Study Plan: Enterprise Data Pipelines

**Target Curriculum:** *Fresher AI Training_Curriculam_Sep2026.pdf (Week 2)*  
**Objective:** Build a repeatable enterprise data pipeline that ingests heterogeneous sources, enforces schemas, applies transformations and data-quality controls, and exposes curated data for downstream services.  
**Methodology:** `LEARN` $\rightarrow$ `PRACTICE` $\rightarrow$ `BUILD` $\rightarrow$ `TEST` $\rightarrow$ `DEBUG` $\rightarrow$ `DOCUMENT` $\rightarrow$ `REVIEW`  

---

## Study Track Overview

```text
Day 1: Ingestion & Profiling (CSV, JSON, Parquet, DB, REST API + Completeness/Uniqueness/Validity)
Day 2: Data Manipulation & Engine Mastery (Pandas DataFrames, PySpark Distributed Processing)
Day 3: Schemas, Data Contracts & Layered Data Design (Raw -> Standardized -> Curated)
Day 4: Quality Controls, Quarantine & Reconciliation (Validation Rules, Rejected Records, Audit Ledger)
Day 5: Enterprise Pipeline Engineering (Incremental Loads, Idempotency, Docker, Debugging & Capstone)
```

---

## Day 1: Heterogeneous Source Ingestion & Data Profiling

### 1. LEARN
- Read `learning/week2/01-data-pipeline-fundamentals.md` (ETL vs ELT, batch processing, data lineage).
- Read `learning/week2/02-heterogeneous-data-sources.md` through `07-rest-api-ingestion.md`.
- Read `learning/week2/08-data-profiling.md` through `13-referential-integrity.md`.

### 2. PRACTICE
- **Lab 1:** Inspect heterogeneous datasets in `data/input/`.
- **Lab 2:** Ingest raw CSV case records (`data/input/cases.csv`).
- **Lab 3:** Ingest JSON reference lookup data (`data/input/reference.json`).
- **Lab 4:** Ingest Parquet policy compliance metadata (`data/input/policy_metadata.parquet`).
- **Lab 5:** Ingest SQLite relational tables from Week 1.
- **Lab 6:** Ingest dynamic policy data from FastAPI mock endpoint (`GET /api/v1/mock/policies`).
- **Lab 7:** Run the data profiler to compute completeness, uniqueness, validity, distribution, and referential integrity.

### 3. BUILD
- Implement `pipeline/sources/` reader modules.
- Implement `pipeline/profiling/profiler.py` and output reports to `reports/profiling/`.

### 4. TEST
- Run `pytest tests/pipeline/test_sources.py` and `pytest tests/pipeline/test_profiler.py`.

---

## Day 2: Data Transformation Mastery (Pandas & PySpark)

### 1. LEARN
- Read `learning/week2/14-pandas-dataframes.md` (Pandas vectorized operations, indexing, memory).
- Read `learning/week2/15-pyspark-dataframes.md` (Distributed computation, RDDs, Catalyst optimizer, lazy evaluation).
- Read `learning/week2/16-filtering.md` through `21-null-handling.md` (Joins, aggregations, windows, deduplication).

### 2. PRACTICE
- **Lab 8:** Pandas transformations on real case records.
- **Lab 9:** PySpark DataFrame operations on case management datasets.
- **Lab 10:** Multi-column deduplication with priority tie-breakers.
- **Lab 11:** Window ranking operations (computing case resolution SLA percentiles).

### 3. BUILD
- Implement `pipeline/transformations/standardization.py`, `joins.py`, `deduplication.py`, `windowing.py`, and `aggregation.py`.

### 4. TEST
- Run `pytest tests/pipeline/test_transformations.py`.

---

## Day 3: Schemas, Data Contracts & Layered Architecture

### 1. LEARN
- Read `learning/week2/22-schema-definition.md` through `25-data-contracts.md`.
- Read `learning/week2/26-raw-standardized-curated.md` (Medallion architecture: Bronze/Raw $\rightarrow$ Silver/Standardized $\rightarrow$ Gold/Curated).

### 2. PRACTICE
- **Lab 12:** Raw/Standardized/Curated layered data flow.
- **Lab 13:** Schema validation and contract violation handling.

### 3. BUILD
- Implement `pipeline/schemas/` and `pipeline/layers/raw.py`, `standardized.py`, and `curated.py`.
- Enforce schemas via `pipeline/validation/schema_validator.py`.

### 4. TEST
- Run `pytest tests/pipeline/test_layers.py` and `pytest tests/pipeline/test_validation.py`.

---

## Day 4: Quality Controls, Quarantine & Reconciliation

### 1. LEARN
- Read `learning/week2/27-data-quality-rules.md` (Rule definitions, severity, validation logic).
- Read `learning/week2/28-rejected-records.md` (Dead-letter queue / quarantine pattern).
- Read `learning/week2/29-reconciliation.md` (Source-to-target count balancing and mathematical reconciliation).

### 2. PRACTICE
- **Lab 14:** Rejected-record quarantine execution.
- **Lab 15:** Source-to-target mathematical count reconciliation.

### 3. BUILD
- Implement `pipeline/validation/quality_rules.py`.
- Implement `pipeline/quarantine/quarantine_manager.py` dumping to `data/rejected/`.
- Implement `pipeline/reconciliation/reconciler.py` outputting to `reports/reconciliation/`.

### 4. TEST
- Run `pytest tests/pipeline/test_quality.py`, `test_quarantine.py`, and `test_reconciliation.py`.

---

## Day 5: Enterprise Execution, Docker, Debugging & Review

### 1. LEARN
- Read `learning/week2/30-incremental-loads.md` (Watermarking, CDC, delta processing).
- Read `learning/week2/31-idempotency.md` (Safe reruns without duplicate records).
- Read `learning/week2/32-audit-metadata.md` through `35-environment-configuration.md`.
- Read `learning/week2/36-pipeline-debugging.md` (Systematic pipeline failure triage).

### 2. PRACTICE
- **Lab 16:** Incremental delta loading using watermarks.
- **Lab 17:** Idempotent rerun verification.
- **Lab 18:** Generating run manifests and inspecting audit metadata.
- **Lab 19:** Docker container build and containerized pipeline execution.
- **Lab 20:** Pipeline failure debugging across 7 seeded failure scenarios.

### 3. BUILD
- Implement `pipeline/orchestration/pipeline.py` and `pipeline/cli.py`.
- Create `Dockerfile` and `.dockerignore`.
- Implement `pipeline/audit/audit_manager.py`.

### 4. TEST & REVIEW
- Run full regression test suite (`pytest -v`).
- Execute all CLI commands in full and incremental modes.
- Complete `learning/week2/week2-self-assessment.md` and review `learning/week2/week2-interview-questions.md`.
