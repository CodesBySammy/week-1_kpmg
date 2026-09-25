# Week 5 Technical Baseline Report

## 1. Executive Summary

This baseline establishes the authoritative, pre-Week-5 operational and verification state of the Enterprise Case Management Platform. All metrics in this document represent actual measured test and coverage executions performed on Python 3.14.7 (win32) prior to applying any Week 5 architecture enhancements, failure injections, or scope modifications.

- **Baseline Test Count**: 143 passed, 0 failed, 0 errors.
- **Execution Duration**: 18.82 seconds.
- **Statement Code Coverage**: 90.63% (Threshold: >=70.0%).
- **Git Commit Baseline**: `1f83186` (Clean working tree, branch `main`).

---

## 2. Baseline Test Execution Results

```text
============================== test session starts ==============================
platform win32 -- Python 3.14.7, pytest-8.3.4, pluggy-1.5.0
rootdir: D:\week1_kpmg\case-management-backend
configfile: pyproject.toml
plugins: anyio-4.8.0, cov-6.0.0
collected 143 items

tests/api/test_cases_api.py ...............                              [ 10%]
tests/pipeline/test_audit.py .....                                       [ 13%]
tests/pipeline/test_data_contracts.py .....                              [ 17%]
tests/pipeline/test_layers.py ......                                     [ 21%]
tests/pipeline/test_orchestration.py ....                                [ 24%]
tests/pipeline/test_profiling.py ....                                    [ 27%]
tests/pipeline/test_quarantine.py .....                                  [ 30%]
tests/pipeline/test_reconciliation.py .....                              [ 34%]
tests/pipeline/test_transformations.py ....                              [ 37%]
tests/test_human_approval.py .....                                       [ 40%]
tests/test_observability.py ....                                         [ 43%]
tests/test_rag_api.py ........                                           [ 48%]
tests/test_rag_chunking.py ....                                          [ 51%]
tests/test_rag_context_generation.py ....                                [ 54%]
tests/test_rag_embeddings_indices.py ....                                [ 57%]
tests/test_rag_evaluation.py ...                                         [ 59%]
tests/test_rag_ingestion.py ......                                       [ 64%]
tests/test_rag_retrieval_rerank.py ..                                    [ 65%]
tests/test_security_guardrails.py .........                              [ 71%]
tests/test_security_rbac.py .....                                        [ 75%]
tests/test_tools_contracts.py .......                                    [ 80%]
tests/test_workflow_api.py .......                                       [ 85%]
tests/test_workflow_orchestration.py .....                               [ 88%]
tests/unit/test_case_repository.py .......                               [ 93%]
tests/unit/test_case_service.py .....                                    [ 97%]
tests/unit/test_models_and_schemas.py ...                                [100%]

====================== 143 passed, 62 warnings in 18.82s ======================
```

---

## 3. Code Coverage Breakdown

| Module | Statements | Missed | Coverage | Uncovered Lines |
|---|---|---|---|---|
| `app/api/__init__.py` | 0 | 0 | 100% | - |
| `app/api/routes/__init__.py` | 0 | 0 | 100% | - |
| `app/api/routes/cases.py` | 44 | 0 | 100% | - |
| `app/api/routes/mock_api.py` | 18 | 10 | 44% | 100-105, 111-114 |
| `app/api/routes/rag.py` | 41 | 0 | 100% | - |
| `app/api/routes/workflow.py` | 81 | 19 | 77% | 58, 81-82, 132-137, 148-164 |
| `app/config.py` | 16 | 0 | 100% | - |
| `app/database/session.py` | 27 | 4 | 85% | 97-101 |
| `app/exceptions/handlers.py` | 37 | 2 | 95% | 152-156 |
| `app/logging_config.py` | 19 | 1 | 95% | 88 |
| `app/main.py` | 50 | 4 | 92% | 146-148, 152 |
| `app/models/case.py` | 63 | 0 | 100% | - |
| `app/repositories/case_repository.py` | 70 | 12 | 83% | 59-65, 137-143, 160-166 |
| `app/schemas/case.py` | 28 | 0 | 100% | - |
| `app/services/case_service.py` | 43 | 0 | 100% | - |
| **TOTAL** | **555** | **52** | **90.63%** | - |

---

## 4. Existing Architecture Inventory (Weeks 1–4)

1. **Week 1 (OLTP Backend)**:
   - FastAPI REST API with structured Pydantic schemas, SQLAlchemy ORM, SQLite database with transactional isolation and audit logging (`AuditLog` entity tracking entity mutations).
   - CRUD operations for Cases, Users, and Audit trail with full pagination and status filtering.
2. **Week 2 (Data Pipeline & Lakehouse)**:
   - Medallion architecture (Raw -> Standardized -> Curated) with data quality contracts, schema enforcement, Great Expectations-style validation, quarantine routing, profiling, and financial reconciliation.
3. **Week 3 (Enterprise Grounded RAG)**:
   - Document ingestion and preprocessing (Markdown with frontmatter), multiple chunking strategies (Fixed, Recursive, Markdown-Section), hybrid indexing (Dense embeddings via deterministic SHA-256 projections + Sparse BM25), Cross-Score reranking, contextual assembly with strict token budgets, grounded answer generation, and policy evaluation metrics.
4. **Week 4 (Controlled Agentic Workflow & Production Readiness)**:
   - Typed tool contracts with Pydantic input/output schemas (`retrieve_case`, `update_ticket`), deterministic error taxonomy (`TOOL_INPUT_INVALID`, `RESOURCE_NOT_FOUND`, `APPROVAL_REQUIRED`), cryptographic HMAC-SHA256 human approval flow for consequential writes, stateful workflow orchestrator (LangGraph-style state machine), security guardrails (jailbreak/injection detection, input length sanitization, prompt isolation), RBAC with JWT claims and access-aware retrieval filtering, OpenTelemetry-compatible tracing, structured JSON logs with Correlation IDs, Prometheus metrics, Docker containerization, and automated rollback scripts.

---

## 5. Known Limitations & Technical Debt Prior to Week 5

1. **Synchronous Execution Pipeline**: Background workflow runs synchronously inside request threads; large batches or slow external LLMs could saturate FastAPI worker pools.
2. **Deterministic Hash Embeddings**: Dense vector provider uses a deterministic 128-dimensional projection for offline testing rather than an external HuggingFace / OpenAI embedding server.
3. **In-Memory Approvals Store**: Human-in-the-loop approval tickets are persisted in SQLite and cached in-memory without a distributed Redis lock.
4. **Mock Upstream Endpoints**: Upstream CRM sync endpoints in `mock_api.py` run in-process for simulation purposes.
5. **Single-Tenant Database**: SQLite database used for portable testability; multi-region PostgreSQL requires connection pooling configuration.

---

## 6. Components Extended in Week 5

| Layer | Component | Extension Scope |
|---|---|---|
| **Data / Domain** | `app/models/case.py`, `app/schemas/case.py` | Scope Change: Add `escalation_tier` (`STANDARD`, `PRIORITY`, `CRITICAL_ESC`), `department` field, SLA calculation, and validation rules. |
| **Workflow / Orchestration** | `workflow/orchestrator.py`, `workflow/router.py` | Support escalated workflows, priority escalation tokens, department-scoped execution. |
| **Tools** | `tools/ticket_tool.py`, `tools/case_tool.py` | Extended validation for escalation tiers and multi-department case modifications. |
| **Security** | `security/rbac.py`, `security/guardrails.py` | Department-based access boundary, enhanced adversarial red-team testing. |
| **Testing** | `tests/` | Comprehensive test hierarchy: E2E (E2E-001 to E2E-010), negative tests, security red-team tests, failure scenarios (INCIDENT 01-08), performance and reliability benchmarks. |
| **Operations** | `release/`, `docs/week5/` | Complete release candidate (v1.0.0-rc1), operations runbook, known-limitations register, and handover package. |
