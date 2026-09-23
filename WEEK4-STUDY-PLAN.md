# Week 4 — 5-Day Study & Mastery Plan

> **Program:** FDE Fresher Readiness Program — Week 4  
> **Topic:** Controlled AI Workflows, Tool Integrations, Security & Production Engineering  
> **Methodology:** LEARN → PRACTICE → BUILD → TEST → SECURE → OBSERVE → DEPLOY → REVIEW

---

## Daily Schedule Breakdown

### Day 1: Typed AI Tools, Schemas & Deterministic Error Contracts
- **LEARN:** Understand why untyped LLM function calls cause production outages and silent data corruption. Study strict Pydantic models for inputs and outputs, deterministic error classifications (`ToolError`), and retryable vs non-retryable errors.
- **PRACTICE:** Read [`docs/week4/tool-contracts.md`](file:///d:/week1_kpmg/case-management-backend/docs/week4/tool-contracts.md) and [`learning/week4/week4-curriculum.md`](file:///d:/week1_kpmg/case-management-backend/learning/week4/week4-curriculum.md). 
- **BUILD:** Inspect [`tools/schemas.py`](file:///d:/week1_kpmg/case-management-backend/tools/schemas.py), [`tools/retrieve_case.py`](file:///d:/week1_kpmg/case-management-backend/tools/retrieve_case.py), and [`tools/update_ticket.py`](file:///d:/week1_kpmg/case-management-backend/tools/update_ticket.py). Understand how `IdempotencyStore` guarantees replay safety.
- **TEST:** Run `.\venv\Scripts\python -m pytest tests/test_tools_contracts.py -v`.

---

### Day 2: Stateful Workflow Orchestration & Human Approval (HITL)
- **LEARN:** Master Finite State Machines for Agentic workflows: `REQUEST_RECEIVED` $\rightarrow$ `INTENT_DETECTED` $\rightarrow$ `TOOL_PROPOSED` $\rightarrow$ `APPROVAL_REQUIRED` $\rightarrow$ `APPROVED` $\rightarrow$ `EXECUTING` $\rightarrow$ `COMPLETED`. Understand why AI models must NEVER unilaterally execute consequential write operations.
- **PRACTICE:** Study [`workflow/state.py`](file:///d:/week1_kpmg/case-management-backend/workflow/state.py) and [`workflow/approval.py`](file:///d:/week1_kpmg/case-management-backend/workflow/approval.py). Trace the token generation, reviewer signing, and TTL expiration mechanics.
- **BUILD:** Review [`workflow/router.py`](file:///d:/week1_kpmg/case-management-backend/workflow/router.py) and [`workflow/orchestrator.py`](file:///d:/week1_kpmg/case-management-backend/workflow/orchestrator.py). Observe exponential backoff retries and fallback handlers.
- **TEST:** Run `.\venv\Scripts\python -m pytest tests/test_workflow_orchestration.py tests/test_human_approval.py -v`.

---

### Day 3: Security Guardrails, RBAC & Access-Aware Retrieval
- **LEARN:** Understand why system prompts are NOT security boundaries. Study HMAC-SHA256 bearer token authentication, Role-Based Access Control (`viewer`, `agent`, `manager`, `admin`), regex injection defenses, delimiter isolation, and access-aware retrieval filtering.
- **PRACTICE:** Inspect [`security/auth.py`](file:///d:/week1_kpmg/case-management-backend/security/auth.py), [`security/rbac.py`](file:///d:/week1_kpmg/case-management-backend/security/rbac.py), [`security/guardrails.py`](file:///d:/week1_kpmg/case-management-backend/security/guardrails.py), and [`security/access_aware_retrieval.py`](file:///d:/week1_kpmg/case-management-backend/security/access_aware_retrieval.py).
- **BUILD:** Test prompt injection sanitization against adversarial attack vectors (e.g., "Ignore all previous instructions").
- **TEST:** Run `.\venv\Scripts\python -m pytest tests/test_security_guardrails.py tests/test_security_rbac.py -v`.

---

### Day 4: Production Observability, Tracing & Workflow API
- **LEARN:** Study enterprise SRE fundamentals: distributed context propagation with `X-Correlation-ID`, structured JSON logging, OpenTelemetry-compatible span tracing, and latency/token consumption metrics.
- **PRACTICE:** Inspect [`observability/correlation.py`](file:///d:/week1_kpmg/case-management-backend/observability/correlation.py), [`observability/events.py`](file:///d:/week1_kpmg/case-management-backend/observability/events.py), [`observability/tracer.py`](file:///d:/week1_kpmg/case-management-backend/observability/tracer.py), and [`observability/metrics.py`](file:///d:/week1_kpmg/case-management-backend/observability/metrics.py).
- **BUILD:** Explore the FastAPI endpoints in [`app/api/routes/workflow.py`](file:///d:/week1_kpmg/case-management-backend/app/api/routes/workflow.py): `/execute`, `/approvals`, `/health`, and `/ready`.
- **TEST:** Run `.\venv\Scripts\python -m pytest tests/test_observability.py tests/test_workflow_api.py -v`.

---

### Day 5: CI/CD Release Gates, Runbooks & Capstone Mastery
- **LEARN:** Study deployment safety: automated release gates, canary rollouts, rollback runbooks, and incident post-mortems.
- **PRACTICE:** Review [`docs/week4/release-gates.md`](file:///d:/week1_kpmg/case-management-backend/docs/week4/release-gates.md), [`docs/week4/runbook.md`](file:///d:/week1_kpmg/case-management-backend/docs/week4/runbook.md), and [`docs/week4/rollback.md`](file:///d:/week1_kpmg/case-management-backend/docs/week4/rollback.md).
- **VERIFY:** Execute the full test suite with coverage enforcement:  
  `.\venv\Scripts\python -m pytest --cov=tools --cov=workflow --cov=security --cov=observability tests/`  
  Ensure **143 tests pass** and coverage exceeds **80%**.
- **CAPSTONE REVIEW:** Complete the Week 4 interview questions and verify requirements against [`docs/week4-requirement-traceability.md`](file:///d:/week1_kpmg/case-management-backend/docs/week4-requirement-traceability.md).
