# Week 1 + Week 2 Baseline Report

> **Generated:** 2026-09-23  
> **Purpose:** Establish baseline before Week 3 RAG implementation  
> **Baseline Test Results:** 68 passed, 88.76% coverage

---

## Existing Architecture

### Week 1: Transactional Backend (OLTP)
- **Framework:** FastAPI with async lifespan, Pydantic v2 validation
- **Database:** SQLite via SQLAlchemy ORM, 3NF normalized
- **Tables:** `users`, `cases`, `case_history`, `curated_cases`
- **API Routes:** `/api/v1/cases/*`, `/api/v1/users`, `/api/v1/mock-policies`, `/health`
- **Patterns:** Clean Architecture, FSM state machine, Repository pattern, Audit logging
- **Config:** `pydantic-settings` with `.env` file

### Week 2: Enterprise Data Pipeline (OLAP)
- **Architecture:** 10-stage Medallion pipeline (Bronze → Silver → Gold)
- **Ingestion:** 5 heterogeneous sources (CSV, JSON, Parquet, REST API, SQLite)
- **Quality:** 8-rule quality engine, dead-letter quarantine, schema contracts
- **Reconciliation:** Mathematical source-to-target verification
- **Orchestration:** Incremental watermarking, idempotent reruns, audit manifests
- **CLI:** `python -m pipeline.cli --mode full|incremental`

### Directory Structure
```
case-management-backend/
├── app/                    # Week 1 FastAPI backend
│   ├── api/routes/         # HTTP endpoints
│   ├── config.py           # Pydantic settings
│   ├── database/           # SQLAlchemy session
│   ├── exceptions/         # Custom exceptions + handlers
│   ├── models/             # ORM models
│   ├── repositories/       # Data access layer
│   ├── schemas/            # Pydantic DTOs
│   └── services/           # Business logic
├── pipeline/               # Week 2 data pipeline
│   ├── audit/              # Manifest generation
│   ├── cli.py              # Pipeline CLI
│   ├── config.py           # Pipeline settings
│   ├── layers/             # Bronze/Silver/Gold managers
│   ├── orchestration/      # Pipeline engine + watermarks
│   ├── profiling/          # Statistical profiler
│   ├── quarantine/         # DLQ manager
│   ├── reconciliation/     # Source-to-target verifier
│   ├── schemas/            # Data contracts
│   ├── sources/            # Heterogeneous readers
│   ├── transformations/    # Standardization, joins, windows
│   └── validation/         # Quality rules engine
├── tests/                  # Test suites
│   ├── conftest.py         # Shared fixtures
│   ├── api/                # 15 API integration tests
│   ├── unit/               # 15 domain unit tests
│   └── pipeline/           # 38 pipeline tests
├── data/                   # Data layers
│   ├── input/              # Source files
│   ├── raw/                # Bronze
│   ├── standardized/       # Silver
│   ├── curated/            # Gold
│   └── rejected/           # Quarantine
├── docs/                   # Documentation
├── learning/               # Learning materials
├── Dockerfile              # Container definition
└── pyproject.toml          # Project config
```

## Baseline Test Results

```
68 passed, 14 warnings in 20.96s
Total coverage: 88.76% (1326 statements, 149 missed)
```

### Week 1 Tests (30 tests)
| Test File | Tests | Coverage |
|-----------|-------|----------|
| `tests/api/test_cases_api.py` | 13 | cases.py: 100% |
| `tests/api/test_user_and_error_handlers.py` | 2 | handlers.py: 95% |
| `tests/unit/test_case_repository.py` | 7 | repository: 83% |
| `tests/unit/test_case_service.py` | 5 | service: 100% |
| `tests/unit/test_models_and_schemas.py` | 3 | models: 100% |

### Week 2 Tests (38 tests)
| Test File | Tests | Coverage |
|-----------|-------|----------|
| `tests/pipeline/test_failures.py` | 4 | Error handling |
| `tests/pipeline/test_orchestration.py` | 3 | Pipeline DAG: 99% |
| `tests/pipeline/test_profiler.py` | 4 | Profiler: 99% |
| `tests/pipeline/test_quarantine.py` | 4 | Quarantine: 100% |
| `tests/pipeline/test_reconciliation.py` | 4 | Reconciler: 100% |
| `tests/pipeline/test_sources.py` | 5 | Source readers |
| `tests/pipeline/test_transformations.py` | 6 | Transforms: 100% |
| `tests/pipeline/test_validation.py` | 8 | Quality rules: 90% |

## Week 3 Integration Points

1. **New FastAPI route:** `POST /api/v1/policy-assistant/query` alongside existing case routes
2. **New `rag/` package:** Parallel to `app/` and `pipeline/`
3. **New `data/policies/` directory:** Policy corpus alongside existing data layers
4. **New `tests/rag/` directory:** RAG tests alongside existing test suites
5. **New `reports/rag/` directory:** Evaluation reports alongside existing reports
6. **Updated config:** New RAG environment variables in `.env.example`
7. **Updated `pyproject.toml`:** New RAG dependencies + `rag` package discovery

## Known Limitations
- SQLite is single-writer; production would use PostgreSQL
- No authentication/authorization (Week 4 scope)
- ResourceWarning for unclosed SQLite connections in pipeline tests (non-blocking)
