# Release Notes — Version 1.0.0-rc1 (Week 5 Final Handover)

## Release Overview
Version 1.0.0-rc1 marks the culmination of the 5-Week FDE Fresher Readiness Program. This release unites the Week 1 CRUD backend, Week 2 lakehouse data pipeline, Week 3 grounded RAG system, Week 4 controlled agentic workflows, and Week 5 integration hardening, adversarial security testing, and production handover artifacts into a single enterprise-ready deliverable.

## Key Features & Enhancements
- **Weeks 1–4 Core Integration**: Unified REST API, medallion data pipeline, hybrid RAG with citations, and stateful LangGraph-style workflow engine.
- **Week 5 Controlled Scope Change**:
  - Implemented `escalation_tier` (`STANDARD`, `PRIORITY`, `CRITICAL_ESC`) and `department` fields on cases.
  - Added strict RBAC rules: only `supervisor` and `admin` roles can set `CRITICAL_ESC`.
  - Enforced departmental data isolation across queries.
- **Week 5 Failure Hardening**:
  - Seeded and mitigated 8 cross-layer incident scenarios (data, API, RAG, tool, auth, model, workflow, deployment).
- **Week 5 Red-Team Security Hardening**:
  - 16 adversarial penetration tests covering prompt injection, access leakage, malformed payloads, and unauthorized tool calls.
- **Week 5 Performance & Reliability**:
  - Comprehensive benchmarking suite verifying p95 latencies under SLAs.
- **Handover & Operational Documentation**:
  - 12 comprehensive handover guides, 29 learning modules, 10 labs, and a full support runbook.

## Verification Evidence
- **Automated Test Results**: 221 passed, 0 failed.
- **Git Branch**: `main`
- **Tag**: `v1.0.0-rc1`
