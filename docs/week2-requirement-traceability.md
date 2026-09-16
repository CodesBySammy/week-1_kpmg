# Week 2 Requirement Traceability Matrix (RTM)

**Curriculum Source:** *Fresher AI Training_Curriculam_Sep2026.pdf (Week 2: Enterprise Data Pipelines)*  
**System Target:** Enterprise Data Pipeline extending Week 1 Case Management Backend  
**Status Target:** Complete Verification with Execution Evidence  

---

## 1. Technical Topics Traceability Matrix

| # | Curriculum Requirement | Learning Material | Code / Artifact Location | Test / Verification Evidence | Status |
|---|---|---|---|---|:---:|
| 1 | **CSV Ingestion** | `learning/week2/03-csv-ingestion.md` | `pipeline/sources/csv_source.py` | `tests/pipeline/test_sources.py::test_csv_ingestion` | 🟢 Planned / Active |
| 2 | **JSON Ingestion** | `learning/week2/04-json-ingestion.md` | `pipeline/sources/json_source.py` | `tests/pipeline/test_sources.py::test_json_ingestion` | 🟢 Planned / Active |
| 3 | **Parquet Ingestion** | `learning/week2/05-parquet-ingestion.md` | `pipeline/sources/parquet_source.py` | `tests/pipeline/test_sources.py::test_parquet_ingestion` | 🟢 Planned / Active |
| 4 | **Relational Ingestion** | `learning/week2/06-relational-ingestion.md` | `pipeline/sources/database_source.py` | `tests/pipeline/test_sources.py::test_relational_ingestion` | 🟢 Planned / Active |
| 5 | **REST API Ingestion** | `learning/week2/07-rest-api-ingestion.md` | `pipeline/sources/api_source.py`, `app/api/routes/mock_api.py` | `tests/pipeline/test_sources.py::test_api_ingestion` | 🟢 Planned / Active |
| 6 | **Data Profiling: Completeness** | `learning/week2/09-completeness.md` | `pipeline/profiling/profiler.py` | `tests/pipeline/test_profiler.py::test_completeness_metrics` | 🟢 Planned / Active |
| 7 | **Data Profiling: Uniqueness** | `learning/week2/10-uniqueness.md` | `pipeline/profiling/profiler.py` | `tests/pipeline/test_profiler.py::test_uniqueness_metrics` | 🟢 Planned / Active |
| 8 | **Data Profiling: Validity** | `learning/week2/11-validity.md` | `pipeline/profiling/profiler.py` | `tests/pipeline/test_profiler.py::test_validity_metrics` | 🟢 Planned / Active |
| 9 | **Data Profiling: Distribution** | `learning/week2/12-distribution.md` | `pipeline/profiling/profiler.py` | `tests/pipeline/test_profiler.py::test_distribution_metrics` | 🟢 Planned / Active |
| 10 | **Data Profiling: Referential Integrity** | `learning/week2/13-referential-integrity.md` | `pipeline/profiling/profiler.py` | `tests/pipeline/test_profiler.py::test_referential_integrity` | 🟢 Planned / Active |
| 11 | **Pandas DataFrame Operations** | `learning/week2/14-pandas-dataframes.md` | `pipeline/transformations/` | `tests/pipeline/test_transformations.py` | 🟢 Planned / Active |
| 12 | **PySpark DataFrame Operations** | `learning/week2/15-pyspark-dataframes.md` | `pipeline/transformations/pyspark_lab.py` | `learning/week2/labs/lab-09-pyspark.md` | 🟢 Planned / Active |
| 13 | **Filtering Operations** | `learning/week2/16-filtering.md` | `pipeline/transformations/standardization.py` | `tests/pipeline/test_transformations.py::test_filter_cases` | 🟢 Planned / Active |
| 14 | **Join Operations** | `learning/week2/17-joins.md` | `pipeline/transformations/joins.py` | `tests/pipeline/test_transformations.py::test_join_reference_and_policy` | 🟢 Planned / Active |
| 15 | **Aggregation Operations** | `learning/week2/18-aggregation.md` | `pipeline/transformations/aggregation.py` | `tests/pipeline/test_transformations.py::test_aggregate_metrics` | 🟢 Planned / Active |
| 16 | **Window Operations** | `learning/week2/19-window-operations.md` | `pipeline/transformations/windowing.py` | `tests/pipeline/test_transformations.py::test_window_ranking` | 🟢 Planned / Active |
| 17 | **Deduplication Operations** | `learning/week2/20-deduplication.md` | `pipeline/transformations/deduplication.py` | `tests/pipeline/test_transformations.py::test_deduplicate_cases` | 🟢 Planned / Active |
| 18 | **Null Handling** | `learning/week2/21-null-handling.md` | `pipeline/transformations/standardization.py` | `tests/pipeline/test_transformations.py::test_null_handling` | 🟢 Planned / Active |
| 19 | **Schema Definition** | `learning/week2/22-schema-definition.md` | `pipeline/schemas/` | `tests/pipeline/test_validation.py::test_schema_definition` | 🟢 Planned / Active |
| 20 | **Schema Validation** | `learning/week2/23-schema-validation.md` | `pipeline/validation/schema_validator.py` | `tests/pipeline/test_validation.py::test_schema_validation` | 🟢 Planned / Active |
| 21 | **Schema Evolution** | `learning/week2/24-schema-evolution.md` | `docs/week2/schema-and-data-contracts.md` | `tests/pipeline/test_validation.py::test_schema_evolution_backwards_compatible` | 🟢 Planned / Active |
| 22 | **Data Contracts** | `learning/week2/25-data-contracts.md` | `docs/data-contracts.md`, `pipeline/schemas/contracts.py` | `tests/pipeline/test_validation.py::test_data_contract_enforcement` | 🟢 Planned / Active |
| 23 | **Raw Layer Design** | `learning/week2/26-raw-standardized-curated.md` | `pipeline/layers/raw.py`, `data/raw/` | `tests/pipeline/test_layers.py::test_raw_layer_persistence` | 🟢 Planned / Active |
| 24 | **Standardized Layer Design** | `learning/week2/26-raw-standardized-curated.md` | `pipeline/layers/standardized.py`, `data/standardized/` | `tests/pipeline/test_layers.py::test_standardized_layer_persistence` | 🟢 Planned / Active |
| 25 | **Curated Layer Design** | `learning/week2/26-raw-standardized-curated.md` | `pipeline/layers/curated.py`, `data/curated/` | `tests/pipeline/test_layers.py::test_curated_layer_persistence` | 🟢 Planned / Active |
| 26 | **Data-Quality Rules** | `learning/week2/27-data-quality-rules.md` | `pipeline/validation/quality_rules.py` | `tests/pipeline/test_quality.py::test_quality_rules_evaluation` | 🟢 Planned / Active |
| 27 | **Rejected-Record Quarantine** | `learning/week2/28-rejected-records.md` | `pipeline/quarantine/quarantine_manager.py`, `data/rejected/` | `tests/pipeline/test_quarantine.py::test_quarantine_bad_records` | 🟢 Planned / Active |
| 28 | **Source-to-Target Reconciliation** | `learning/week2/29-reconciliation.md` | `pipeline/reconciliation/reconciler.py`, `reports/reconciliation/` | `tests/pipeline/test_reconciliation.py::test_reconciliation_pass` | 🟢 Planned / Active |
| 29 | **Incremental Loads** | `learning/week2/30-incremental-loads.md` | `pipeline/orchestration/incremental.py` | `tests/pipeline/test_orchestration.py::test_incremental_load` | 🟢 Planned / Active |
| 30 | **Idempotent Processing** | `learning/week2/31-idempotency.md` | `pipeline/orchestration/pipeline.py` | `tests/pipeline/test_orchestration.py::test_idempotent_rerun` | 🟢 Planned / Active |
| 31 | **Audit Metadata / Manifest** | `learning/week2/32-audit-metadata.md` | `pipeline/audit/audit_manager.py`, `audit/` | `tests/pipeline/test_audit.py::test_audit_manifest_generation` | 🟢 Planned / Active |
| 32 | **Repeatable Reruns** | `learning/week2/33-reruns.md` | `pipeline/cli.py` (`--run-id`, `--rerun`) | `tests/pipeline/test_orchestration.py::test_rerun_capability` | 🟢 Planned / Active |
| 33 | **Dockerfile Containerization** | `learning/week2/34-docker-containerization.md` | `Dockerfile`, `.dockerignore` | `docs/week2/docker-execution.md` | 🟢 Planned / Active |
| 34 | **Environment Configuration** | `learning/week2/35-environment-configuration.md` | `pipeline/config.py`, `.env.example` | `tests/pipeline/test_config.py` | 🟢 Planned / Active |
| 35 | **Pipeline Debugging Methodology** | `learning/week2/36-pipeline-debugging.md` | `docs/week2/debugging-guide.md` | 7 Failure Scenario Lab Walkthroughs | 🟢 Planned / Active |

---

## 2. Practical Outcomes Traceability

| Outcome | Description | Verification Method | Status |
|---|---|---|:---:|
| **Outcome 1** | Profile unfamiliar datasets and identify structural and quality issues | Profiler generates machine-readable JSON & human-readable Markdown profiling reports | 🟢 In Progress |
| **Outcome 2** | Implement schema-driven ingestion for file and API sources | Typed Pydantic & Arrow schema enforcement across CSV, JSON, Parquet, SQLite, REST API | 🟢 In Progress |
| **Outcome 3** | Develop reusable transformations using Pandas/PySpark DataFrames | Modular functions for standardizing, joining, ranking, and aggregating case records | 🟢 In Progress |
| **Outcome 4** | Apply automated quality, reconciliation, and exception-handling controls | Automated rule evaluation, quarantine dumping, and source-to-target mathematical count validation | 🟢 In Progress |
| **Outcome 5** | Preserve processing metadata for traceability and reruns | Execution manifests stored with batch IDs, run parameters, row counts, and error digests | 🟢 In Progress |
| **Outcome 6** | Package pipeline for consistent execution across environments | Production `Dockerfile` and CLI runner with environment overrides | 🟢 In Progress |

---

## 3. Formal Technical Deliverables Verification Check

- [ ] File and API ingestion components (`pipeline/sources/`)
- [ ] Declared source and target schemas/data contracts (`pipeline/schemas/`, `docs/data-contracts.md`)
- [ ] Raw, standardized and curated datasets/tables (`data/raw/`, `data/standardized/`, `data/curated/`)
- [ ] Transformation pipeline with reusable functions (`pipeline/transformations/`)
- [ ] Data-quality results & profiling report (`reports/profiling/`, `reports/data_quality/`)
- [ ] Rejected-record output with quarantine metadata (`data/rejected/`)
- [ ] Reconciliation report (`reports/reconciliation/`)
- [ ] Run manifest/audit log with batch metadata (`audit/`)
- [ ] Dockerfile and environment configuration (`Dockerfile`, `.dockerignore`, `.env.example`)
- [ ] Complete Week 2 learning modules (37 files) & 20 hands-on labs
