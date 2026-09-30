# Module 19: Unsafe Tool Request Mitigation & Principle of Deterministic Control

## 1. Simple Explanation
The Principle of Deterministic Control dictates: 'The Model May Propose, but Deterministic Application Code Must Decide'. Unsafe or unauthorized tool actions are blocked at the application boundary.

## 2. Why It Matters
In Forward Deployed Engineering (FDE), raw prototype code is never sufficient for production client environments. Engineering deliverables must withstand non-happy-path real-world conditions, stringent enterprise compliance, organizational scope modifications, and architectural integration audits.

## 3. Key Concepts & Terminology
- **Primary Concept**: Unsafe Tool Request Mitigation & Principle of Deterministic Control provides the structural foundation for engineering predictability and system hardening.
- **Traceability**: Direct correlation between business problem statements, functional requirements, code implementations, automated verification tests, and operational telemetry.
- **Fail-Safe Determinism**: System state transitions and authorization checks must be deterministic, governed by verified application logic rather than stochastic model inference.
- **Operational Readiness**: A system is only ready for handover when observability, recovery runbooks, and failure mitigations are codified and tested.

## 4. Architecture & Technical Design
```text
LLM Proposal ('update ticket CASE-101') -> Deterministic Guardrail -> Role Check -> Approval Verification -> DB Execution
```

## 5. Project-Specific Implementation
`tools/update_ticket.py` verifies caller permissions and requires a valid HMAC approval token from `workflow/approval.py` before executing any state or escalation modifications.

## 6. Code & Module Mapping
- **Implementation File(s)**: `tools/update_ticket.py, workflow/approval.py`
- **Test File(s)**: `tests/test_human_approval.py`
- **Documentation Reference**: `docs/week5/security/SECURITY_HARDENING_REPORT.md`

## 7. Common Pitfalls & Mistakes
- Allowing an LLM to directly trigger database mutations or financial transactions without human approval.
- Trusting model-generated parameters without re-validating them against database constraints.

## 8. Troubleshooting & Diagnostic Guide
Verify that calling `update_ticket` with a tampered approval token returns `INVALID_APPROVAL`.

## 9. Interview Questions & Detailed Answers
### Q1: What is the core architectural principle governing tool execution in enterprise AI?
**Answer**: 'The model may propose; deterministic application code must decide.' The LLM has zero authority to commit transactions; all calls pass through strict RBAC, validation, and approval checks.

### Q2: What happens if an LLM hallucinates an invalid ticket ID in a tool call?
**Answer**: The tool intercepts the missing ID, catches the domain exception, and returns a typed `ToolError(error_code='CASE_NOT_FOUND')` rather than crashing the worker.

## 10. Practical Hands-On Exercise
Review `tools/update_ticket.py`.
