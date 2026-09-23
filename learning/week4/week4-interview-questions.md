# Week 4 Senior Engineering Interview Questions & Master Answers

---

### Q1: Why is "function calling" in production LLM systems dangerous without typed contracts and strict validation?
**Answer:**
Untyped LLM function calling treats model output as raw key-value dictionaries. In production, this introduces catastrophic failure modes:
1. **Type Hallucinations:** Models may pass `"123"` instead of integer `123`, or pass invalid enum values (`"super_high"` instead of `"HIGH"`).
2. **Missing Invariants:** Negative numbers or SQL injection fragments can bypass rudimentary parsers.
3. **Silent Errors:** Downstream databases crash or corrupt data when non-validated arguments are inserted.
By placing strict **Pydantic contracts** with `@field_validator` and `@model_validator` between the LLM and internal services, invalid inputs are rejected deterministically before any business logic executes, returning structured `ToolError` objects with machine-readable codes.

---

### Q2: What is the architectural difference between a safe read tool and a consequential write tool?
**Answer:**
- **Safe Read Tools** (e.g., `retrieve_case_details`):
  - Idempotent and side-effect free.
  - Can be executed autonomously upon intent recognition and authorization.
  - Safe to retry automatically with exponential backoff on transient errors.
- **Consequential Write Tools** (e.g., `update_ticket`):
  - Mutate persistent state (relational databases, external APIs, financial records).
  - Can cause irreversible harm if executed incorrectly or maliciously.
  - **Mandate Human-in-the-Loop (HITL) approval**: The workflow halts in `APPROVAL_REQUIRED` until an authorized human grants an approval token.
  - **Require Idempotency Keys**: Protects against double-billing, duplicate status updates, or duplicate emails upon network timeouts or replay attacks.

---

### Q3: Why can prompt-level instructions NOT be relied upon as security controls in enterprise AI?
**Answer:**
System prompts ("Do not reveal confidential data", "Only answer if user is manager") run in the **same token context** as user input. Because LLMs are probabilistic sequence predictors, user input can manipulate token attention (Prompt Injection / Jailbreaking) to override system instructions.
**Security must be enforced deterministically outside the LLM context:**
1. **Deterministic Guardrails:** Input sanitization, length limits, and regex signature detection strip adversarial prompts before LLM invocation.
2. **Deterministic RBAC:** Role-Based Access Control verified via cryptographically signed JWT/HMAC tokens at the API and tool layer.
3. **Access-Aware Retrieval:** Database queries and vector search pre-filter documents by the user's role claims, guaranteeing unauthorized text never enters the LLM's prompt context.

---

### Q4: Explain the state transitions of a production AI Workflow State Machine.
**Answer:**
A robust AI workflow is modeled as a deterministic Finite State Machine:
1. `REQUEST_RECEIVED`: Request accepted, Correlation ID attached.
2. `INTENT_DETECTED`: Router classifies intent into RAG policy search, safe read, or ticket write.
3. `TOOL_PROPOSED`: Tool arguments validated against Pydantic schema.
4. `APPROVAL_REQUIRED`: For consequential actions lacking an approval token, workflow pauses and generates an approval request.
5. `APPROVED`: Human reviewer signs approval token before expiration.
6. `EXECUTING`: Tool executes with timeout and exponential backoff retry.
7. `COMPLETED`: Result returned to user with audit trail.
8. `FAILED` / `TIMED_OUT`: Unrecoverable errors routed to deterministic fallback handlers.

---

### Q5: How does distributed tracing and correlation ID propagation work across an AI service?
**Answer:**
Every inbound request is assigned an `X-Correlation-ID` header (or generated via `corr_<uuid>`).
This ID is:
1. Stored in Python `contextvars` (thread-safe asynchronous execution context).
2. Attached to all structured JSON application log lines.
3. Included in OpenTelemetry span attributes for distributed trace trees.
4. Propagated in HTTP response headers back to the client.
5. Recorded in database audit history and Kafka/event logs.
This enables engineers and SREs to query a single Correlation ID and reconstruct the complete journey of an AI request across gateways, routers, RAG retrieval, vector search, tool execution, and database commits.
