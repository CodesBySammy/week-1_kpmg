# Enterprise Case Management & Controlled AI Platform

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Tests Passing](https://img.shields.io/badge/tests-143%2F143%20passed-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-87.15%25-brightgreen.svg)]()
[![Architecture: Medallion](https://img.shields.io/badge/architecture-Medallion%20Lakehouse-orange.svg)]()
[![RAG: Hybrid+Rerank](https://img.shields.io/badge/RAG-Hybrid%20%2B%20Rerank-purple.svg)]()
[![Workflow: Controlled Agency](https://img.shields.io/badge/workflow-HITL%20Controlled%20Agency-blue.svg)]()
[![Docker](https://img.shields.io/badge/Docker-Multi--Stage-2496ED.svg)](https://www.docker.com/)

An enterprise-grade, four-pillar software, data, and agentic AI platform developed for the **Forward Deployed Engineering (FDE) Fresher Readiness Program**:
1. **Week 1 Transactional Backend:** Modular, tested REST API service with SQLite, 3NF schema, Pydantic validation, and SCD Type 1/2 audit trails.
2. **Week 2 Enterprise Data Pipeline:** Medallion Lakehouse architecture (Bronze/Silver/Gold), 5-pillar statistical profiling, declarative data contracts, 8 domain quality rules, non-blocking quarantine handling, and mathematical source-to-target reconciliation.
3. **Week 3 Grounded Policy Knowledge Assistant (RAG):** Enterprise Policy Assistant featuring document ingestion, Markdown Section chunking, dense vector & Lucene BM25 hybrid indexing, candidate cross-score reranking, token-budget context assembly, and zero-hallucination grounded generation with verified citations.
4. **Week 4 Controlled AI Workflows & Production Engineering:** Deterministic finite state machine orchestration, typed tool contracts (`retrieve_case_details`, `update_ticket`), mandatory Human-in-the-Loop (HITL) approval tokens, HMAC-SHA256 JWT auth, role-based access control (RBAC), prompt injection guardrails, access-aware retrieval, distributed tracing (`X-Correlation-ID`), structured events, production metrics, and automated CI/CD release gates.

---

## 1. High-Level System Architecture

```mermaid
flowchart TD
    subgraph Ingress ["API Gateway & Ingress Layer"]
        Client[Client / Analyst / Caseworker] -->|HTTP / Bearer JWT| Gateway[FastAPI Ingress :8000]
        Gateway --> AuthMW[HMAC-SHA256 Auth & RBAC Middleware]
        AuthMW --> TelemetryMW[X-Correlation-ID & Tracing Context]
    end

    subgraph Week1 ["Week 1: Transactional OLTP Subsystem"]
        TelemetryMW --> CaseAPI[Case API: app/api/routes/cases.py]
        CaseAPI --> Service[Case Service: app/services/case_service.py]
        Service --> Repo[Repository: app/repositories/case_repository.py]
        Repo --> DB[(SQLite 3NF: case_management.db)]
        Repo --> AuditDB[(Audit Table: case_history)]
    end

    subgraph Week2 ["Week 2: Enterprise Data Pipeline Subsystem"]
        SrcCSV["Cases (CSV)"] & SrcJSON["Reference (JSON)"] & SrcPQ["Policies (Parquet)"] & SrcAPI["Policy REST API"] & SrcDB["Database Source"] --> Bronze["Raw Bronze Layer (Parquet Landing)"]
        Bronze --> Profiler["5-Pillar Statistical Profiler"]
        Profiler --> Quality{"8 Domain Quality Rules"}
        Quality -->|Invalid / Corrupted| DeadLetter["Quarantine Dead-Letter Sink (data/rejected/)"]
        Quality -->|Clean Valid Rows| Silver["Standardized Silver Layer (Cleaned Parquet)"]
        Silver --> Transform["Deduplication + Joins + Window Analytics + Aggregations"]
        Transform --> Gold["Curated Gold Layer (Parquet, CSV, SQLite)"]
        
        Bronze -.-> Reconciler["Source-to-Target Reconciliation Engine"]
        DeadLetter -.-> Reconciler
        Gold -.-> Reconciler
    end

    subgraph Week3 ["Week 3: Grounded Policy RAG Assistant Subsystem"]
        Corpus["Policy Corpus (data/policies/)"] --> Parser["Markdown & PDF Parsers + Text Sanitizer"]
        Parser --> Chunker["Markdown Section Chunker"]
        Chunker --> VectorIdx["Dense Vector Index (Cosine Dot Product)"]
        Chunker --> BM25Idx["Lucene Smoothed BM25 Index"]
        
        VectorIdx & BM25Idx --> Fusion["Hybrid Fusion (Weighted Score & RRF)"]
        Fusion --> Reranker["CrossScore Candidate Reranker"]
        Reranker --> Assembler["Token-Bounded Context Assembler (Max 2000 tok)"]
        Assembler --> Generator["Grounded Answer Generator (MockLLM / OpenAI)"]
        Generator --> CitationEngine["Citation Cross-Verification & Refusal Engine"]
    end

    subgraph Week4 ["Week 4: Controlled AI Workflow Subsystem"]
        TelemetryMW --> WorkflowAPI[Workflow API: app/api/routes/workflow.py]
        WorkflowAPI --> Sanitizer[Input Guardrail & Injection Scanner]
        Sanitizer --> Router[Deterministic Intent Router]
        Router --> FSM[Finite State Machine: 9 Valid States]
        
        FSM -->|Read Intent| ToolRead[Tool 1: retrieve_case_details]
        ToolRead --> Repo
        
        FSM -->|Write Intent| ApprMgr[Approval Manager: Cryptographic HITL Tokens]
        ApprMgr -->|Status: APPROVAL_REQUIRED| PendingPause[Execution Paused]
        
        Manager[Manager / Admin Reviewer] -->|POST /workflow/approval/{id}/approve| ApprMgr
        ApprMgr -->|Status: APPROVED| ToolWrite[Tool 2: update_ticket]
        ToolWrite --> IdempStore[Idempotency Store: Replay Protection]
        IdempStore --> Repo
        
        FSM --> Tracer[Distributed Tracing & Structured Events]
        Tracer --> MetricsCollector[Production Metrics: P50/P95/P99]
    end

    Router -->|Policy Search| Fusion
    Gateway -->|/health, /ready, /metrics| TelemetryMW
```

---

## 2. Quickstart & Installation

```powershell
# 1. Clone repository
git clone <repo_url>
cd case-management-backend

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -e .

# 4. Seed database
python seed_db.py

# 5. Run complete test suite with coverage
pytest --cov=app --cov=tools --cov=workflow --cov=security --cov=observability tests/

# 6. Start API server
uvicorn app.main:app --reload
```

---

## 3. Core API Endpoints

### Case Management (`app/api/routes/cases.py`)
- `POST /api/v1/cases`: Create case with domain validation.
- `GET /api/v1/cases/{id}`: Retrieve case and audit history.
- `PUT /api/v1/cases/{id}`: Update case status and assignees.
- `GET /api/v1/cases`: Paginated listing with multi-field filters.

### Grounded RAG Assistant (`app/api/routes/rag.py`)
- `GET /api/v1/rag/policies`: List all indexed policy documents and metadata.
- `POST /api/v1/rag/ingest`: Trigger corpus re-ingestion and vector indexing.
- `POST /api/v1/rag/query`: Grounded question-answering with verified citations.
- `POST /api/v1/rag/cases/{case_id}/policy-check`: Check a case against corporate policies for automated compliance advice.

### Controlled AI Workflow (`app/api/routes/workflow.py`)
- `POST /api/v1/workflow/auth/token`: Issue HMAC-SHA256 signed JWT bearer token (`viewer`, `agent`, `manager`, `admin`).
- `POST /api/v1/workflow/execute`: Execute authenticated AI workflow with intent routing, retries, and tool contracts.
- `GET /api/v1/workflow/approvals`: List pending human approval requests for managers.
- `POST /api/v1/workflow/approval/{id}/approve`: Grant manager approval for consequential ticket updates.
- `POST /api/v1/workflow/approval/{id}/reject`: Reject an approval request with audit reason.
- `GET /health`: Liveness probe.
- `GET /ready`: Readiness probe validating database connectivity and orchestrator initialization.
- `GET /metrics`: Telemetry endpoint exposing request counts, error distributions, and latency percentiles.

---

## 4. Documentation & Learning Index

### Master Study Plans
- [`WEEK1-STUDY-PLAN.md`](WEEK1-STUDY-PLAN.md): Week 1 Backend Mastery Plan.
- [`WEEK2-STUDY-PLAN.md`](WEEK2-STUDY-PLAN.md): Week 2 Lakehouse Data Pipeline Plan.
- [`WEEK3-STUDY-PLAN.md`](WEEK3-STUDY-PLAN.md): Week 3 Grounded RAG Assistant Plan.
- [`WEEK4-STUDY-PLAN.md`](WEEK4-STUDY-PLAN.md): Week 4 Controlled AI Workflows & SRE Plan.

### Master Architecture & Operational Docs
- [`docs/architecture.md`](docs/architecture.md): Complete 4-Pillar Master Architecture Document.
- [`docs/week4/tool-contracts.md`](docs/week4/tool-contracts.md): Strict I/O Schemas & Tool Specifications.
- [`docs/week4/human-approval.md`](docs/week4/human-approval.md): Human-in-the-Loop Governance Specification.
- [`docs/week4/security-guardrails.md`](docs/week4/security-guardrails.md): Prompt Injection & Guardrail Defenses.
- [`docs/week4/runbook.md`](docs/week4/runbook.md): SRE Operational Runbook for Incidents.
- [`docs/week4/rollback.md`](docs/week4/rollback.md): Deployment Rollback Procedure.
- [`docs/week4/release-gates.md`](docs/week4/release-gates.md): CI/CD Automated Quality Gates.
- [`docs/week4-security-review.md`](docs/week4-security-review.md): Senior Security Engineering Review.
- [`docs/week4-performance.md`](docs/week4-performance.md): Latency Benchmarks & Telemetry Review.
- [`docs/week4-requirement-traceability.md`](docs/week4-requirement-traceability.md): Requirements Traceability Matrix.

### Week 4 Learning Modules (`learning/week4/`)
- [`00-week4-overview.md`](learning/week4/00-week4-overview.md) through [`36-week4-debugging.md`](learning/week4/36-week4-debugging.md): 37 comprehensive tutorial modules covering every Week 4 topic.
- [`week4-practical-labs.md`](learning/week4/week4-practical-labs.md): Hands-on labs for tool contracts, approvals, and observability.
- [`week4-interview-questions.md`](learning/week4/week4-interview-questions.md): Senior engineering interview questions with architectural answers.
- [`week4-self-assessment.md`](learning/week4/week4-self-assessment.md): 10-question self-assessment checklist.
- [`week4-self-assessment-answers.md`](learning/week4/week4-self-assessment-answers.md): Detailed answer keys and scoring rubric.

---

## 5. Docker Deployment

```powershell
# Build multi-stage Docker image
docker build -t case-management-platform:v4.0 .

# Run containerized service
docker run -d -p 8000:8000 --name case-platform case-management-platform:v4.0

# Verify health probe
curl http://localhost:8000/health
curl http://localhost:8000/ready
```
