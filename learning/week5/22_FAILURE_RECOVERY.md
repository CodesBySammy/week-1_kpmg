# Module 22: Failure Recovery & Self-Healing State Machines

## 1. Simple Explanation
Failure recovery mechanisms enable systems to detect abnormal states, safely roll back in-flight transactions, and transition state machines into well-defined recovery states.

## 2. Why It Matters
In Forward Deployed Engineering (FDE), raw prototype code is never sufficient for production client environments. Engineering deliverables must withstand non-happy-path real-world conditions, stringent enterprise compliance, organizational scope modifications, and architectural integration audits.

## 3. Key Concepts & Terminology
- **Primary Concept**: Failure Recovery & Self-Healing State Machines provides the structural foundation for engineering predictability and system hardening.
- **Traceability**: Direct correlation between business problem statements, functional requirements, code implementations, automated verification tests, and operational telemetry.
- **Fail-Safe Determinism**: System state transitions and authorization checks must be deterministic, governed by verified application logic rather than stochastic model inference.
- **Operational Readiness**: A system is only ready for handover when observability, recovery runbooks, and failure mitigations are codified and tested.

## 4. Architecture & Technical Design
```text
State: EXECUTING -> Exception Encountered -> DB Rollback -> State: FAILED / CANCELLED -> Error Emitted
```

## 5. Project-Specific Implementation
Implemented in `workflow/state.py` and `workflow/orchestrator.py`: if a tool fails or an approval token is invalid, the orchestrator transitions state to `FAILED` or `APPROVAL_REJECTED`.

## 6. Code & Module Mapping
- **Implementation File(s)**: `workflow/state.py, workflow/orchestrator.py`
- **Test File(s)**: `tests/failure-scenarios/test_failure_scenarios.py`
- **Documentation Reference**: `docs/week5/failures/FAILURE_SCENARIOS.md`

## 7. Common Pitfalls & Mistakes
- Leaving state machines in zombie or orphan states when background operations crash.
- Committing partial database writes before verifying all downstream constraints.

## 8. Troubleshooting & Diagnostic Guide
Inspect `workflow_state_transitions_total` metrics to trace failed state paths.

## 9. Interview Questions & Detailed Answers
### Q1: Why must database transactions be bound to workflow state transitions?
**Answer**: To maintain ACID consistency: if a workflow step fails, the database rollback reverts any intermediate mutations, ensuring persistent storage exactly mirrors workflow state.

### Q2: What states are available in the Week 4/5 workflow state machine?
**Answer**: `REQUEST_RECEIVED`, `INTENT_DETECTED`, `TOOL_PROPOSED`, `APPROVAL_REQUIRED`, `APPROVED`, `EXECUTING`, `COMPLETED`, `APPROVAL_REJECTED`, `APPROVAL_EXPIRED`, `TIMED_OUT`, `FAILED`.

## 10. Practical Hands-On Exercise
Run `pytest tests/test_workflow_orchestration.py -v`.
