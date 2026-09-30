# Enterprise Case Management Platform (Weeks 1–5 FDE Capstone)

[![Tests](https://img.shields.io/badge/tests-221%20passed-brightgreen)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-90%25+-blue)](htmlcov/)
[![Python](https://img.shields.io/badge/python-3.14.7-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green)](https://fastapi.tiangolo.com/)
[![Release](https://img.shields.io/badge/release-v1.0.0--rc1-orange)](release/)

---

# Project Overview
The Enterprise Case Management Platform is the cumulative capstone deliverable of the 5-Week Forward Deployed Engineering (FDE) Fresher Readiness Program. Designed for tier-1 financial and regulatory compliance institutions, this solution integrates relational OLTP case tracking, an automated lakehouse medallion ingestion pipeline, a grounded hallucination-free Retrieval-Augmented Generation (RAG) subsystem, and a stateful, human-in-the-loop agentic workflow orchestrator into a production-grade, hardened, deployable application.

# Business Problem
Financial compliance teams and investigators handle thousands of high-stakes investigations (anti-money laundering, fraud, sanction breaches, customer complaints) trapped in fragmented legacy systems and raw unstructured document archives. Manual triage introduces:
1. Significant latency and regulatory reporting SLA breaches.
2. Inconsistent policy interpretations and compliance non-adherence.
3. Severe operational risks when AI or automation executes unapproved, consequential modifications.
4. Total lack of cross-layer forensic auditability connecting user queries, AI suggestions, human approvals, and database writes.

# Solution
An integrated, secure, and observable Case Management Platform operating under the core engineering principle: **"The Model May Propose, but Deterministic Application Code Must Decide."**
- Ingests structured and unstructured case history through an automated medallion lakehouse pipeline.
- Provides strict grounded RAG policy search with bracketed citations and verifiable non-hallucination.
- Orchestrates multi-step investigations via stateful agentic workflows.
- Gates consequential case lifecycle actions behind HMAC-SHA256 cryptographic human approval tokens.
- Enforces strict role-based access control (RBAC), multi-tenant department data isolation, and prompt injection defense.

# Features
- **Deterministic Case Lifecycle**: Full CRUD operations with state transitions (`OPEN`, `INVESTIGATING`, `PENDING_APPROVAL`, `RESOLVED`, `CLOSED`).
- **Medallion Data Lakehouse**: Bronze (raw CSV/JSON), Silver (cleansed Parquet), and Gold (reconciled aggregates) with automated quarantine of corrupted records.
- **Hybrid Grounded RAG**: Dense vector + sparse BM25 retrieval, cross-score reranking, strict token budgeting, and out-of-domain refusals.
- **Agentic Tool Registry**: Pydantic typed contracts for `retrieve_case` and `update_ticket`.
- **Human-in-the-Loop (HITL)**: Cryptographic Two-Man Rule enforcement for state changes and high-tier escalations.
- **Adversarial Security**: Pre-execution regex guardrails, department isolation, and zero-trust parameter validation.
- **Full Distributed Tracing**: Unified `correlation_id` propagating across API, middleware, tools, database, and OpenTelemetry spans.

# Architecture
The platform follows a clean, decoupled layered architecture:
```text
┌─────────────────────────────────────────────────────────────────┐
│                    API CONSUMER / CLIENT APP                    │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTP / REST + Bearer JWT + X-Correlation-ID
                    ┌──────────▼──────────┐
                    │  Correlation MW     │ ← ASGI Request Tracing
                    │  JWT & RBAC Guard   │ ← security/auth.py, rbac.py
                    │  Prompt Guardrails  │ ← security/guardrails.py
                    └──────────┬──────────┘
                               │
             ┌─────────────────▼──────────────────┐
             │         Workflow Orchestrator       │ ← workflow/orchestrator.py
             │  Intent Detection → State Machine   │ ← workflow/state.py
             │  Human Approval Token Verification  │ ← workflow/approval.py
             │  Fault Fallback & Circuit Breaking  │ ← workflow/fallback.py
             └──────┬───────────────────────┬──────┘
                    │                       │
        ┌───────────▼─────┐     ┌───────────▼────────────┐
        │  read_tool      │     │  write_tool            │
        │  retrieve_case  │     │  update_ticket (HITL)  │
        └───────────┬─────┘     └───────────┬────────────┘
                    │                       │
        ┌───────────▼───────────────────────▼─────────────┐
        │                  RAG Subsystem                  │
        │  Chunking → Dense + BM25 Search → Rerank        │
        │  Grounded Generation (with verified citations)  │
        └───────────────────────┬─────────────────────────┘
                                │
        ┌───────────────────────▼─────────────────────────┐
        │             Data & Persistence Layer            │
        │  SQLAlchemy ORM · Case & Audit Tables · Parquet │
        └─────────────────────────────────────────────────┘
```

# Week 1 — Foundation
Established the robust OLTP relational backend:
- FastAPI gateway with OpenAPI contract generation.
- SQLAlchemy 2.0 ORM data layer with SQLite/PostgreSQL compatibility.
- Comprehensive Pydantic v2 domain schemas (`CaseCreate`, `CaseUpdate`, `CaseResponse`).
- Repository pattern isolating persistence from domain service logic.
- RFC 7807 structured problem details for client errors.

# Week 2 — Data Engineering
Constructed the enterprise lakehouse medallion pipeline:
- Bronze raw ingestion accommodating CSV, JSON, and external batch data.
- Silver layer schema enforcement, date standardization, and deduplication into Apache Parquet.
- Automated quarantine engine routing corrupted records with failure reason metadata.
- Financial reconciliation engine ensuring ledger parity.
- Data profiling metrics and pipeline execution audits.

# Week 3 — RAG
Implemented the Grounded Knowledge & Retrieval-Augmented Generation system:
- Fixed-size token-budgeted chunking with overlap control.
- Dense vector hashing and sparse Rank-BM25 hybrid retrieval.
- Cross-score reciprocal reranking to maximize retrieval precision.
- Token-budgeted context assembly preventing prompt truncation.
- `GroundedAnswerGenerator` providing 100% citation compliance and deterministic policy refusal on empty context.

# Week 4 — Controlled AI Workflow
Engineered the deterministic agentic orchestration layer:
- Stateful LangGraph-style state machine (11 explicit lifecycle states).
- Intent classification routing queries between policy search and case tools.
- Strict Pydantic I/O contracts for tools (`retrieve_case`, `update_ticket`).
- Cryptographic `ApprovalManager` implementing HMAC-SHA256 Two-Man Rule.
- Full OpenTelemetry tracing and correlation ID propagation.

# Week 5 — Integration, Hardening & Handover
Unified the cumulative platform and achieved production readiness:
- **Client Engagement Simulation**: Technical discovery, current-state analysis, and structured requirements engineering.
- **Controlled Scope Change**: Added `escalation_tier` (`STANDARD`, `PRIORITY`, `CRITICAL_ESC`) and `department` isolation with backward-compatible migrations.
- **Failure Hardening**: Seeded and mitigated 8 cross-layer incident scenarios (data, API, RAG, tool, auth, model, workflow, deployment).
- **Red-Team Security**: 16 automated adversarial penetration tests verifying prompt injection and access leakage mitigation.
- **Handover Package**: 12 operational guides, 29 learning modules, 10 labs, and support runbooks for client engineering teams.

# Complete End-to-End Flow
1. **Client Request**: Client submits an authenticated query (e.g., `"Escalate CASE-101 to CRITICAL_ESC"`).
2. **Gateway**: `CorrelationIdMiddleware` assigns a UUID4; JWT authenticator validates signature and extracts `UserPrincipal`.
3. **Guardrails**: `detect_prompt_injection` verifies the prompt contains no adversarial instruction hijacking.
4. **Intent Detection**: The router classifies intent as `TOOL_PROPOSAL: update_ticket`.
5. **Approval Interception**: Consequential action triggers state `APPROVAL_REQUIRED`; execution halts and emits pending approval request.
6. **Supervisor Action**: Supervisor reviews request and grants approval; server issues cryptographic HMAC token.
7. **Execution**: Request resubmitted with approval token; tool validates signature and supervisor role, applies mutation to DB.
8. **Audit & Response**: Immutable record saved in `audit_logs`, trace flushed to OpenTelemetry, client receives HTTP 200 with correlation ID.

# Technology Stack
- **Language & Runtime**: Python 3.14.7 (win32)
- **Web Gateway**: FastAPI 0.115+, Starlette, Uvicorn
- **Data Validation & Schemas**: Pydantic v2
- **Persistence & ORM**: SQLAlchemy 2.0, Alembic, SQLite (dev) / PostgreSQL (prod)
- **Data Lakehouse**: PyArrow, Apache Parquet, Pandas
- **RAG & Search**: Rank-BM25, Custom Vector Index, Dense Hash Embeddings
- **Security**: Stateless HMAC-SHA256 JWT, Cryptographic Approval Tokens, Regex Guardrails
- **Observability**: OpenTelemetry SDK, Structlog, Prometheus Client
- **Testing**: PyTest 9.1+, AnyIO, HTTPX, Coverage.py

# Repository Structure
```text
case-management-backend/
├── app/                          # Core Application (Week 1)
│   ├── api/                      # REST endpoints & dependency injection
│   ├── models/                   # SQLAlchemy models (Case, User, AuditLog)
│   ├── schemas/                  # Pydantic request/response schemas
│   ├── services/                 # Business domain services
│   └── database/                 # Database engine & migrations
├── pipeline/                     # Lakehouse Data Pipeline (Week 2)
│   ├── sources/                  # CSV, JSON, Parquet batch connectors
│   ├── validation/               # Schema verification & quarantine routing
│   └── quarantine/               # Corrupted record isolation
├── rag/                          # Grounded RAG Subsystem (Week 3)
│   ├── chunking/                 # Token-budgeted text splitting
│   ├── indexing/                 # Dense hash & sparse BM25 indices
│   ├── retrieval/                # Hybrid retriever & cross-score reranker
│   └── generation/               # Grounded answer generator with citations
├── workflow/                     # Controlled Agentic Engine (Week 4)
│   ├── orchestrator.py           # Stateful workflow coordinator
│   ├── state.py                  # Workflow state machine enum
│   ├── approval.py               # HMAC-SHA256 human approval manager
│   └── router.py                 # Intent classification & tool routing
├── tools/                        # Agentic Tool Registry (Week 4)
│   ├── contracts.py              # Pydantic I/O contracts
│   ├── retrieve_case.py          # Read-only case lookup tool
│   └── update_ticket.py          # HITL-gated ticket update tool
├── security/                     # Security & Guardrails (Weeks 4–5)
│   ├── auth.py                   # JWT minting & authentication
│   ├── rbac.py                   # Role-based access control & dept isolation
│   └── guardrails.py             # Prompt injection detection & sanitization
├── tests/                        # Automated Test Suites (221 Tests)
│   ├── api/                      # REST API endpoint tests
│   ├── unit/                     # Domain, service, repository unit tests
│   ├── pipeline/                 # Data engineering & quarantine tests
│   ├── e2e/                      # Scope change escalation E2E tests
│   ├── failure-scenarios/        # 8-incident cross-layer failure tests
│   ├── negative/                 # Negative-path & boundary condition tests
│   ├── regression/               # Weeks 1–4 cumulative regression tests
│   ├── security/                 # Red-team adversarial penetration tests
│   └── performance/              # p50/p95/p99 latency benchmark tests
├── docs/week5/                   # Handover & Engineering Documentation
│   ├── client-engagement/        # Discovery, requirements, constraints
│   ├── architecture/             # Component, sequence, deployment, ADRs
│   ├── scope-change/             # Escalation tier impact assessment & ADR
│   ├── failures/                 # Failure catalog & incident runbooks 01-08
│   ├── security/                 # Threat model, abuse cases, red-team report
│   ├── testing/                  # Performance benchmarks & regression strategy
│   ├── production-readiness/     # PRR checklist, reviews, limitations register
│   ├── deployment/               # Deployment, rollback, health check guides
│   ├── demo/                     # Demo scripts, presentations, checklist
│   ├── handover/                 # 12-document comprehensive handover package
│   └── operations/               # Level 1/2/3 Support Runbook
├── learning/week5/               # Learning Curriculum (30 Modules + 10 Labs)
│   ├── 00_WEEK5_OVERVIEW.md - 29_HANDOVER.md
│   ├── labs/                     # LAB-01 through LAB-10
│   ├── INTERVIEW_PREPARATION.md  # Beginner to scenario-based Q&A
│   ├── SELF_ASSESSMENT.md        # 20 questions + answer key
│   └── WEEK5_STUDY_PLAN.md       # 10-day structured progression
├── release/                      # Release Candidate Artifacts (v1.0.0-rc1)
└── README.md                     # Master Repository Overview
```

# Setup

### Prerequisites
- Python 3.14+ (or Python 3.11/3.12)
- Git
- PowerShell (Windows) or Bash (Linux/macOS)

### Installation
```bash
# Clone repository
git clone <repo-url> case-management-backend
cd case-management-backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate       # Windows PowerShell
source venv/bin/activate      # Linux / macOS

# Install package in development mode with test dependencies
pip install -e ".[dev]"
```

# Environment Configuration
Create a `.env` file from the reference template:
```bash
DATABASE_URL=sqlite:///./test.db
JWT_SECRET_KEY=dev-secret-key-12345
APPROVAL_SECRET_KEY=dev-approval-key-67890
ENVIRONMENT=development
LOG_LEVEL=INFO
EMBEDDING_PROVIDER=dense_hash
LLM_PROVIDER=mock
```

# Running Locally
Start the FastAPI server using Uvicorn:
```bash
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```
- Interactive API Docs: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/health/ready`

# Running Tests
Execute the entire test suite (221 tests) across all 5 weeks:
```bash
.\venv\Scripts\python.exe -m pytest -q
```
*Current Suite Status: 221 passed, 0 failed in ~27 seconds.*

# Unit Tests
Run domain models, services, and repository unit tests:
```bash
.\venv\Scripts\python.exe -m pytest tests/unit/ -v
```

# Integration Tests
Run REST API, database interaction, and tool contract tests:
```bash
.\venv\Scripts\python.exe -m pytest tests/api/ tests/test_tools_contracts.py -v
```

# E2E Tests
Run end-to-end scope change and workflow journey tests:
```bash
.\venv\Scripts\python.exe -m pytest tests/e2e/test_scope_change_escalation.py -v
```

# Regression Tests
Verify that Weeks 1–4 capabilities remain completely intact:
```bash
.\venv\Scripts\python.exe -m pytest tests/regression/test_regression_suite.py -v
```

# Negative Tests
Run boundary condition, corrupted schema, and malformed payload tests:
```bash
.\venv\Scripts\python.exe -m pytest tests/negative/test_negative_paths.py -v
```

# Security Tests
Execute the 16-test Red-Team adversarial penetration suite:
```bash
.\venv\Scripts\python.exe -m pytest tests/security/test_red_team_suite.py -v
```

# Performance Tests
Run the automated latency and throughput benchmark suite:
```bash
.\venv\Scripts\python.exe -m pytest tests/performance/test_performance_benchmarks.py -v
```

# RAG Evaluation
Execute groundedness, retrieval relevance, and citation verification tests:
```bash
.\venv\Scripts\python.exe -m pytest tests/test_rag_evaluation.py -v
```

# Failure Scenarios
Inject cross-layer failures (data, API, RAG, tool, auth, model, workflow, deployment):
```bash
.\venv\Scripts\python.exe -m pytest tests/failure-scenarios/test_failure_scenarios.py -v
```

# Authentication & Authorization
- **Authentication**: Stateless HMAC-SHA256 JWT bearer tokens minted via `/api/v1/auth/token`.
- **Role Hierarchy**: `viewer` < `investigator` < `supervisor` < `admin` < `auditor`.
- **Enforcement**: Fast-failing FastAPI dependencies (`require_roles(...)`) and tool-level checks.
- **Department Isolation**: Enforced at the repository query level (`security/rbac.py::check_department_access`).

# Human Approval
Consequential actions (modifying ticket status to `RESOLVED` / `CLOSED` or escalating to `CRITICAL_ESC`) cannot execute autonomously:
1. Orchestrator detects consequential intent and transitions to `APPROVAL_REQUIRED`.
2. An authorized `supervisor` or `admin` reviews the request.
3. Cryptographic HMAC token generated binding ticket ID, proposed status, and approver ID with a 30-minute TTL.
4. Token verified deterministically prior to database write.

# Tool Integrations
- `retrieve_case`: Read-only tool querying case metadata and transaction details.
- `update_ticket`: Consequential write tool requiring cryptographic approval for critical state transitions.
- All tools wrapped in Pydantic input/output contracts with typed error envelopes.

# Observability
- **Correlation ID**: Unique UUID4 assigned at request entry, propagated to all sub-calls.
- **Structured Logging**: JSON logging via `structlog` with correlation ID, user ID, and timestamp.
- **Distributed Tracing**: OpenTelemetry spans tracing API -> workflow -> tools -> persistence.
- **Metrics**: Prometheus counters and histograms measuring request latency and error rates.

# Deployment
Deployable via Docker:
```bash
docker build -t case-management-backend:1.0.0-rc1 -f deployment/Dockerfile .
docker run -d -p 8000:8000 --env-file .env case-management-backend:1.0.0-rc1
```
Detailed instructions in `docs/week5/deployment/DEPLOYMENT_GUIDE.md`.

# Health Checks
- Liveness Probe: `GET /health/live` (Process is running).
- Readiness Probe: `GET /health/ready` (Database connected, RAG index initialized).

# Rollback
Automated rollback procedure documented in `docs/week5/deployment/ROLLBACK_PROCEDURE.md`:
```bash
kubectl rollout undo deployment/case-management-backend -n production
alembic downgrade -1
```

# CI/CD
Automated pipeline executes linting, static checks, unit tests, integration tests, security tests, and performance benchmarks on all pull requests.

# Production Readiness
Evaluated against `docs/week5/production-readiness/PRODUCTION_READINESS_CHECKLIST.md`:
- All functional, security, performance, and operational gates marked **PASS**.
- Complete sign-offs recorded in `FINAL_READINESS_REPORT.md`.

# Known Limitations
Documented in `docs/week5/production-readiness/KNOWN_LIMITATIONS.md`:
- Local dense hash embeddings used for unit testing; remote vector API recommended for production.
- SQLite WAL mode used in local dev; PostgreSQL required for multi-pod Kubernetes deployments.
- Approval tokens have a fixed 30-minute TTL.

# Troubleshooting
Level 1/2/3 Support Runbook located at `docs/week5/operations/SUPPORT_RUNBOOK.md`. Incident catalog for 8 primary failure types available at `docs/week5/failures/FAILURE_CATALOG.md`.

# Technical Demo
18-step live demonstration script available at `docs/week5/demo/DEMO_SCRIPT.md` covering architecture, grounded RAG, human approval, audit trails, and red-team attack mitigation.

# Knowledge Transfer
12 dedicated handover guides located in `docs/week5/handover/`:
- `SYSTEM_OVERVIEW.md`, `LOCAL_SETUP.md`, `CONFIGURATION_GUIDE.md`
- `DEPLOYMENT_GUIDE.md`, `OPERATIONS_GUIDE.md`, `TROUBLESHOOTING_GUIDE.md`
- `SECURITY_GUIDE.md`, `TESTING_GUIDE.md`, `OWNERSHIP_MATRIX.md`

# Handover
Formal engagement closure package in `docs/week5/handover/HANDOVER_GUIDE.md` with complete ownership transition sign-offs.

# Learning Materials
Comprehensive curriculum under `learning/week5/`:
- Modules `00_WEEK5_OVERVIEW.md` through `29_HANDOVER.md` (30 modules).
- Practical Labs `LAB-01` through `LAB-10`.
- Interview Preparation (`INTERVIEW_PREPARATION.md`).
- Self-Assessment with Answer Key (`SELF_ASSESSMENT.md`).
- 10-Day Study Plan (`WEEK5_STUDY_PLAN.md`).

# Curriculum Traceability
Every requirement from `Fresher AI Training_Curriculam_Sep2026.pdf` is mapped in:
- `docs/week5/WEEK5_TRACEABILITY_MATRIX.md`
- `learning/week5/WEEK5_CURRICULUM_TRACEABILITY.md`

# Week 5 Deliverables
All 53 prompt deliverables created and verified with actual test evidence:
- 221 passed tests (0 failed).
- 8 seeded failure incident runbooks.
- 16-test adversarial Red-Team suite and closure report.
- Performance benchmark reports with measured p50/p95 latencies.
- Complete Production Readiness Review and Limitations Register.

# Final Release Candidate
Tagged and published as:
- **Version**: `1.0.0-rc1` (`release/VERSION.md`)
- **Release Notes**: `release/RELEASE_NOTES.md`
- **Release Checklist**: `release/RELEASE_CHECKLIST.md`
