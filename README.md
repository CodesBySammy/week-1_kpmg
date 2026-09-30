# Case Management Platform — FDE Fresher Readiness Program

> **5-Week Cumulative Enterprise Project** | FastAPI · SQLAlchemy · Lakehouse ETL · Grounded RAG · Controlled AI Workflows · Observability

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Technology Stack](#2-technology-stack)
3. [Repository Structure](#3-repository-structure)
4. [Prerequisites](#4-prerequisites)
5. [Step 1 — Clone the Repository](#5-step-1--clone-the-repository)
6. [Step 2 — Create a Virtual Environment](#6-step-2--create-a-virtual-environment)
7. [Step 3 — Install Dependencies](#7-step-3--install-dependencies)
8. [Step 4 — Configure Environment Variables](#8-step-4--configure-environment-variables)
9. [Step 5 — Initialize & Seed the Database](#9-step-5--initialize--seed-the-database)
10. [Step 6 — Start the FastAPI Server](#10-step-6--start-the-fastapi-server)
11. [Step 7 — Verify Health & Readiness Probes](#11-step-7--verify-health--readiness-probes)
12. [Step 8 — Test the REST API (Week 1)](#12-step-8--test-the-rest-api-week-1)
13. [Step 9 — Run the Data Pipeline (Week 2)](#13-step-9--run-the-data-pipeline-week-2)
14. [Step 10 — Run the RAG Assistant (Week 3)](#14-step-10--run-the-rag-assistant-week-3)
15. [Step 11 — Test Controlled AI Workflows (Week 4)](#15-step-11--test-controlled-ai-workflows-week-4)
16. [Step 12 — Run the Full Automated Test Suite](#16-step-12--run-the-full-automated-test-suite)
17. [Step 13 — Run Tests with Coverage Report](#17-step-13--run-tests-with-coverage-report)
18. [Step 14 — Run Individual Test Categories](#18-step-14--run-individual-test-categories)
19. [Step 15 — Run with Docker](#19-step-15--run-with-docker)
20. [Step 16 — CI/CD Pipeline (GitHub Actions)](#20-step-16--cicd-pipeline-github-actions)
21. [Step 17 — Run SQL Exercises](#21-step-17--run-sql-exercises)
22. [API Reference (All Endpoints)](#22-api-reference-all-endpoints)
23. [Troubleshooting](#23-troubleshooting)

---

## 1. Project Overview

This is a **single cumulative project** built across 5 weeks of the FDE Fresher Readiness Program:

| Week | Theme | What Was Built |
|------|-------|---------------|
| **Week 1** | Foundations | FastAPI REST API, SQLAlchemy ORM, SQLite database, CRUD, pagination, error handling, OpenAPI docs |
| **Week 2** | Data Engineering | Lakehouse ETL pipeline (CSV/Parquet/JSON ingestion → Bronze → Silver → Gold), validation, quarantine, reconciliation |
| **Week 3** | AI/ML Integration | Grounded RAG assistant with hybrid retrieval (BM25 + vector), chunking, reranking, citation verification, hallucination guardrails |
| **Week 4** | Production Hardening | JWT RBAC auth, tool contracts, human-in-the-loop approval, workflow orchestrator, observability (metrics/tracing/events) |
| **Week 5** | Deployment & Quality | SLA escalation tiers, scope change management, comprehensive test suite (221 tests), CI/CD, Docker, release management |

---

## 2. Technology Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Web Framework | FastAPI + Uvicorn |
| ORM | SQLAlchemy 2.0 |
| Database | SQLite |
| Validation | Pydantic v2 |
| Data Processing | Pandas + PyArrow |
| RAG Retrieval | BM25 (rank_bm25) + Dense Vector (cosine similarity) |
| Document Parsing | pypdf |
| Auth | JWT (HS256) |
| Testing | pytest + pytest-cov + httpx |
| CI/CD | GitHub Actions |
| Containerization | Docker (multi-stage) |

---

## 3. Repository Structure

```
case-management-backend/
├── app/                          # Week 1: FastAPI application
│   ├── main.py                   #   Application entry point
│   ├── config.py                 #   Settings from .env
│   ├── api/routes/               #   REST API route handlers
│   │   ├── cases.py              #     CRUD for cases & users
│   │   ├── rag.py                #     RAG query endpoints
│   │   ├── workflow.py           #     AI workflow endpoints
│   │   └── mock_api.py           #     Mock external API
│   ├── models/case.py            #   SQLAlchemy ORM models
│   ├── schemas/case.py           #   Pydantic request/response schemas
│   ├── repositories/             #   Database access layer
│   ├── services/                 #   Business logic layer
│   ├── database/session.py       #   DB engine & session factory
│   └── exceptions/               #   Custom error handlers
│
├── pipeline/                     # Week 2: Data Pipeline
│   ├── cli.py                    #   CLI entry point
│   ├── sources/                  #   CSV, JSON, Parquet readers
│   ├── transformations/          #   Standardization, dedup, joins
│   ├── validation/               #   Schema & business rule validation
│   ├── quarantine/               #   Bad record isolation
│   ├── reconciliation/           #   Row count balance checks
│   ├── orchestration/pipeline.py #   Full/incremental pipeline runner
│   ├── profiling/                #   Data profiling reports
│   ├── audit/                    #   Pipeline audit trails
│   └── layers/                   #   Bronze → Silver → Gold export
│
├── rag/                          # Week 3: RAG Assistant
│   ├── cli.py                    #   CLI entry point
│   ├── pipeline.py               #   Main RAG pipeline orchestrator
│   ├── ingestion/                #   PDF/Markdown document loader
│   ├── chunking/                 #   Recursive text chunking
│   ├── embeddings/               #   TF-IDF dense embeddings
│   ├── indexing/                  #   BM25 + Vector hybrid index
│   ├── retrieval/                #   Hybrid retriever + reranker
│   ├── context/                  #   Token-bounded context builder
│   ├── generation/               #   Grounded answer generator
│   ├── evaluation/               #   Benchmark evaluator
│   └── llm/                      #   LLM abstraction layer
│
├── security/                     # Week 4: Auth & Security
│   ├── auth.py                   #   JWT token creation & verification
│   ├── rbac.py                   #   Role-based access control
│   ├── guardrails.py             #   Input/output guardrails
│   └── access_aware_retrieval.py #   Department-scoped RAG
│
├── workflow/                     # Week 4: Controlled AI Workflows
│   ├── orchestrator.py           #   Multi-step workflow engine
│   ├── router.py                 #   Intent classification & routing
│   ├── state.py                  #   Workflow state machine
│   ├── approval.py               #   Human-in-the-loop approval gate
│   └── fallback.py               #   Graceful degradation
│
├── tools/                        # Week 4: Tool Contracts
│   ├── registry.py               #   Tool registration system
│   ├── retrieve_case.py          #   Read-only case lookup tool
│   ├── update_ticket.py          #   Write tool (requires approval)
│   └── schemas.py                #   Tool input/output contracts
│
├── observability/                # Week 4: Telemetry
│   ├── metrics.py                #   Latency, token, error counters
│   ├── tracer.py                 #   Span-based distributed tracing
│   ├── events.py                 #   Structured event logger
│   └── correlation.py            #   Correlation ID middleware
│
├── tests/                        # All Weeks: 221 automated tests
│   ├── conftest.py               #   Shared fixtures & test client
│   ├── api/                      #   API integration tests
│   ├── unit/                     #   Model, schema, service unit tests
│   ├── pipeline/                 #   ETL pipeline tests
│   ├── e2e/                      #   End-to-end scenario tests
│   ├── security/                 #   Red team / penetration tests
│   ├── negative/                 #   Negative path tests
│   ├── performance/              #   Latency & throughput benchmarks
│   ├── regression/               #   Cross-week regression suite
│   ├── failure-scenarios/        #   Failure mode tests
│   ├── test_rag_*.py             #   RAG component tests
│   ├── test_workflow_*.py        #   Workflow orchestration tests
│   ├── test_security_*.py        #   RBAC & guardrail tests
│   └── test_tools_contracts.py   #   Tool contract validation
│
├── sql/                          # Raw SQL exercises
│   ├── schema.sql                #   Table creation DDL
│   ├── seed.sql                  #   Sample data DML
│   ├── queries.sql               #   CTEs, window functions, subqueries
│   └── transaction_examples.sql  #   ACID transaction demos
│
├── data/
│   ├── input/                    #   Pipeline source files (CSV, Parquet, JSON)
│   ├── policies/                 #   6 corporate policy documents for RAG
│   ├── raw/                      #   Bronze layer output
│   ├── standardized/             #   Silver layer output
│   └── curated/                  #   Gold layer output
│
├── docs/                         #   35+ design documents
├── learning/                     #   Week-by-week learning materials
├── release/                      #   Release notes & version
├── Dockerfile                    #   Multi-stage container build
├── pyproject.toml                #   Project config & dependencies
├── seed_db.py                    #   Database seeding script
├── .env.example                  #   Environment variable template
└── .github/workflows/ci.yml     #   GitHub Actions CI/CD pipeline
```

---

## 4. Prerequisites

Before you begin, make sure you have these installed on your machine:

| Tool | Minimum Version | Check Command | Install From |
|------|----------------|---------------|-------------|
| **Python** | 3.10 | `python --version` | [python.org](https://www.python.org/downloads/) |
| **pip** | 21.0 | `pip --version` | Included with Python |
| **Git** | 2.30 | `git --version` | [git-scm.com](https://git-scm.com/) |
| **Docker** *(optional)* | 20.0 | `docker --version` | [docker.com](https://www.docker.com/) |
| **curl** *(optional)* | any | `curl --version` | Pre-installed on most systems |

> **Note for Windows users**: Use PowerShell (recommended) or Command Prompt. All commands below work in both. If you use Git Bash, replace `python` with `python3` if needed.

---

## 5. Step 1 — Clone the Repository

Open your terminal and run:

```bash
git clone https://github.com/CodesBySammy/week-1_kpmg.git
cd week-1_kpmg/case-management-backend
```

> **Already cloned?** Just navigate to the project directory:
> ```bash
> cd path/to/week-1_kpmg/case-management-backend
> ```

---

## 6. Step 2 — Create a Virtual Environment

Creating a virtual environment isolates this project's dependencies from your system Python.

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> **How to verify it's active?** Your terminal prompt should now show `(venv)` at the beginning.

---

## 7. Step 3 — Install Dependencies

With your virtual environment activated, install all project and dev dependencies:

```bash
pip install --upgrade pip setuptools wheel
pip install -e ".[dev]"
```

**What this installs:**
- `fastapi`, `uvicorn`, `sqlalchemy`, `pydantic` — Web API stack
- `pandas`, `pyarrow` — Data pipeline processing
- `rank-bm25`, `pypdf` — RAG retrieval and document parsing
- `pyyaml`, `requests` — Configuration and HTTP
- `pytest`, `pytest-cov`, `httpx` — Testing tools (dev dependencies)

**Verify installation worked:**
```bash
python -c "import app, pipeline, rag, security, tools, workflow, observability; print('All 7 core modules imported successfully!')"
```

Expected output:
```
All 7 core modules imported successfully!
```

---

## 8. Step 4 — Configure Environment Variables

Copy the example environment file:

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**macOS / Linux:**
```bash
cp .env.example .env
```

The defaults work out-of-the-box for local development. Key settings in `.env`:

```env
APP_NAME=case-management-backend
APP_PORT=8000
DATABASE_URL=sqlite:///./case_management.db
LOG_LEVEL=DEBUG
RAG_POLICIES_DIR=./data/policies
JWT_SECRET=super-secret-development-jwt-signing-key-change-in-production
```

> **⚠️ Important:** Never commit the `.env` file to Git. It's already in `.gitignore`.

---

## 9. Step 5 — Initialize & Seed the Database

This creates the SQLite database file and inserts sample data (users, cases, case history):

```bash
python seed_db.py
```

**Expected output:**
```
Connecting to SQLite database at: .../case_management.db
Executing schema.sql...
Executing seed.sql...
==================================================
Database seeding completed successfully!
  - Users created:        5
  - Cases created:        10
  - Case History entries: 20
==================================================
```

**Verify the database was created:**

```bash
python -c "import sqlite3; conn = sqlite3.connect('case_management.db'); print('Tables:', [r[0] for r in conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()]); conn.close()"
```

Expected output:
```
Tables: ['users', 'cases', 'case_history']
```

---

## 10. Step 6 — Start the FastAPI Server

Run the development server:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Expected terminal output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Application starting
INFO:     Database tables initialized
```

**The server is now running at:** `http://127.0.0.1:8000`

| URL | Description |
|-----|------------|
| http://127.0.0.1:8000/docs | **Swagger UI** — Interactive API docs (try endpoints here!) |
| http://127.0.0.1:8000/redoc | **ReDoc** — Clean API documentation |
| http://127.0.0.1:8000/openapi.json | Raw OpenAPI 3.0 specification |

> **Keep this terminal running.** Open a **new terminal** for the following test commands.

---

## 11. Step 7 — Verify Health & Readiness Probes

Open a **new terminal** (activate the venv again if needed) and run:

**Health Check (Liveness Probe):**
```bash
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "app": "case-management-backend",
  "version": "4.0.0"
}
```

**Readiness Check (Readiness Probe):**
```bash
curl http://127.0.0.1:8000/ready
```

Expected response:
```json
{
  "status": "ready",
  "checks": {
    "database": true,
    "rag_service": true,
    "workflow_engine": true
  },
  "version": "4.0.0"
}
```

> **Windows without curl?** Open `http://127.0.0.1:8000/health` in your browser, or use PowerShell:
> ```powershell
> Invoke-RestMethod http://127.0.0.1:8000/health
> ```

---

## 12. Step 8 — Test the REST API (Week 1)

These commands test the CRUD API. Run them in a **separate terminal** while the server is running.

### 8a. Create a User
```bash
curl -X POST http://127.0.0.1:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "full_name": "Test User", "role": "analyst"}'
```

**Windows PowerShell version:**
```powershell
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/api/v1/users" `
  -ContentType "application/json" `
  -Body '{"username": "testuser", "email": "test@example.com", "full_name": "Test User", "role": "analyst"}'
```

Expected: HTTP 201 with the created user JSON.

### 8b. List All Users
```bash
curl http://127.0.0.1:8000/api/v1/users
```

### 8c. Create a Case
```bash
curl -X POST http://127.0.0.1:8000/api/v1/cases \
  -H "Content-Type: application/json" \
  -d '{"title": "Login page broken", "description": "Users cannot log in since the last deploy", "created_by": 1, "priority": "HIGH", "case_type": "BUG"}'
```

**Windows PowerShell version:**
```powershell
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/api/v1/cases" `
  -ContentType "application/json" `
  -Body '{"title": "Login page broken", "description": "Users cannot log in since the last deploy", "created_by": 1, "priority": "HIGH", "case_type": "BUG"}'
```

Expected: HTTP 201 with the created case JSON.

### 8d. Get a Specific Case
```bash
curl http://127.0.0.1:8000/api/v1/cases/1
```

### 8e. List All Cases (with Pagination & Filters)
```bash
# Get first 5 cases
curl "http://127.0.0.1:8000/api/v1/cases?skip=0&limit=5"

# Filter by status
curl "http://127.0.0.1:8000/api/v1/cases?status=OPEN"

# Filter by priority
curl "http://127.0.0.1:8000/api/v1/cases?priority=HIGH"
```

### 8f. Update a Case
```bash
curl -X PUT http://127.0.0.1:8000/api/v1/cases/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "IN_PROGRESS", "assigned_to": 2}'
```

**Windows PowerShell version:**
```powershell
Invoke-RestMethod -Method PUT -Uri "http://127.0.0.1:8000/api/v1/cases/1" `
  -ContentType "application/json" `
  -Body '{"status": "IN_PROGRESS", "assigned_to": 2}'
```

### 8g. Test Error Handling
```bash
# 404 — Case not found
curl http://127.0.0.1:8000/api/v1/cases/99999

# 422 — Validation error (missing required field)
curl -X POST http://127.0.0.1:8000/api/v1/cases \
  -H "Content-Type: application/json" \
  -d '{"description": "Missing title field"}'
```

---

## 13. Step 9 — Run the Data Pipeline (Week 2)

The data pipeline processes CSV, JSON, and Parquet source files through Bronze → Silver → Gold layers.

> **You do NOT need the server running for this.** The pipeline runs as a standalone CLI.

### 9a. Full Pipeline Run
```bash
python -m pipeline.cli --mode full
```

**Expected output:**
```
=================================================================
>>> STARTING CASE MANAGEMENT ENTERPRISE DATA PIPELINE (WEEK 2)
   Execution Mode: FULL
=================================================================

[SUCCESS] PIPELINE EXECUTION COMPLETED
=================================================================
  * Run ID:                RUN_20260930_...
  * Batch ID:              BATCH_...
  * Status:                PASS
  * Ingested Source Rows:  30
  * Valid Rows:            28
  * Quarantined Rows:      2
  * Duplicates Removed:    3
  * Curated Rows:          25
  * Reconciliation Check:  PASS
  * Run Manifest:          data/curated/manifest_...
=================================================================
```

### 9b. Incremental Pipeline Run
```bash
python -m pipeline.cli --mode incremental
```

### 9c. Pipeline with Custom Input
```bash
python -m pipeline.cli --mode full --input data/input/cases.csv --run-id MY_TEST_RUN
```

### 9d. Verify Pipeline Output Files

After running, check that output files were created:

```bash
# Check the curated (Gold) layer
python -c "import os; files = os.listdir('data/curated'); print('Curated files:', files)"

# Check quarantined (rejected) records
python -c "import os; files = os.listdir('data/rejected'); print('Rejected files:', files)"
```

---

## 14. Step 10 — Run the RAG Assistant (Week 3)

The RAG assistant answers questions about corporate policies using hybrid retrieval with grounding checks.

> **You do NOT need the server running for CLI mode.** But the API endpoints require the server.

### 10a. Ingest Policy Documents
```bash
python -m rag.cli ingest --dir data/policies
```

**Expected output:**
```
============================================================
RAG Corpus Ingestion & Vector Indexing
============================================================
Indexed 6 documents into 48 chunks.
Indices updated: VectorIndex (dense) + BM25Index (lexical)
Completed in 0.35 seconds.
```

### 10b. Query the RAG Assistant
```bash
python -m rag.cli query "What is the password policy?"
```

**Expected output:**
```
============================================================
Policy Knowledge Query: 'What is the password policy?'
Mode: hybrid | Top-K: 3 | Reranker: True
============================================================

--- GROUNDED ANSWER ---
Based on the IT Security Policy (IT-SECURITY-005), passwords must be...

Grounding Status: Grounded in Context
Refusal Status: none
```

### 10c. Try Different Retrieval Modes
```bash
# Vector-only retrieval
python -m rag.cli query "What is the leave policy?" --mode vector

# BM25 (lexical) retrieval
python -m rag.cli query "How are expenses reimbursed?" --mode bm25

# Hybrid retrieval with verbose output
python -m rag.cli query "What are the travel approval thresholds?" --mode hybrid --top-k 5 -v
```

### 10d. Run RAG Benchmark Evaluation
```bash
python -m rag.cli evaluate
```

**Expected output:**
```
============================================================
RAG Retrieval & Generation Benchmark Evaluation
Strategy A (Vector Only k=5) vs Strategy B (Hybrid + Reranking k=3)
============================================================

Benchmark Queries Evaluated: 6

Metric                    | Strategy A (Vector)    | Strategy B (Hybrid+Rerank)
------------------------------------------------------------------------------
Hit Rate                  |                83.3%   |                   100.0%
MRR (Mean Reciprocal Rank)|               0.7222   |                  1.0000
...
```

### 10e. Test RAG via API (Server Must Be Running)
```bash
# List indexed policies
curl http://127.0.0.1:8000/api/v1/rag/policies

# Ask a question via API
curl -X POST http://127.0.0.1:8000/api/v1/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the expense reimbursement limit?", "retrieval_mode": "hybrid", "top_k": 3}'

# Check a case against policies (integrates Week 1 + Week 3)
curl -X POST http://127.0.0.1:8000/api/v1/rag/cases/1/policy-check

# Run benchmark via API
curl http://127.0.0.1:8000/api/v1/rag/benchmark
```

**Windows PowerShell version:**
```powershell
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/api/v1/rag/query" `
  -ContentType "application/json" `
  -Body '{"question": "What is the expense reimbursement limit?", "retrieval_mode": "hybrid", "top_k": 3}'
```

---

## 15. Step 11 — Test Controlled AI Workflows (Week 4)

The workflow system implements JWT-authenticated, approval-gated AI operations with full observability.

> **The server must be running** for these tests.

### 11a. Generate a JWT Token
```bash
curl -X POST http://127.0.0.1:8000/api/v1/workflow/auth/token \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "username": "test_agent", "email": "agent@company.com", "role": "agent", "department": "Operations"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "Bearer",
  "role": "agent",
  "username": "test_agent"
}
```

> **⚠️ Copy the `access_token` value.** You'll use it in the next commands as `YOUR_TOKEN`.

### 11b. Execute a Read-Only Workflow (No Approval Needed)
```bash
curl -X POST http://127.0.0.1:8000/api/v1/workflow/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"query": "Look up case 1"}'
```

**Windows PowerShell:**
```powershell
$token = "YOUR_TOKEN"  # Paste your token here
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/api/v1/workflow/execute" `
  -ContentType "application/json" `
  -Headers @{ Authorization = "Bearer $token" } `
  -Body '{"query": "Look up case 1"}'
```

### 11c. Execute a Write Workflow (Triggers Approval Gate)
```bash
curl -X POST http://127.0.0.1:8000/api/v1/workflow/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"query": "Update case 1 status to IN_PROGRESS"}'
```

Response will include `"requires_approval": true` and an `approval_id`.

### 11d. List Pending Approvals
```bash
curl http://127.0.0.1:8000/api/v1/workflow/approvals \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 11e. Approve a Pending Request (Requires Manager Role)

First, generate a manager token:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/workflow/auth/token \
  -H "Content-Type: application/json" \
  -d '{"user_id": 2, "username": "manager_user", "email": "mgr@company.com", "role": "manager", "department": "Operations"}'
```

Then approve (use the `approval_id` from step 11c):
```bash
curl -X POST http://127.0.0.1:8000/api/v1/workflow/approval/APPROVAL_ID_HERE/approve \
  -H "Authorization: Bearer MANAGER_TOKEN"
```

### 11f. Re-Execute with Approval Token
```bash
curl -X POST http://127.0.0.1:8000/api/v1/workflow/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"query": "Update case 1 status to IN_PROGRESS", "approval_id": "APPROVAL_ID_HERE"}'
```

### 11g. View Observability Metrics
```bash
curl http://127.0.0.1:8000/api/v1/workflow/metrics
```

Response includes latencies, request counts, error rates, and token usage.

---

## 16. Step 12 — Run the Full Automated Test Suite

> **Stop the server first** (Ctrl+C). Tests use their own in-memory test database.

### 12a. Run All 221 Tests
```bash
python -m pytest
```

**Expected output:**
```
============================= test session starts =============================
collected 221 items

tests/api/test_cases_api.py ........                                 [  3%]
tests/api/test_user_and_error_handlers.py ....                       [  5%]
tests/e2e/test_scope_change_escalation.py .........                  [  9%]
tests/failure-scenarios/test_failure_scenarios.py ...........         [ 14%]
tests/negative/test_negative_paths.py ................                [ 21%]
tests/performance/test_performance_benchmarks.py ........             [ 25%]
tests/pipeline/test_failures.py ....                                 [ 27%]
tests/pipeline/test_orchestration.py ....                            [ 29%]
tests/pipeline/test_profiler.py ....                                 [ 31%]
tests/pipeline/test_quarantine.py ........                           [ 34%]
tests/pipeline/test_reconciliation.py ......                         [ 37%]
tests/pipeline/test_sources.py ......                                [ 40%]
tests/pipeline/test_transformations.py ......                        [ 43%]
tests/pipeline/test_validation.py .......                            [ 46%]
tests/regression/test_regression_suite.py ..........                  [ 50%]
tests/security/test_red_team_suite.py ..............                  [ 57%]
tests/test_human_approval.py ..........                               [ 61%]
tests/test_observability.py ......                                   [ 64%]
tests/test_rag_api.py ........                                       [ 68%]
tests/test_rag_chunking.py .......                                   [ 71%]
tests/test_rag_context_generation.py ....                            [ 73%]
tests/test_rag_embeddings_indices.py ........                        [ 76%]
tests/test_rag_evaluation.py ....                                    [ 78%]
tests/test_rag_ingestion.py ........                                 [ 82%]
tests/test_rag_retrieval_rerank.py ......                            [ 85%]
tests/test_security_guardrails.py .....                              [ 87%]
tests/test_security_rbac.py ......                                   [ 90%]
tests/test_tools_contracts.py ...........                            [ 95%]
tests/test_workflow_api.py ........                                  [ 98%]
tests/test_workflow_orchestration.py ....                             [100%]
tests/unit/test_case_repository.py ........
tests/unit/test_case_service.py ..........
tests/unit/test_models_and_schemas.py ...

======================== 221 passed in ~10s ================================
```

---

## 17. Step 13 — Run Tests with Coverage Report

### 13a. Coverage with Terminal Output
```bash
python -m pytest --cov=app --cov=pipeline --cov=rag --cov=security --cov=tools --cov=workflow --cov=observability --cov-report=term-missing --cov-fail-under=70
```

This shows:
- Line-by-line coverage for every module
- Missing lines highlighted
- **Fails if coverage drops below 70%** (the CI gate threshold)

### 13b. Generate HTML Coverage Report
```bash
python -m pytest --cov=app --cov=pipeline --cov=rag --cov=security --cov=tools --cov=workflow --cov=observability --cov-report=html
```

Then open `htmlcov/index.html` in your browser:

**Windows:**
```powershell
Start-Process htmlcov\index.html
```

**macOS:**
```bash
open htmlcov/index.html
```

**Linux:**
```bash
xdg-open htmlcov/index.html
```

---

## 18. Step 14 — Run Individual Test Categories

You can run specific test groups independently:

### By Week / Component

```bash
# Week 1: API & CRUD tests
python -m pytest tests/api/ tests/unit/ -v

# Week 2: Data Pipeline tests
python -m pytest tests/pipeline/ -v

# Week 3: RAG tests
python -m pytest tests/test_rag_*.py -v

# Week 4: Workflow, Security, Tools tests
python -m pytest tests/test_workflow_*.py tests/test_security_*.py tests/test_tools_contracts.py tests/test_human_approval.py -v

# Week 5: E2E, Regression, Performance, Security, Negative, Failure Scenarios
python -m pytest tests/e2e/ tests/regression/ tests/performance/ tests/security/ tests/negative/ tests/failure-scenarios/ -v
```

### By Test Type

```bash
# Unit tests only
python -m pytest tests/unit/ -v

# API integration tests only
python -m pytest tests/api/ -v

# End-to-end scenario tests
python -m pytest tests/e2e/ -v

# Negative path tests (invalid inputs, boundary conditions)
python -m pytest tests/negative/ -v

# Performance benchmark tests
python -m pytest tests/performance/ -v

# Security red-team tests (injection, privilege escalation)
python -m pytest tests/security/ -v

# Regression suite (cross-week compatibility)
python -m pytest tests/regression/ -v

# Failure scenario tests (crash recovery, graceful degradation)
python -m pytest tests/failure-scenarios/ -v

# Observability tests
python -m pytest tests/test_observability.py -v
```

### Run a Single Test File
```bash
python -m pytest tests/api/test_cases_api.py -v
```

### Run a Single Test Function
```bash
python -m pytest tests/api/test_cases_api.py::TestCaseAPI::test_create_case_valid -v
```

### Run Tests Matching a Keyword
```bash
# All tests with "rag" in the name
python -m pytest -k "rag" -v

# All tests with "approval" in the name
python -m pytest -k "approval" -v

# All tests with "pipeline" in the name
python -m pytest -k "pipeline" -v
```

---

## 19. Step 15 — Run with Docker

### 15a. Build the Docker Image
```bash
docker build -t case-management-platform .
```

### 15b. Run the FastAPI Server in Docker
```bash
docker run -p 8000:8000 case-management-platform uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Then test: `curl http://localhost:8000/health`

### 15c. Run the Data Pipeline in Docker
```bash
docker run case-management-platform python -m pipeline.cli --mode full
```

### 15d. Run the RAG CLI in Docker
```bash
# Ingest policies
docker run case-management-platform python -m rag.cli ingest

# Ask a question
docker run case-management-platform python -m rag.cli query "What is the password policy?"

# Run evaluation
docker run case-management-platform python -m rag.cli evaluate
```

### 15e. Run Tests in Docker
```bash
docker run case-management-platform python -m pytest tests/ -v
```

---

## 20. Step 16 — CI/CD Pipeline (GitHub Actions)

The project includes a GitHub Actions CI/CD pipeline (`.github/workflows/ci.yml`) that automatically runs on every push to `main`/`master` or pull request.

### What the CI Pipeline Does

| Step | Description |
|------|------------|
| **Matrix** | Runs on Python 3.10 and 3.11 |
| **Install** | `pip install -e ".[dev]"` |
| **Import Verification** | Verifies all 7 core modules import cleanly |
| **Test Suite** | Runs all 221 tests with coverage |
| **Coverage Gate** | Fails if coverage < 70% |
| **Health Probe** | Verifies `/health` and `/ready` endpoints return 200 |

### Trigger CI Manually

Push any commit to trigger:
```bash
git add .
git commit -m "your message"
git push origin main
```

Then check: `https://github.com/CodesBySammy/week-1_kpmg/actions`

---

## 21. Step 17 — Run SQL Exercises

The `sql/` directory contains standalone SQL scripts for learning and exercises.

### 17a. Run Schema Creation
```bash
python -c "
import sqlite3
conn = sqlite3.connect('case_management.db')
with open('sql/schema.sql') as f:
    conn.executescript(f.read())
print('Schema executed successfully')
conn.close()
"
```

### 17b. Run Seed Data
```bash
python -c "
import sqlite3
conn = sqlite3.connect('case_management.db')
with open('sql/seed.sql') as f:
    conn.executescript(f.read())
print('Seed data inserted successfully')
conn.close()
"
```

### 17c. Run Query Exercises (CTEs, Window Functions, Subqueries)
```bash
python -c "
import sqlite3
conn = sqlite3.connect('case_management.db')
cursor = conn.cursor()

# Example: CTE — Case timeline
print('=== CTE: Case Change Timeline ===')
cursor.execute('''
    WITH case_changes AS (
        SELECT c.title, ch.field_changed, ch.old_value, ch.new_value, ch.changed_at
        FROM case_history ch
        JOIN cases c ON ch.case_id = c.id
    )
    SELECT * FROM case_changes ORDER BY changed_at DESC LIMIT 5
''')
for row in cursor.fetchall():
    print(row)

# Example: Window Function — Row number per case
print('\n=== Window Function: Nth Change per Case ===')
cursor.execute('''
    SELECT case_id, field_changed,
           ROW_NUMBER() OVER (PARTITION BY case_id ORDER BY changed_at) as change_num
    FROM case_history
    LIMIT 10
''')
for row in cursor.fetchall():
    print(row)

conn.close()
"
```

### 17d. Interactive SQL Session
```bash
python -c "
import sqlite3, cmd

class SQLShell(cmd.Cmd):
    prompt = 'sql> '
    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect('case_management.db')
    def default(self, line):
        try:
            for row in self.conn.execute(line):
                print(row)
        except Exception as e:
            print(f'Error: {e}')
    def do_exit(self, _): return True

SQLShell().cmdloop('SQLite Shell (type SQL queries, \"exit\" to quit)')
"
```

---

## 22. API Reference (All Endpoints)

### System Endpoints

| Method | Endpoint | Description |
|--------|---------|-------------|
| `GET` | `/health` | Liveness probe |
| `GET` | `/ready` | Readiness probe (checks DB, RAG, Workflow) |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc documentation |
| `GET` | `/openapi.json` | OpenAPI 3.0 spec |

### Case Management (Week 1) — `/api/v1`

| Method | Endpoint | Description |
|--------|---------|-------------|
| `POST` | `/api/v1/users` | Create a new user |
| `GET` | `/api/v1/users` | List all users |
| `POST` | `/api/v1/cases` | Create a new case |
| `GET` | `/api/v1/cases` | List cases (paginated, filterable) |
| `GET` | `/api/v1/cases/{id}` | Get a case by ID |
| `PUT` | `/api/v1/cases/{id}` | Update a case |

### RAG Assistant (Week 3) — `/api/v1/rag`

| Method | Endpoint | Description |
|--------|---------|-------------|
| `GET` | `/api/v1/rag/policies` | List all indexed policy documents |
| `POST` | `/api/v1/rag/ingest` | Trigger policy ingestion & indexing |
| `POST` | `/api/v1/rag/retrieve` | Retrieve relevant chunks (no generation) |
| `POST` | `/api/v1/rag/query` | Ask a grounded question to the RAG assistant |
| `GET` | `/api/v1/rag/benchmark` | Run retrieval strategy comparison |
| `POST` | `/api/v1/rag/cases/{id}/policy-check` | Check a case against corporate policies |

### Controlled AI Workflow (Week 4) — `/api/v1/workflow`

| Method | Endpoint | Description | Auth Required |
|--------|---------|-------------|:---:|
| `POST` | `/api/v1/workflow/auth/token` | Generate JWT token | ❌ |
| `POST` | `/api/v1/workflow/execute` | Execute AI workflow | ✅ |
| `GET` | `/api/v1/workflow/approvals` | List pending approvals | ✅ |
| `POST` | `/api/v1/workflow/approval/{id}/approve` | Approve a request | ✅ (manager) |
| `POST` | `/api/v1/workflow/approval/{id}/reject` | Reject a request | ✅ (manager) |
| `GET` | `/api/v1/workflow/metrics` | View telemetry metrics | ❌ |

---

## 23. Troubleshooting

### Common Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| `ModuleNotFoundError: No module named 'app'` | Not in the right directory | `cd` into `case-management-backend/` |
| `ModuleNotFoundError: No module named 'rank_bm25'` | Dependencies not installed | Run `pip install -e ".[dev]"` |
| `ModuleNotFoundError: No module named 'pyarrow'` | pyarrow not installed (common on Python 3.13+) | Run `pip install pyarrow` |
| `sqlite3.OperationalError: no such table: users` | Database not initialized | Run `python seed_db.py` |
| `Address already in use (port 8000)` | Another server is using the port | Kill it or use `--port 8001` |
| `venv\Scripts\Activate.ps1 cannot be loaded` | PowerShell execution policy | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Tests fail with `ImportError` | Virtual environment not activated | Run `.\venv\Scripts\Activate.ps1` |
| `422 Unprocessable Entity` on API calls | Invalid JSON or missing required fields | Check the Swagger docs at `/docs` |
| CI fails but local passes | Python version difference | CI uses Python 3.10/3.11; check version-specific behavior |

### Useful Debug Commands

```bash
# Check Python version
python --version

# Check if venv is active
pip --version   # Should show path inside venv/

# Check installed packages
pip list

# Check database exists and has data
python -c "import sqlite3; c=sqlite3.connect('case_management.db'); print('Users:', c.execute('SELECT COUNT(*) FROM users').fetchone()[0]); print('Cases:', c.execute('SELECT COUNT(*) FROM cases').fetchone()[0]); c.close()"

# Verify all core imports
python -c "import app, pipeline, rag, security, tools, workflow, observability; print('OK')"

# Check test count without running
python -m pytest --collect-only -q
```

---

## Quick Reference — Complete Testing Checklist

```
✅ STEP  1  →  git clone + cd into project
✅ STEP  2  →  python -m venv venv && activate
✅ STEP  3  →  pip install -e ".[dev]"
✅ STEP  4  →  cp .env.example .env
✅ STEP  5  →  python seed_db.py
✅ STEP  6  →  uvicorn app.main:app --reload
✅ STEP  7  →  curl /health + /ready
✅ STEP  8  →  CRUD operations via curl
✅ STEP  9  →  python -m pipeline.cli --mode full
✅ STEP 10  →  python -m rag.cli ingest + query + evaluate
✅ STEP 11  →  JWT token → workflow execute → approve
✅ STEP 12  →  python -m pytest (221 tests)
✅ STEP 13  →  pytest --cov (coverage ≥ 70%)
✅ STEP 14  →  Individual test categories
✅ STEP 15  →  docker build + run
✅ STEP 16  →  git push → GitHub Actions green ✓
✅ STEP 17  →  SQL exercises (CTEs, window functions)
```

---

**Built as part of the FDE Fresher Readiness Program — 5-Week Technical Learning Plan**
