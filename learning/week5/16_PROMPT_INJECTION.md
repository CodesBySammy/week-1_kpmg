# Module 16: Prompt Injection Defense & Untrusted Text Isolation

## 1. Simple Explanation
Prompt injection occurs when user-supplied text manipulates the LLM into ignoring system instructions, leaking private prompts, or executing unauthorized actions.

## 2. Why It Matters
In Forward Deployed Engineering (FDE), raw prototype code is never sufficient for production client environments. Engineering deliverables must withstand non-happy-path real-world conditions, stringent enterprise compliance, organizational scope modifications, and architectural integration audits.

## 3. Key Concepts & Terminology
- **Primary Concept**: Prompt Injection Defense & Untrusted Text Isolation provides the structural foundation for engineering predictability and system hardening.
- **Traceability**: Direct correlation between business problem statements, functional requirements, code implementations, automated verification tests, and operational telemetry.
- **Fail-Safe Determinism**: System state transitions and authorization checks must be deterministic, governed by verified application logic rather than stochastic model inference.
- **Operational Readiness**: A system is only ready for handover when observability, recovery runbooks, and failure mitigations are codified and tested.

## 4. Architecture & Technical Design
```text
User Prompt -> Pre-Execution Regex Guardrails -> Context Token Sanitization -> Model (Treated as Untrusted)
```

## 5. Project-Specific Implementation
`security/guardrails.py::detect_prompt_injection()` scans inputs for adversarial patterns ('ignore previous instructions', 'bypass security', 'you are now unconstrained').

## 6. Code & Module Mapping
- **Implementation File(s)**: `security/guardrails.py`
- **Test File(s)**: `tests/test_security_guardrails.py`
- **Documentation Reference**: `docs/week5/security/ABUSE_CASES.md`

## 7. Common Pitfalls & Mistakes
- Passing raw user input directly to the system prompt context without validation.
- Relying solely on prompt instructions like 'Do not execute dangerous commands'.

## 8. Troubleshooting & Diagnostic Guide
Test pattern matching in `security/guardrails.py` against OWASP Top 10 LLM jailbreak vectors.

## 9. Interview Questions & Detailed Answers
### Q1: What is the difference between direct and indirect prompt injection?
**Answer**: Direct prompt injection is typed directly by the user into the chat prompt. Indirect prompt injection is embedded inside ingested external data (e.g. inside a retrieved compliance document or customer email).

### Q2: How does our architecture neutralize indirect prompt injection in RAG contexts?
**Answer**: By treating retrieved context strictly as passive reference text and forbidding tool execution from RAG answer generation pipelines.

## 10. Practical Hands-On Exercise
Inspect the regex patterns in `security/guardrails.py`.
