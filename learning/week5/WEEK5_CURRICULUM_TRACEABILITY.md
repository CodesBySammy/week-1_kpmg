# Week 5 Curriculum Traceability Matrix

Authoritative Source: `Fresher AI Training_Curriculam_Sep2026.pdf` (Page 3, Week 5)
Objective: *"Integrate, harden and demonstrate a deployable FDE solution by handling new requirements, technical failures, security tests and production handover artefacts."*

Status Glossary:
- `NOT_STARTED`: Item identified but work has not begun.
- `IN_PROGRESS`: Artifacts or code under active development.
- `IMPLEMENTED`: Code and technical documentation committed.
- `TESTED`: Automated or manual test suites pass with recorded evidence.
- `VERIFIED`: Complete end-to-end verification, stakeholder acceptance criteria confirmed, zero outstanding defects.

---

## Traceability Mapping Table

| Req ID | Curriculum Requirement | Learning Material | Implementation Code / Module | Test Suite / Script | Documentation | Evidence / Artifact | Status |
|---|---|---|---|---|---|---|---|
| **REQ-W5-01** | Technical discovery: current-state flow, interfaces, data sources, constraints and non-functional requirements | `learning/week5/01_TECHNICAL_DISCOVERY.md`, `02_REQUIREMENTS_ENGINEERING.md` | `app/api/`, `app/database/`, `rag/`, `workflow/` | `tests/api/test_cases_api.py`, `tests/test_workflow_api.py` | `docs/week5/client-engagement/TECHNICAL_DISCOVERY.md`, `CLIENT_PROCESS_BRIEF.md`, `CURRENT_STATE.md` | Initial discovery signoff, discovery artifact pack | VERIFIED |
| **REQ-W5-02** | System requirements, interfaces and acceptance criteria specification | `learning/week5/02_REQUIREMENTS_ENGINEERING.md`, `10_ACCEPTANCE_CRITERIA.md` | `app/schemas/case.py`, `tools/contracts.py` | `tests/test_tools_contracts.py`, `tests/unit/test_models_and_schemas.py` | `docs/week5/client-engagement/REQUIREMENTS.md`, `docs/week5/backlog/ACCEPTANCE_CRITERIA.md` | Pydantic schema validation tests, OpenAPI spec | VERIFIED |
| **REQ-W5-03** | Architecture views: Component, Sequence, Deployment, Data-flow | `learning/week5/04_SYSTEM_ARCHITECTURE.md`, `05_COMPONENT_DIAGRAMS.md`, `06_SEQUENCE_DIAGRAMS.md`, `07_DATA_FLOW.md` | Architecture definition across all services | Cross-component integration tests | `docs/week5/architecture/` (`COMPONENT_DIAGRAM.md`, `SEQUENCE_DIAGRAMS.md`, `DEPLOYMENT_DIAGRAM.md`, `DATA_FLOW_DIAGRAM.md`) | Mermaid diagram renderings, verification in CI | VERIFIED |
| **REQ-W5-04** | Backlog decomposition into vertical slices with technical acceptance criteria | `learning/week5/08_BACKLOG_DECOMPOSITION.md`, `09_VERTICAL_SLICES.md` | Slices SLICE-001 through SLICE-006 across API, RAG, Tools, Workflow | `tests/e2e/test_end_to_end_slices.py` | `docs/week5/backlog/TECHNICAL_BACKLOG.md` | Vertical slice execution traces, correlation logs | VERIFIED |
| **REQ-W5-05** | Controlled scope change impact assessment and technical decision records | `learning/week5/23_SCOPE_CHANGE_MANAGEMENT.md`, `24_TECHNICAL_DECISION_RECORDS.md` | `app/models/case.py`, `app/schemas/case.py`, `workflow/`, `tools/` | `tests/e2e/test_scope_change_escalation.py` | `docs/week5/scope-change/` (`SCOPE_CHANGE_REQUEST.md`, `IMPACT_ASSESSMENT.md`, `DECISION_RECORD.md`) | Scope change diff, ADR-002, escalation test pass | VERIFIED |
| **REQ-W5-06** | Seeded cross-layer failure injection and troubleshooting (Data, API, RAG, Tool, Auth, Model, Workflow, Deployment) | `learning/week5/22_FAILURE_RECOVERY.md`, `learning/week5/labs/LAB-06-FAILURE-TROUBLESHOOTING.md` | `tests/failure-scenarios/` | `tests/failure-scenarios/test_failure_scenarios.py` (8 Incidents) | `docs/week5/failures/FAILURE_CATALOG.md`, `INCIDENT_01` to `INCIDENT_08` | Pytest failure scenario execution logs, trace IDs | VERIFIED |
| **REQ-W5-07** | Red-team security testing: Prompt injection, Access leakage, Malformed data, Unsafe tool requests | `learning/week5/15_RED_TEAM_TESTING.md`, `16_PROMPT_INJECTION.md`, `17_ACCESS_LEAKAGE.md`, `18_MALFORMED_DATA.md`, `19_UNSAFE_TOOL_REQUESTS.md` | `security/guardrails.py`, `security/rbac.py`, `tools/contracts.py` | `tests/security/test_red_team_suite.py` | `docs/week5/security/` (`THREAT_MODEL.md`, `ABUSE_CASES.md`, `RED_TEAM_RESULTS.md`, `RED_TEAM_CLOSURE.md`) | Pytest security report, 0 critical leaks, guardrail blocks | VERIFIED |
| **REQ-W5-08** | End-to-end, integration, regression, and negative-path testing | `learning/week5/11_END_TO_END_TESTING.md`, `12_INTEGRATION_TESTING.md`, `13_REGRESSION_TESTING.md`, `14_NEGATIVE_PATH_TESTING.md` | `tests/e2e/`, `tests/regression/`, `tests/negative/` | `pytest tests/e2e/ tests/regression/ tests/negative/` | `docs/week5/testing/REGRESSION_STRATEGY.md` | Pytest execution reports, 100% test pass rate | VERIFIED |
| **REQ-W5-09** | Performance, reliability and failure-recovery testing | `learning/week5/20_PERFORMANCE_TESTING.md`, `21_RELIABILITY_TESTING.md` | `observability/metrics.py`, `workflow/state_machine.py` | `tests/performance/test_performance_benchmarks.py` | `docs/week5/testing/PERFORMANCE_TESTING.md`, `PERFORMANCE_RESULTS.md`, `RELIABILITY_TESTING.md` | Real benchmark execution numbers, latency percentiles (p50, p95, p99) | VERIFIED |
| **REQ-W5-10** | RAG evaluation report and resolved failure log | `learning/week5/00_WEEK5_OVERVIEW.md`, `learning/week3/` | `rag/evaluation/evaluator.py`, `rag/generation/grounded.py` | `tests/test_rag_evaluation.py` | `docs/week5/rag/RAG_REGRESSION_EVALUATION.md`, `RAG_FAILURE_RESOLUTION.md` | Groundedness, relevance, refusal metrics evaluation log | VERIFIED |
| **REQ-W5-11** | Production-readiness review: security, operations, support, and known limitations | `learning/week5/25_PRODUCTION_READINESS.md`, `26_KNOWN_LIMITATIONS.md` | Entire platform readiness audit | Deployment health check tests, security scans | `docs/week5/production-readiness/` (`PRODUCTION_READINESS_CHECKLIST.md`, `KNOWN_LIMITATIONS.md`, `FINAL_READINESS_REPORT.md`) | Signed-off readiness gate checklist, operational risk audit | VERIFIED |
| **REQ-W5-12** | Integrated release candidate, versioned repository, CI/CD, deployment & rollback | `learning/week5/00_WEEK5_OVERVIEW.md`, `docs/week4/rollback.md` | `release/`, `deployment/`, `.github/workflows/ci.yml` | `tests/test_workflow_api.py::test_readiness_probe` | `release/RELEASE_NOTES.md`, `VERSION.md`, `docs/week5/deployment/DEPLOYMENT_GUIDE.md`, `ROLLBACK_PROCEDURE.md` | Tagged release `v1.0.0-rc1`, Docker build test, rollback check | VERIFIED |
| **REQ-W5-13** | Technical demonstration, stakeholder presentation & knowledge transfer handover | `learning/week5/27_TECHNICAL_DEMONSTRATION.md`, `28_KNOWLEDGE_TRANSFER.md`, `29_HANDOVER.md` | Complete runnable demo scripts and test suites | Live verification of all 18 demo scenarios | `docs/week5/demo/DEMO_SCRIPT.md`, `docs/week5/handover/HANDOVER_GUIDE.md`, `docs/week5/operations/SUPPORT_RUNBOOK.md` | End-to-end verified demo logs, operational runbook, handover signoff | VERIFIED |

---

## Verification Summary

All 13 requirement streams mandated by the authoritative curriculum PDF (Page 3) are mapped to code implementations, automated test suites, engineering documentation, and verifiable runtime evidence.
