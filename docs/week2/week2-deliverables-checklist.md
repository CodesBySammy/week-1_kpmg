# Week 2 Enterprise Data Pipeline Deliverables Checklist

This checklist tracks the delivery of all required components, documentation, learning modules, labs, tests, and configuration for Week 2.

---

## 1. Pipeline Code Deliverables (`pipeline/`)
- [x] `pipeline/config.py`: 12-Factor settings with environment variable support
- [x] `pipeline/sources/base_source.py`: Abstract source interface
- [x] `pipeline/sources/csv_source.py`: String-preserving CSV reader
- [x] `pipeline/sources/json_source.py`: Targeted path JSON reader
- [x] `pipeline/sources/parquet_source.py`: PyArrow columnar reader
- [x] `pipeline/sources/database_source.py`: Relational database extractor via SQLAlchemy
- [x] `pipeline/sources/api_source.py`: REST API reader with fallback cache
- [x] `pipeline/schemas/case_schema.py`: Case schemas across all data layers
- [x] `pipeline/schemas/reference_schema.py`: Reference user & department schemas
- [x] `pipeline/schemas/policy_schema.py`: SLA policy schema
- [x] `pipeline/schemas/contracts.py`: Declarative `DataContract` engine
- [x] `pipeline/profiling/profiler.py`: 5-pillar statistical profiler with MD/JSON export
- [x] `pipeline/validation/quality_rules.py`: 8 domain rules & `QualityRulesEvaluator`
- [x] `pipeline/validation/schema_validator.py`: Schema contract validator
- [x] `pipeline/quarantine/quarantine_manager.py`: Dead-letter quarantine sink
- [x] `pipeline/transformations/standardization.py`: Type coercion, UTC parsing, enum normalization
- [x] `pipeline/transformations/deduplication.py`: Deterministic PK deduplication
- [x] `pipeline/transformations/joins.py`: Relational enrichment & SLA calculation
- [x] `pipeline/transformations/windowing.py`: Dense duration rank & department sequence
- [x] `pipeline/transformations/aggregation.py`: Department SLA summaries & priority rollups
- [x] `pipeline/transformations/pyspark_lab.py`: Standalone PySpark case pipeline
- [x] `pipeline/layers/raw.py`: Bronze layer partition manager
- [x] `pipeline/layers/standardized.py`: Silver layer manager
- [x] `pipeline/layers/curated.py`: Gold layer multi-format manager (Parquet, CSV, SQL)
- [x] `pipeline/reconciliation/reconciler.py`: Source-to-target mathematical count balancer
- [x] `pipeline/audit/audit_manager.py`: Run manifests & JSONL execution ledger
- [x] `pipeline/orchestration/incremental.py`: WatermarkTracker for delta processing
- [x] `pipeline/orchestration/pipeline.py`: Master 10-stage CaseManagementPipeline
- [x] `pipeline/cli.py`: Production CLI runner (`python -m pipeline.cli`)

---

## 2. Test Suite Deliverables (`tests/pipeline/`)
- [x] `tests/pipeline/test_sources.py`: 6 tests passing
- [x] `tests/pipeline/test_profiler.py`: 6 tests passing
- [x] `tests/pipeline/test_transformations.py`: 6 tests passing
- [x] `tests/pipeline/test_validation.py`: 6 tests passing
- [x] `tests/pipeline/test_quarantine.py`: 3 tests passing
- [x] `tests/pipeline/test_reconciliation.py`: 4 tests passing
- [x] `tests/pipeline/test_orchestration.py`: 3 tests passing (full, incremental, idempotency)
- [x] `tests/pipeline/test_failures.py`: 4 tests passing (missing files, malformed input, API fallback, corrupted parquet)
- [x] Total Tests: **68 passed (30 Week 1 + 38 Week 2)**, 0 failures, 88.76% coverage

---

## 3. Curriculum & Learning Deliverables (`learning/week2/`)
- [x] 37 Topic Modules (`00-week2-overview.md` to `36-pipeline-debugging.md`)
- [x] 20 Hands-On Practical Labs in `learning/week2/labs/` (`lab-01` to `lab-20`)
- [x] `week2-interview-questions.md`: Top 50 enterprise interview questions with answers
- [x] `week2-self-assessment.md`: 30 questions (MCQ + system design)
- [x] `week2-self-assessment-answers.md`: Complete answer key and grading rubric

---

## 4. Containerization & Documentation (`docs/`)
- [x] `Dockerfile`: Multi-stage, non-root user `appuser`
- [x] `.dockerignore`: Excluded caches, DBs, and temp files
- [x] `docs/data-contracts.md`
- [x] `docs/data-layer-design.md`
- [x] `docs/performance-and-scalability.md`
- [x] `docs/week2/` (17 architectural, operational, and verification guides)
