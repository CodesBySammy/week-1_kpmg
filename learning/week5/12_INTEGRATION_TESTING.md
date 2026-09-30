# Module 12: Cross-Layer Integration Testing

## 1. Simple Explanation
Integration testing focuses on the interfaces and interactions between adjacent modules (e.g., API router to domain service, domain service to repository, workflow to tool contract).

## 2. Why It Matters
In Forward Deployed Engineering (FDE), raw prototype code is never sufficient for production client environments. Engineering deliverables must withstand non-happy-path real-world conditions, stringent enterprise compliance, organizational scope modifications, and architectural integration audits.

## 3. Key Concepts & Terminology
- **Primary Concept**: Cross-Layer Integration Testing provides the structural foundation for engineering predictability and system hardening.
- **Traceability**: Direct correlation between business problem statements, functional requirements, code implementations, automated verification tests, and operational telemetry.
- **Fail-Safe Determinism**: System state transitions and authorization checks must be deterministic, governed by verified application logic rather than stochastic model inference.
- **Operational Readiness**: A system is only ready for handover when observability, recovery runbooks, and failure mitigations are codified and tested.

## 4. Architecture & Technical Design
```text
Module A (API) <-> Interface Contract <-> Module B (Service) <-> Persistence Contract <-> Module C (Database)
```

## 5. Project-Specific Implementation
`tests/api/test_cases_api.py` and `tests/test_tools_contracts.py` test integration between FastAPI request bodies, Pydantic tool schemas, and SQLAlchemy case models.

## 6. Code & Module Mapping
- **Implementation File(s)**: `app/api/cases.py, tools/update_ticket.py`
- **Test File(s)**: `tests/api/test_cases_api.py`
- **Documentation Reference**: `docs/week5/testing/REGRESSION_STRATEGY.md`

## 7. Common Pitfalls & Mistakes
- Over-mocking: mocking the database, the repository, and the schema until no real integration is actually tested.
- Ignoring serialization edge cases such as datetime timezone handling.

## 8. Troubleshooting & Diagnostic Guide
Execute tests with real SQLite test databases and verify actual table writes.

## 9. Interview Questions & Detailed Answers
### Q1: What distinguishes integration testing from E2E testing?
**Answer**: Integration tests verify specific pairwise component contracts (e.g. service + database), while E2E tests exercise the complete path from the public API entry point through all subsystems.

### Q2: Why must tool contracts be rigorously integration-tested in agentic AI architectures?
**Answer**: Because LLM tool-calling engines produce structured JSON; if the tool contract validation is loose, malformed arguments could corrupt the database or trigger unhandled server exceptions.

## 10. Practical Hands-On Exercise
Run `pytest tests/test_tools_contracts.py -v`.
