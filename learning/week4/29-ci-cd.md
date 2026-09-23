# Automated CI/CD Pipelines

## 1. What It Is
Building GitHub Actions automation for linting, testing, packaging, and deployment.

## 2. Why It Exists
In autonomous and generative AI systems, unconstrained models frequently hallucinate, execute invalid operations, leak confidential context, or hang on network timeouts. This module introduces engineering patterns to make AI workflows deterministic, secure, and production-ready.

## 3. Why It Matters
Without deterministic controls, an enterprise cannot deploy LLMs to production. A single unauthorized write action or prompt injection can cause catastrophic data loss, compliance violations, or severe financial liability.

## 4. How It Works
1. **Request Intake:** The system captures inbound requests, binds a correlation ID, and sanitizes input.
2. **Deterministic Evaluation:** The application layer evaluates schemas, permissions, and state machines.
3. **Controlled Execution:** Tools and RAG retrieval execute within strict timeout and retry boundaries.
4. **Audit & Telemetry:** Every transition is recorded in structured logs, distributed traces, and metrics.

## 5. Important Terminology
- **FSM (Finite State Machine):** A computation model consisting of a finite number of states and explicit transitions.
- **Idempotency:** The property where an operation can be applied multiple times without changing the result beyond the initial application.
- **HITL (Human-in-the-Loop):** Requiring explicit human review and authorization before high-consequence actions execute.
- **Correlation ID:** A unique string propagated across distributed systems to trace a single transaction end-to-end.

## 6. Simple Example
```python
# Minimal conceptual implementation
def execute_safe_operation(input_data, principal):
    if not principal.is_authorized():
        raise PermissionError("Access denied")
    return {"status": "SUCCESS", "data": input_data}
```

## 7. Real-World Example
In banking case management, when an AI suggests refunding $5,000 to an account, the system halts, notifies a compliance officer, and only executes the transaction when the manager provides a signed approval token.

## 8. Example from This Project
In `tools/update_ticket.py`, the `update_ticket` function checks `params.approval_id` with `workflow.approval.approval_manager`. If no valid token exists, execution is blocked with error code `APPROVAL_REQUIRED`.

## 9. Common Mistakes
- Relying on the LLM's system prompt to enforce security or role permissions.
- Retrying non-transient errors (such as 404 Not Found or validation errors).
- Allowing mutable write operations without idempotency keys.
- Logging raw tokens, passwords, or PII in application telemetry.

## 10. Good Practices
- Use strict Pydantic v2 schemas for all tool inputs and outputs.
- Enforce explicit state transition tables (`VALID_TRANSITIONS`).
- Propagate `X-Correlation-ID` across all components and thread contexts.
- Enforce at least 70% automated test coverage in CI/CD quality gates.

## 11. Bad Practices
- Hardcoding credentials or JWT secrets in repository code.
- Using unbounded retries without exponential backoff.
- Trusting retrieved documents as executable instructions instead of passive data.

## 12. When to Use It
Use this pattern whenever building AI applications that interact with real databases, external APIs, financial records, or confidential enterprise knowledge.

## 13. When Not to Use It
For purely creative or conversational chatbots that do not touch databases, external tools, or confidential data, lightweight stateless architectures may suffice.

## 14. Security Implications
Enforces defense-in-depth: authentication, role-based authorization, deterministic input sanitization, and access-aware retrieval ensure the AI model can never exceed authorized boundaries.

## 15. Testing Implications
Unit and integration tests must cover:
- Schema validation rejections.
- State machine transition limits.
- Unauthorized access attempts.
- Replay and idempotency verification.

## 16. Practical Exercise
Run the project's test suite to verify this module in action:
```bash
pytest tests/ -v
```

## 17. Senior Interview Questions
- **Q:** *Why can't an LLM be trusted to enforce its own authorization?*  
  **A:** *Because prompt attention can be manipulated via prompt injection; authorization must be enforced in deterministic application code outside the token generation loop.*

## 18. Self-Test
1. What error code is returned when an unapproved write action is attempted?  
   *(Answer: `APPROVAL_REQUIRED`)*
2. What header propagates transaction identity across microservices?  
   *(Answer: `X-Correlation-ID`)*
