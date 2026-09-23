# Week 1 – Week 3 System Baseline & Integration Points for Week 4

> **Report Date:** September 2026  
> **Baseline Established:** 100 Tests Passing, 86.78% Code Coverage  
> **Target Program:** FDE Fresher Readiness Program — Week 4 Evolution

---

## 1. Existing System Architecture Overview

### Week 1: Case Management Backend (`app/`)
- **FastAPI Web Service:** Modular layered architecture (`api/`, `schemas/`, `services/`, `repositories/`, `models/`, `database/`, `exceptions/`).
- **Relational Persistence:** SQLite database (`case_management.db`) in Third Normal Form (3NF) with tables `users`, `cases`, and SCD Type 1/2 `case_history` for full audit trails.
- **Validation & Errors:** Strict Pydantic models with domain state-machine enforcement (e.g. `CLOSED` cases cannot be mutated). Global exception handlers map errors to RFC 7807 problem details.
- **Baseline Tests:** 30 unit & integration tests passing.

### Week 2: Enterprise Data Pipeline (`pipeline/`)
- **Medallion Lakehouse:** Raw (Bronze Parquet landing), Standardized (Silver cleaned data), and Curated (Gold analytics with aggregations and joins).
- **5-Pillar Statistical Profiler:** Completeness, Uniqueness, Validity, Distribution, and Referential integrity metrics.
- **Quality Rules & Quarantine:** 8 domain quality rules, non-blocking quarantine dead-letter sink (`data/rejected/`), and high-watermark state tracking (`audit/watermark.json`).
- **Source-to-Target Reconciliation:** Row-count and metric sum balance ledger verifying zero silent data loss.
- **Baseline Tests:** 38 tests passing.

### Week 3: Grounded RAG Policy Knowledge Assistant (`rag/`)
- **Corporate Policy Corpus:** 6 enterprise Markdown documents with YAML frontmatter (`data/policies/`).
- **Chunking & Indexing:** `MarkdownSectionChunker` preserving header context; `VectorIndex` with dense hashing; `BM25Index` with Lucene smoothed IDF; `HybridIndex` supporting Weighted Fusion ($\alpha=0.6$) and Reciprocal Rank Fusion (RRF).
- **Reranker & Generation:** `CrossScoreReranker` for candidate cross-scoring; `ContextAssembler` with token budget enforcement (2000 tokens); `GroundedAnswerGenerator` with citation verification and out-of-domain refusals.
- **REST Endpoints:** `/api/v1/rag/*` including `/policies`, `/ingest`, `/retrieve`, `/query`, `/benchmark`, and `/cases/{id}/policy-check`.
- **Baseline Tests:** 32 tests passing.

---

## 2. Baseline Test Results

```text
====================== 100 passed, 49 warnings in 16.74s ======================
Total Coverage: 86.78%
app/ coverage: 90%+
pipeline/ coverage: 87%+
rag/ coverage: 85%+
```

---

## 3. Week 4 Integration Points & Architectural Evolution

To convert the platform into a **Controlled AI Workflow with Typed Tool Integrations, Human Approval, Security Guardrails, Observability, and CI/CD**, the system will be extended as follows:

```
                         CASE MANAGEMENT PLATFORM
                                    |
       +----------------------------+----------------------------+
       |                            |                            |
       ↓                            ↓                            ↓
    FastAPI                   Data Pipeline                     RAG
  (Transactional)              (Analytical)             (Policy Knowledge)
       |                            |                            |
       ↓                            ↓                            ↓
   Database                  Curated Data                 Policy Corpus
       |                                                         |
       +----------------------------+----------------------------+
                                    |
                                    ↓
                         AI WORKFLOW ORCHESTRATOR
                       (workflow/orchestration/)
                                    |
                    +---------------+---------------+
                    |                               |
                    ↓                               ↓
               RAG Answer                     Tool Decision
                                                    |
                                    +---------------+---------------+
                                    |                               |
                                    ↓                               ↓
                          retrieve_case_details               update_ticket
                               (Read Tool)                    (Write Tool)
                                    |                               |
                                    |                     [APPROVAL REQUIRED]
                                    |                               |
                                    |                     [Manager / Admin RBAC]
                                    |                               |
                                    +---------------+---------------+
                                                    |
                                                    ↓
                                         [Audit Trail & Tracing]
                                        (observability/tracing/)
                                                    |
                                                    ↓
                                       [Security & Guardrails]
                                            (security/)
                                                    |
                                                    ↓
                                            [CI/CD & Delivery]
                                          (.github/workflows/)
```

### Specific Subsystem Extensions:
1. **`workflow/` Subsystem:**
   - `workflow/state.py`: Explicit workflow state machine (`REQUEST_RECEIVED`, `INTENT_DETECTED`, `TOOL_PROPOSED`, `APPROVAL_REQUIRED`, `APPROVED`, `EXECUTING`, `COMPLETED`, `APPROVAL_REJECTED`, `FAILED`).
   - `workflow/router.py`: Deterministic and AI-driven routing between pure RAG answers, case retrieval tools, and ticket update workflows.
   - `workflow/orchestrator.py`: Multi-step execution engine with retries (exponential backoff), timeouts, and fallback paths.
   - `workflow/approval.py`: Persistent Human-in-the-loop (HITL) approval manager for consequential/write actions.
2. **`tools/` Subsystem:**
   - `tools/schemas.py`: Explicit Pydantic JSON schemas with strict field-level constraints.
   - `tools/retrieve_case.py`: Typed read tool with error mapping (`CASE_NOT_FOUND`, `INVALID_CASE_ID`, `UNAUTHORIZED`).
   - `tools/update_ticket.py`: Typed write tool requiring pre-approved token, idempotency key enforcement, and audit recording.
   - `tools/registry.py`: Centralized tool registry exposing JSON schemas to LLM.
3. **`security/` Subsystem:**
   - `security/auth.py`: JWT-based / Bearer authentication establishing caller identity.
   - `security/rbac.py`: Role-Based Access Control (`viewer`, `agent`, `manager`, `admin`) with deterministic application-level gatekeeping.
   - `security/access_aware_retrieval.py`: Access-aware policy filtering so unauthorized roles cannot retrieve or cite restricted policies (e.g. Executive compensation or confidential whistleblowing files).
   - `security/guardrails.py`: Prompt-injection detection, instruction/data boundary enforcement, and unsafe input sanitization.
4. **`observability/` Subsystem:**
   - `observability/correlation.py`: Correlation ID propagation across HTTP, workflow, tools, and DB.
   - `observability/events.py`: Structured domain lifecycle events.
   - `observability/tracer.py`: Lightweight OpenTelemetry-compatible span and trace collector.
   - `observability/metrics.py`: Latency timers, token/AI usage counters, and error rate collectors.
5. **CI/CD & Deployment:**
   - `.github/workflows/ci.yml`: Automated quality gates (linting, tests, build, quality checks).
   - Docker update supporting workflow and health/readiness endpoints (`/health` and `/ready`).
   - Runbook and rollback procedures (`docs/week4/runbook.md`, `docs/week4/rollback.md`).
