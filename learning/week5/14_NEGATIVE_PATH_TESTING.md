# Module 14: Negative-Path & Boundary Condition Testing

## 1. Simple Explanation
Negative-path testing systematically subjects the system to invalid, malformed, unexpected, and boundary-exceeding inputs to verify that it fails safely and deterministically without crashing.

## 2. Why It Matters
In Forward Deployed Engineering (FDE), raw prototype code is never sufficient for production client environments. Engineering deliverables must withstand non-happy-path real-world conditions, stringent enterprise compliance, organizational scope modifications, and architectural integration audits.

## 3. Key Concepts & Terminology
- **Primary Concept**: Negative-Path & Boundary Condition Testing provides the structural foundation for engineering predictability and system hardening.
- **Traceability**: Direct correlation between business problem statements, functional requirements, code implementations, automated verification tests, and operational telemetry.
- **Fail-Safe Determinism**: System state transitions and authorization checks must be deterministic, governed by verified application logic rather than stochastic model inference.
- **Operational Readiness**: A system is only ready for handover when observability, recovery runbooks, and failure mitigations are codified and tested.

## 4. Architecture & Technical Design
```text
Input -> [Malformed JSON / Missing Fields / Giant Strings / Null Bytes] -> Gateway Validation -> HTTP 422 / 400 + Structured Error
```

## 5. Project-Specific Implementation
`tests/negative/test_negative_paths.py` contains 18 tests evaluating missing mandatory fields, negative amounts, oversized strings, expired tokens, duplicate IDs, and invalid status transitions.

## 6. Code & Module Mapping
- **Implementation File(s)**: `tests/negative/test_negative_paths.py`
- **Test File(s)**: `tests/negative/test_negative_paths.py`
- **Documentation Reference**: `docs/week5/testing/REGRESSION_STRATEGY.md`

## 7. Common Pitfalls & Mistakes
- Only testing happy-path valid data and assuming client applications will always send conformant payloads.
- Allowing uncaught 500 Internal Server Errors on malformed client requests.

## 8. Troubleshooting & Diagnostic Guide
Ensure all negative test cases assert structured error models (RFC 7807) and specific status codes (400, 401, 403, 422).

## 9. Interview Questions & Detailed Answers
### Q1: Why is negative-path testing crucial in production AI applications?
**Answer**: AI models and external web clients regularly generate unpredictable, truncated, or malformed inputs. Deterministic validation layers ensure these anomalies never cause crashes or undefined database states.

### Q2: What status code should a FastAPI endpoint return for a body with syntax errors versus business rule violations?
**Answer**: HTTP 422 Unprocessable Entity for schema/syntax validation errors; HTTP 400 Bad Request or HTTP 403 Forbidden for semantic business rule or authorization violations.

## 10. Practical Hands-On Exercise
Run `pytest tests/negative/test_negative_paths.py -v`.
