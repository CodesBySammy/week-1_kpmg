# FDE Case Management System
### FDE Fresher Readiness Programme — 5-Week Technical Learning Plan
### Cumulative Build: Weeks 1–5 | Production-Ready

[![Tests](https://img.shields.io/badge/tests-221%20passed-brightgreen)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-90%25+-blue)](htmlcov/)
[![Python](https://img.shields.io/badge/python-3.14.7-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green)](https://fastapi.tiangolo.com/)

---

## Overview

This repository is the **cumulative deliverable** of the FDE Fresher Readiness Programme. It is a production-grade, AI-powered Case Management System built and extended across 5 weeks, starting from a simple CRUD API and evolving into a fully deployable, secure, observable, and AI-augmented platform.

> **Curriculum Source**: `Fresher AI Training_Curriculam_Sep2026.pdf`

---

## Quick Start

```bash
# 1. Clone the repository
cd case-management-backend

# 2. Activate virtual environment
.\venv\Scripts\activate        # Windows PowerShell
source venv/bin/activate       # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database and start server
python -m uvicorn app.main:app --reload --port 8000

# 5. Open the API documentation
# http://localhost:8000/docs
```

---

## Test Suite

```bash
# Run all 221 tests
.\venv\Scripts\python.exe -m pytest -q

# Run with coverage
.\venv\Scripts\python.exe -m pytest --cov=. --cov-report=html

# Run specific suites
pytest tests\failure-scenarios\     # Week 5 failure injection
pytest tests\security\              # Week 5 red-team tests
pytest tests\regression\            # Weeks 1-4 regression guard
pytest tests\negative\              # Negative/boundary tests
pytest tests\performance\           # Performance benchmarks
pytest tests\e2e\                   # End-to-end scope change tests
```

**Latest run**: `221 passed, 0 failed, 52 warnings`

---

## Repository Structure

```
case-management-backend/
│
├── app/                          # Core application (Week 1)
│   ├── main.py                   # FastAPI application entry point
│   ├── models/case.py            # SQLAlchemy ORM models (+ Week 5 escalation_tier)
│   ├── schemas/case.py           # Pydantic request/response schemas
│   ├── services/case_service.py  # Business logic layer
│   ├── repositories/             # Data access layer
│   └── database/session.py       # DB session + auto-migration
│
├── pipeline/                     # Data Pipeline System (Week 2)
│   ├── sources/                  # CSV, JSON, Parquet, API, DB sources
│   ├── layers/                   # Raw → Standardized → Curated
│   ├── validation/               # Schema validation & quality rules
│   ├── quarantine/               # Bad record isolation
│   ├── audit/                    # Audit trail management
│   └── orchestration/            # Incremental pipeline orchestrator
│
├── rag/                          # RAG System (Week 3)
│   ├── chunking/                 # Fixed-size & semantic chunkers
│   ├── embeddings/               # Dense hash + Sentence Transformer providers
│   ├── indexing/                 # BM25, Vector, Hybrid indexes
│   ├── retrieval/                # Retriever + Reranker
│   ├── context/                  # Context assembler
│   ├── generation/               # GroundedAnswerGenerator (no hallucination)
│   └── evaluation/               # RAG evaluation metrics
│
├── workflow/                     # Agentic Workflow System (Week 4)
│   ├── orchestrator.py           # WorkflowOrchestrator (state-driven)
│   ├── state.py                  # WorkflowState enum
│   ├── approval.py               # Human-in-the-loop ApprovalManager
│   ├── router.py                 # Intent-based tool routing
│   └── fallback.py               # Fallback and retry logic
│
├── tools/                        # AI Tool Integrations (Week 4)
│   ├── schemas.py                # Typed I/O contracts (Pydantic)
│   ├── retrieve_case.py          # TOOL 1: retrieve_case_details
│   └── update_ticket.py          # TOOL 2: update_ticket (HITL-gated)
│
├── security/                     # Security Layer (Week 4–5)
│   ├── auth.py                   # JWT token creation & verification
│   ├── rbac.py                   # Role-based access control (+ dept isolation)
│   └── guardrails.py             # Prompt injection detection & sanitization
│
├── tests/                        # Test Suite
│   ├── api/                      # API endpoint tests
│   ├── e2e/                      # End-to-end scope change escalation tests
│   ├── failure-scenarios/        # 8-category failure injection tests (Week 5)
│   ├── negative/                 # Negative-path and boundary tests (Week 5)
│   ├── performance/              # Latency & reliability benchmarks (Week 5)
│   ├── regression/               # Weeks 1-4 backward-compatibility guard (Week 5)
│   ├── security/                 # Red-team adversarial tests (Week 5)
│   ├── pipeline/                 # Pipeline unit tests
│   └── unit/                     # Unit tests for models, services, repos
│
└── docs/                         # Documentation
    ├── week1/                    # OLTP API design & learning
    ├── week2/                    # Data pipeline reference
    ├── week3/                    # RAG system documentation
    ├── week4/                    # Agentic workflow & tool docs
    └── week5/                    # Week 5 deliverables
        ├── DEFINITION_OF_DONE.md      # Master completion checklist
        ├── WEEK5_TRACEABILITY_MATRIX.md
        ├── architecture/
        │   └── WEEK5_ARCHITECTURE.md
        ├── backlog/
        │   └── WEEK5_BACKLOG.md
        ├── failures/
        │   └── FAILURE_SCENARIOS.md   # Incident response docs
        ├── security/
        │   └── RED_TEAM_REPORT.md     # Adversarial testing report
        └── testing/
            └── PERFORMANCE_BENCHMARKS.md
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT (API / AI Agent)                        │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  JWT Authentication  │ ← security/auth.py
                    │  RBAC Authorization  │ ← security/rbac.py
                    │  Prompt Injection    │ ← security/guardrails.py
                    │  Dept. Isolation     │
                    └──────────┬──────────┘
                               │
            ┌──────────────────▼──────────────────┐
            │         WorkflowOrchestrator          │ ← workflow/orchestrator.py
            │  Intent Detection → Tool Routing      │ ← workflow/router.py
            │  State Machine (11 states)            │ ← workflow/state.py
            │  Human Approval Gate (HITL)           │ ← workflow/approval.py
            │  Retry / Fallback                     │ ← workflow/fallback.py
            └──────┬───────────────────────┬────────┘
                   │                       │
       ┌───────────▼─────┐     ┌───────────▼────────────┐
       │  TOOL 1          │     │  TOOL 2                 │
       │  retrieve_case   │     │  update_ticket          │
       │  (read-only)     │     │  (approval required)    │
       └───────────┬──────┘     └───────────┬─────────────┘
                   │                        │
       ┌───────────▼──────────────────────────────────────┐
       │                  RAG System                        │
       │  Chunking → Embedding → Hybrid Index               │
       │  Retrieval → Rerank → Context Assembly             │
       │  GroundedAnswerGenerator (no-hallucination)        │
       └───────────────────────────────────────────────────┘
                               │
       ┌───────────────────────▼───────────────────────────┐
       │                  Core API (FastAPI)                 │
       │  Case CRUD · User Mgmt · Workflow API              │
       │  Observability · Health · Metrics                  │
       └───────────────────────────────────────────────────┘
                               │
       ┌───────────────────────▼───────────────────────────┐
       │              Data Pipeline System                   │
       │  Raw → Standardized → Curated                      │
       │  Validation · Quarantine · Reconciliation          │
       └───────────────────────────────────────────────────┘
                               │
                     ┌─────────▼────────┐
                     │  SQLite Database  │ ← (dev) / PostgreSQL (prod)
                     └──────────────────┘
```

---

## Week-by-Week Feature Summary

| Week | Theme | Key Deliverables |
|---|---|---|
| **Week 1** | OLTP API Design | FastAPI, SQLAlchemy, Pydantic, CRUD, structured logging |
| **Week 2** | Data Pipeline | Multi-source ETL, medallion layers, quarantine, audit |
| **Week 3** | RAG System | Chunking, embeddings, hybrid retrieval, grounded generation |
| **Week 4** | Agentic Workflow | Tool contracts, HITL approval, state machine, RBAC, JWT |
| **Week 5** | Production Readiness | Scope change, failure injection, red-team, performance, handover |

---

## Week 5 Scope Change: Escalation Tier & Department Isolation

A controlled mid-project scope change was introduced during Week 5 simulating a real client engagement:

- **New fields**: `escalation_tier` (STANDARD | PRIORITY | CRITICAL_ESC), `department`
- **Backward-compatible DB migration**: `ALTER TABLE` with `PRAGMA table_info` check
- **RBAC rule**: Only `supervisor`/`admin` roles can escalate to `CRITICAL_ESC`
- **Department isolation**: Agents restricted to their department; managers/admins have cross-department access
- **Verified by**: `tests/e2e/test_scope_change_escalation.py` (4 tests, all passing)

---

## Security Model

| Mechanism | Implementation |
|---|---|
| Authentication | HMAC-SHA256 JWT (no PyJWT dependency) |
| Authorization | Role-Based Access Control (viewer/agent/supervisor/manager/admin) |
| Department Isolation | `check_department_access()` in `security/rbac.py` |
| Prompt Injection | 8-pattern regex + `InputGuardrail.sanitize()` |
| HITL Gate | `ApprovalManager` with TTL-bound approval tokens |
| Idempotency | `IdempotencyStore` per-tool key caching |
| Audit Trail | Structured JSON logs + `audit_event_id` per write |

---

## Handover Package

The following documents are ready for the client/team handover:

| Document | Location |
|---|---|
| Definition of Done | `docs/week5/DEFINITION_OF_DONE.md` |
| Traceability Matrix | `docs/week5/WEEK5_TRACEABILITY_MATRIX.md` |
| Architecture | `docs/week5/architecture/WEEK5_ARCHITECTURE.md` |
| Backlog | `docs/week5/backlog/WEEK5_BACKLOG.md` |
| Scope Change Record | `docs/week5/SCOPE_CHANGE.md` |
| Failure Scenarios | `docs/week5/failures/FAILURE_SCENARIOS.md` |
| Red-Team Report | `docs/week5/security/RED_TEAM_REPORT.md` |
| Performance Benchmarks | `docs/week5/testing/PERFORMANCE_BENCHMARKS.md` |

---

## Contributing / Extending

1. **Adding a new tool**: Create `tools/my_tool.py`, add schemas to `tools/schemas.py`, register in `workflow/router.py`
2. **Adding a new role**: Add to `security/rbac.py::ROLE_PERMISSIONS`
3. **Adding a department**: No code change — `department` is a free-form string enforced at runtime
4. **Adding RAG documents**: Use `rag/ingestion/parser.py` + `rag/indexing/hybrid_index.py`
5. **Adding tests**: Follow the pattern in `tests/failure-scenarios/` or `tests/regression/`

---

## Known Limitations (Production Gaps)

| Gap | Priority | Mitigation Path |
|---|---|---|
| SQLite not suitable for production | HIGH | Replace with PostgreSQL via `DATABASE_URL` env var |
| In-memory idempotency store | HIGH | Replace with Redis |
| No rate limiting | MEDIUM | Add `slowapi` or API Gateway rate limiting |
| Secrets in code | HIGH | Move to Vault / AWS Secrets Manager |
| Audit logs in-memory | MEDIUM | Persist to append-only store (e.g., DynamoDB) |

---

## Curriculum Traceability

Every week's implementation is traced to the curriculum PDF:

- **Week 1** → `docs/week1/LEARNING_PLAN.md`
- **Week 2** → `docs/week2/LEARNING_PLAN.md`
- **Week 3** → `docs/week3/LEARNING_PLAN.md`
- **Week 4** → `docs/week4/LEARNING_PLAN.md`
- **Week 5** → `docs/week5/WEEK5_TRACEABILITY_MATRIX.md`

---

*Built by the FDE Fresher Cohort Sep-2026 | Reviewed by Senior AI Engineer*
