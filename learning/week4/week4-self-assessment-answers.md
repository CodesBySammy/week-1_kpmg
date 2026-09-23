# Week 4 Self-Assessment Detailed Answers & Explanations

This document provides detailed answers, explanations, and engineering context for the questions in [`week4-self-assessment.md`](file:///d:/week1_kpmg/case-management-backend/learning/week4/week4-self-assessment.md).

---

### Question 1: What distinguishes a transient tool error from a permanent tool error?
**Answer: B**
- **Explanation:** In production engineering, failures are classified by whether repeating the exact same request with identical parameters might yield a success. Transient errors (network blips, socket drops, rate limits, lock contention) should be retried with exponential backoff and jitter. Permanent errors (invalid JSON, unknown ticket ID, unauthorized role, malformed input) will NEVER succeed on retry and must fail fast to save compute and prevent log spam.

---

### Question 2: Why does `update_ticket` require an idempotency key?
**Answer: B**
- **Explanation:** In distributed systems, networks are unreliable. A client might submit an update, the server applies the change, but the network drops before the 200 OK reaches the client. If the client retries, without an idempotency key, the server might append duplicate audit comments or duplicate state changes. An idempotency key ensures that repeated requests return the original outcome without secondary database mutations.

---

### Question 3: In the Human-in-the-Loop workflow, what happens if an approval token expires before use?
**Answer: B**
- **Explanation:** Every approval token has a Time-To-Live (TTL, default 10 minutes in this project). If an approval is not executed before expiration, `ApprovalManager.verify_approval` marks the token `EXPIRED` and rejects execution. This prevents "stale approvals" from being executed hours or days later after operational context has changed.

---

### Question 4: Where should Role-Based Access Control (RBAC) be enforced?
**Answer: B**
- **Explanation:** An LLM's system prompt is not a security boundary; it can be bypassed via prompt injection or jailbreaking. Real authorization must be enforced deterministically in code: at API gateway route handlers and inside tool execution functions using verified cryptographic tokens (JWT/HMAC).

---

### Question 5: How does Access-Aware Retrieval prevent unauthorized data exposure in RAG?
**Answer: B**
- **Explanation:** Rather than letting the LLM decide what to conceal, Access-Aware Retrieval pre-filters indexed policy chunks based on the user's authenticated role before vector search occurs. Additionally, any citations generated are verified against the user's role before being returned in the response.

---

### Question 6: What is the purpose of the `/ready` probe vs the `/health` probe?
**Answer: B**
- **Explanation:**
  - `/health` (Liveness): Validates that the process is alive and responding to HTTP requests. If this fails, the container orchestrator (e.g. Kubernetes, Docker) restarts the container.
  - `/ready` (Readiness): Validates that all downstream dependencies (database, vector indices, internal caches) are connected and ready to accept traffic. If this fails, traffic is temporarily diverted away from the container without restarting it.

---

### Question 7: Why do we sanitize user input with regex and delimiter isolation before passing it to an LLM?
**Answer: A**
- **Explanation:** Delimiters (such as `<user_input>` and `<retrieved_evidence>`) create clear token boundaries that instruct the LLM to treat the enclosed content strictly as untrusted data rather than system-level instructions. Regex scanning strips known jailbreak patterns before model processing.

---

### Question 8: What header is propagated to maintain distributed observability across microservices?
**Answer: A**
- **Explanation:** `X-Correlation-ID` is an industry standard HTTP header that links log lines, distributed traces, metric entries, and database audit records to a single user request across microservices.

---

### Question 9: What is the state transition sequence for an update request requiring manager approval?
**Answer: A**
- **Explanation:** The deterministic FSM transitions through:
  `REQUEST_RECEIVED` $\rightarrow$ `INTENT_DETECTED` $\rightarrow$ `TOOL_PROPOSED` $\rightarrow$ `APPROVAL_REQUIRED` $\rightarrow$ `APPROVED` $\rightarrow$ `EXECUTING` $\rightarrow$ `COMPLETED`.

---

### Question 10: What minimum test coverage percentage is required to pass the Week 4 automated release gate?
**Answer: B**
- **Explanation:** The project CI/CD pipeline enforces a strict quality gate requiring at least **70.0% code coverage** (`pytest --cov`) before any pull request can be merged or deployed. Our current test suite achieves **87.15% coverage**.
