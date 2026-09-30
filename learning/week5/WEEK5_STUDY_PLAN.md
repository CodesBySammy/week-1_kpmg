# Week 5 Capstone: 10-Day Structured Study Plan

A daily roadmap to mastering enterprise integration, failure hardening, red-teaming, and handover engineering.

---

## Day 1: Technical Discovery & Baseline Verification
- **Objectives**: Master client discovery methodologies; run and verify the baseline test suite.
- **Reading**: `learning/week5/00_WEEK5_OVERVIEW.md`, `01_TECHNICAL_DISCOVERY.md`, `03_CURRENT_STATE_ANALYSIS.md`.
- **Hands-On Lab**: `learning/week5/labs/LAB-01-TECHNICAL-DISCOVERY.md`.
- **Artifacts**: Inspect `docs/week5/WEEK5_BASELINE.md` and `docs/week5/client-engagement/TECHNICAL_DISCOVERY.md`.
- **Verification**: Run `pytest tests/` and verify all tests pass.

## Day 2: Structured Requirements & Architectural Modeling
- **Objectives**: Translate client discovery into testable requirements; model cross-layer architectures with Mermaid.
- **Reading**: `learning/week5/02_REQUIREMENTS_ENGINEERING.md`, `04_SYSTEM_ARCHITECTURE.md`, `05_COMPONENT_DIAGRAMS.md`, `06_SEQUENCE_DIAGRAMS.md`.
- **Hands-On Lab**: `learning/week5/labs/LAB-02-ARCHITECTURE-DESIGN.md`.
- **Artifacts**: Review `docs/week5/architecture/COMPONENT_DIAGRAM.md` and `SEQUENCE_DIAGRAMS.md`.
- **Verification**: Trace request paths through component and sequence diagrams.

## Day 3: Backlog Decomposition & Vertical Slicing
- **Objectives**: Decompose feature epics into end-to-end vertical slices with observable acceptance criteria.
- **Reading**: `learning/week5/07_DATA_FLOW.md`, `08_BACKLOG_DECOMPOSITION.md`, `09_VERTICAL_SLICES.md`, `10_ACCEPTANCE_CRITERIA.md`.
- **Hands-On Lab**: `learning/week5/labs/LAB-03-BACKLOG-DECOMPOSITION.md`.
- **Artifacts**: Inspect `docs/week5/backlog/TECHNICAL_BACKLOG.md` and `ACCEPTANCE_CRITERIA.md`.
- **Verification**: Run `pytest tests/e2e/test_scope_change_escalation.py`.

## Day 4: Testing Hierarchy & Negative Path Hardening
- **Objectives**: Implement robust negative path, integration, and regression testing strategies.
- **Reading**: `learning/week5/11_END_TO_END_TESTING.md`, `12_INTEGRATION_TESTING.md`, `13_REGRESSION_TESTING.md`, `14_NEGATIVE_PATH_TESTING.md`.
- **Hands-On Lab**: `learning/week5/labs/LAB-04-NEGATIVE-TESTING.md`.
- **Artifacts**: Review `docs/week5/testing/REGRESSION_STRATEGY.md`.
- **Verification**: Run `pytest tests/negative/test_negative_paths.py` and `tests/regression/test_regression_suite.py`.

## Day 5: Red-Team Security & Adversarial Evaluation
- **Objectives**: Execute adversarial testing across prompt injection, privilege escalation, malformed data, and unsafe tools.
- **Reading**: `learning/week5/15_RED_TEAM_TESTING.md` through `19_UNSAFE_TOOL_REQUESTS.md`.
- **Hands-On Lab**: `learning/week5/labs/LAB-05-RED-TEAM-TESTING.md`.
- **Artifacts**: Review `docs/week5/security/THREAT_MODEL.md` and `RED_TEAM_RESULTS.md`.
- **Verification**: Run `pytest tests/security/test_red_team_suite.py` (16 passed).

## Day 6: Failure Injection, Troubleshooting & Recovery
- **Objectives**: Seed cross-layer faults, trace correlation IDs, and verify self-healing state transitions.
- **Reading**: `learning/week5/21_RELIABILITY_TESTING.md`, `22_FAILURE_RECOVERY.md`.
- **Hands-On Lab**: `learning/week5/labs/LAB-06-FAILURE-TROUBLESHOOTING.md`.
- **Artifacts**: Review `docs/week5/failures/FAILURE_CATALOG.md` and incidents 1 through 8.
- **Verification**: Run `pytest tests/failure-scenarios/test_failure_scenarios.py` (15 passed).

## Day 7: Performance Benchmarking & Controlled Scope Change
- **Objectives**: Measure p50/p95/p99 latencies; evaluate and implement mid-project scope changes.
- **Reading**: `learning/week5/20_PERFORMANCE_TESTING.md`, `23_SCOPE_CHANGE_MANAGEMENT.md`, `24_TECHNICAL_DECISION_RECORDS.md`.
- **Hands-On Lab**: `learning/week5/labs/LAB-07-PERFORMANCE-TESTING.md`, `LAB-08-SCOPE-CHANGE.md`.
- **Artifacts**: Review `docs/week5/testing/PERFORMANCE_BENCHMARKS.md` and `docs/week5/scope-change/IMPACT_ASSESSMENT.md`.
- **Verification**: Run `pytest tests/performance/test_performance_benchmarks.py`.

## Day 8: Production-Readiness & Known Limitations Audit
- **Objectives**: Conduct formal Production-Readiness Review (PRR) and audit system debt.
- **Reading**: `learning/week5/25_PRODUCTION_READINESS.md`, `26_KNOWN_LIMITATIONS.md`.
- **Hands-On Lab**: `learning/week5/labs/LAB-09-PRODUCTION-READINESS.md`.
- **Artifacts**: Review `docs/week5/production-readiness/PRODUCTION_READINESS_CHECKLIST.md` and `KNOWN_LIMITATIONS.md`.
- **Verification**: Audit all checklist evidence references against code.

## Day 9: Release Packaging, Deployment & Rollback Drills
- **Objectives**: Tag release candidate v1.0.0-rc1, verify health probes, and execute rollback drills.
- **Reading**: Review deployment, configuration, and rollback guides.
- **Artifacts**: Inspect `release/VERSION.md`, `RELEASE_NOTES.md`, and `docs/week5/deployment/ROLLBACK_PROCEDURE.md`.
- **Verification**: Probe `/health/live` and `/health/ready` endpoints.

## Day 10: Technical Demonstration & Knowledge Transfer Handover
- **Objectives**: Rehearse live 18-step technical demonstration; complete handover package.
- **Reading**: `learning/week5/27_TECHNICAL_DEMONSTRATION.md`, `28_KNOWLEDGE_TRANSFER.md`, `29_HANDOVER.md`.
- **Hands-On Lab**: `learning/week5/labs/LAB-10-HANDOVER.md`.
- **Artifacts**: Review `docs/week5/demo/DEMO_SCRIPT.md` and `docs/week5/handover/HANDOVER_GUIDE.md`.
- **Verification**: Execute full self-assessment in `learning/week5/SELF_ASSESSMENT.md`.
