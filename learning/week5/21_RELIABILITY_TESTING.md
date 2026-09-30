# Module 21: Reliability, Resilience & Fault Tolerance

## 1. Simple Explanation
Reliability engineering verifies that a system maintains uninterrupted service, recovers gracefully from transient dependency failures, and avoids cascading outages.

## 2. Why It Matters
In Forward Deployed Engineering (FDE), raw prototype code is never sufficient for production client environments. Engineering deliverables must withstand non-happy-path real-world conditions, stringent enterprise compliance, organizational scope modifications, and architectural integration audits.

## 3. Key Concepts & Terminology
- **Primary Concept**: Reliability, Resilience & Fault Tolerance provides the structural foundation for engineering predictability and system hardening.
- **Traceability**: Direct correlation between business problem statements, functional requirements, code implementations, automated verification tests, and operational telemetry.
- **Fail-Safe Determinism**: System state transitions and authorization checks must be deterministic, governed by verified application logic rather than stochastic model inference.
- **Operational Readiness**: A system is only ready for handover when observability, recovery runbooks, and failure mitigations are codified and tested.

## 4. Architecture & Technical Design
```text
Component Outage (LLM Down / DB Lock) -> Circuit Breaker / Timeout -> Fallback Path Activated -> Graceful Response + Telemetry
```

## 5. Project-Specific Implementation
Verified in `tests/failure-scenarios/test_failure_scenarios.py`: when mock LLM inference fails, the system falls back to a deterministic degraded policy message rather than returning HTTP 500.

## 6. Code & Module Mapping
- **Implementation File(s)**: `workflow/orchestrator.py, rag/generation/generator.py`
- **Test File(s)**: `tests/failure-scenarios/test_failure_scenarios.py`
- **Documentation Reference**: `docs/week5/testing/RELIABILITY_TESTING.md`

## 7. Common Pitfalls & Mistakes
- Unbounded network timeouts that block threads indefinitely when external services hang.
- Failing to release database connections during exception handling, leading to pool exhaustion.

## 8. Troubleshooting & Diagnostic Guide
Simulate an external dependency failure and verify that client receives a graceful HTTP 503 or cached fallback.

## 9. Interview Questions & Detailed Answers
### Q1: What is the difference between fault tolerance and graceful degradation?
**Answer**: Fault tolerance means the system continues functioning with zero user-visible impairment. Graceful degradation means non-critical features (like AI reasoning) step down to canned fallbacks while core business operations continue.

### Q2: How does the state machine handle retry exhaustion?
**Answer**: After reaching max retries, the state machine transitions cleanly from `EXECUTING` to `FAILED` and records an audit log entry.

## 10. Practical Hands-On Exercise
Review `INCIDENT_06_MODEL_FAILURE.md`.
