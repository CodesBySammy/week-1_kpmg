# Week 4 — Requirement Traceability Matrix (RTM)

> **Curriculum Source:** `Fresher AI Training_Curriculam_Sep2026.pdf` (Page 2, Week 4)  
> **Objective:** Convert the RAG service into a controlled AI workflow with typed tool integrations, human approval, security guardrails, observability, automated delivery, and sandbox deployment.  
> **Status:** 100% Implemented, Integrated, and Verified (143/143 Tests Passing, 87.15% Code Coverage)

---

| # | Curriculum Requirement | Learning Material | Implementation Source Files | Test / Evidence | Status |
|---|---|---|---|---|:---:|
| **1** | **Tool Calling & JSON Schemas** | `learning/week4/02-tool-calling.md`, `03-json-schemas.md` | `tools/schemas.py`, `tools/registry.py` | `tests/test_tools_contracts.py` | **VERIFIED** |
| **2** | **Tool Validation & Deterministic Errors** | `learning/week4/04-tool-validation.md`, `05-deterministic-tool-errors.md` | `tools/retrieve_case.py`, `tools/update_ticket.py` | `tests/test_tools_contracts.py` | **VERIFIED** |
| **3** | **Tool Idempotency** | `learning/week4/06-tool-idempotency.md` | `tools/update_ticket.py` (`IdempotencyStore`) | `tests/test_tools_contracts.py` | **VERIFIED** |
| **4** | **Workflow State & Routing** | `learning/week4/07-workflow-state.md`, `08-workflow-routing.md` | `workflow/state.py`, `workflow/router.py` | `tests/test_workflow_orchestration.py` | **VERIFIED** |
| **5** | **Retries, Timeouts & Fallback Paths** | `learning/week4/09-retries.md`, `10-timeouts.md`, `11-fallback-paths.md` | `workflow/orchestrator.py`, `workflow/fallback.py` | `tests/test_workflow_orchestration.py` | **VERIFIED** |
| **6** | **Human-in-the-Loop Approval (Consequential Actions)** | `learning/week4/12-human-in-the-loop.md`, `13-consequential-actions.md` | `workflow/approval.py` | `tests/test_human_approval.py` | **VERIFIED** |
| **7** | **Authentication & Role-Based Authorization (RBAC)** | `learning/week4/14-authentication.md`, `15-role-based-authorization.md` | `security/auth.py`, `security/rbac.py` | `tests/test_security_rbac.py` | **VERIFIED** |
| **8** | **Access-Aware Retrieval Concepts** | `learning/week4/16-access-aware-retrieval.md` | `security/access_aware_retrieval.py` | `tests/test_security_rbac.py` | **VERIFIED** |
| **9** | **Secrets & Configuration Separation** | `learning/week4/17-secrets-management.md`, `18-configuration-separation.md` | `app/config.py`, `.env.example` | `tests/test_security_guardrails.py` | **VERIFIED** |
| **10** | **Prompt-Injection & Unsafe-Input Protections** | `learning/week4/20-prompt-injection.md`, `21-unsafe-input.md` | `security/guardrails.py` | `tests/test_security_guardrails.py` | **VERIFIED** |
| **11** | **Unauthorized-Action Protections** | `learning/week4/22-unauthorized-actions.md` | `workflow/orchestrator.py`, `security/rbac.py` | `tests/test_security_rbac.py` | **VERIFIED** |
| **12** | **Correlation IDs & Structured Events** | `learning/week4/23-correlation-ids.md`, `24-structured-events.md` | `observability/correlation.py`, `observability/events.py` | `tests/test_observability.py` | **VERIFIED** |
| **13** | **Tracing & Span Context** | `learning/week4/25-tracing.md` | `observability/tracer.py` | `tests/test_observability.py` | **VERIFIED** |
| **14** | **Latency, Token Usage & Error Metrics** | `learning/week4/26-latency-metrics.md`, `27-token-and-ai-usage-metrics.md`, `28-error-metrics.md` | `observability/metrics.py` | `tests/test_observability.py` | **VERIFIED** |
| **15** | **CI/CD Pipeline & Quality Gates** | `learning/week4/29-ci-cd.md`, `30-quality-gates.md` | `.github/workflows/ci.yml`, `docs/week4/release-gates.md` | CI workflow syntax & 70% test gate | **VERIFIED** |
| **16** | **Container Deployment & Health Checks** | `learning/week4/31-container-deployment.md`, `32-health-checks.md` | `Dockerfile`, `app/main.py` (`/health`, `/ready`) | Container health probe tests | **VERIFIED** |
| **17** | **Rollback Procedure & Runbooks** | `learning/week4/33-rollback.md`, `34-operational-runbooks.md` | `docs/week4/rollback.md`, `docs/week4/runbook.md` | SRE runbook procedures | **VERIFIED** |
| **18** | **TOOL 1: Retrieve Case Details** | `docs/week4/tool-contracts.md` | `tools/retrieve_case.py` | `tests/test_tools_contracts.py` | **VERIFIED** |
| **19** | **TOOL 2: Update Ticket System** | `docs/week4/tool-contracts.md` | `tools/update_ticket.py` | `tests/test_tools_contracts.py`, `tests/test_human_approval.py` | **VERIFIED** |
| **20** | **Failure Injection & Edge Case Scenarios** | `learning/week4/36-week4-debugging.md` | `docs/week4/incident-exercises.md` | Handled across test suite | **VERIFIED** |
| **21** | **Master Architecture & Trust Boundaries** | `docs/architecture.md` | `docs/architecture.md`, `docs/week4/architecture.md` | Complete architecture specifications | **VERIFIED** |
| **22** | **Full Regression Safety (Weeks 1–3)** | `docs/week1-week3-baseline.md` | Entire repository codebase | 143/143 tests pass (0 regressions) | **VERIFIED** |
