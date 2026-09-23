# Week 4 Self-Assessment & Mastery Checklist

Test your mastery of Week 4 concepts: Controlled AI Workflows, Tool Contracts, Security, and Production Engineering.

---

## 1. Multiple-Choice & Short-Answer Questions

1. **What distinguishes a transient tool error from a permanent tool error?**
   - [ ] A) Transient errors have HTTP 4xx codes; permanent errors have HTTP 5xx codes.
   - [ ] B) Transient errors (e.g., network timeouts, rate limits) can be retried with exponential backoff; permanent errors (e.g., validation failures, resource not found) must fail immediately without retrying.
   - [ ] C) Transient errors require human approval, while permanent errors do not.

2. **Why does `update_ticket` require an idempotency key?**
   - [ ] A) To ensure the database runs faster.
   - [ ] B) To prevent duplicate state mutations if a network timeout causes the client to retry an already-executed write request.
   - [ ] C) To encrypt the database connection string.

3. **In the Human-in-the-Loop workflow, what happens if an approval token expires before use?**
   - [ ] A) The workflow automatically approves the action.
   - [ ] B) The approval manager marks the request `EXPIRED`, and the execution tool rejects execution with an authorization error.
   - [ ] C) The system deletes the entire case from the database.

4. **Where should Role-Based Access Control (RBAC) be enforced?**
   - [ ] A) Only in the LLM's system prompt instructions.
   - [ ] B) In the API route middleware and in the tool execution functions using verified cryptographic tokens.
   - [ ] C) Only in client-side JavaScript.

5. **How does Access-Aware Retrieval prevent unauthorized data exposure in RAG?**
   - [ ] A) By asking the user if they have permission to view the file.
   - [ ] B) By pre-filtering documents based on the authenticated user's role before vector similarity search and stripping unauthorized citations.
   - [ ] C) By turning off document indexing entirely.

6. **What is the purpose of the `/ready` probe vs the `/health` probe?**
   - [ ] A) They are identical endpoints with different names.
   - [ ] B) `/health` checks simple process liveness; `/ready` verifies that downstream dependencies (e.g., database connection, vector index) are active and capable of serving traffic.
   - [ ] C) `/ready` is only for staging environments.

7. **Why do we sanitize user input with regex and delimiter isolation before passing it to an LLM?**
   - [ ] A) To minimize prompt tokens and neutralize prompt injection attempts trying to escape intended prompt boundaries.
   - [ ] B) Because LLMs cannot read spaces or punctuation.
   - [ ] C) To convert English into binary code.

8. **What header is propagated to maintain distributed observability across microservices?**
   - [ ] A) `X-Correlation-ID`
   - [ ] B) `Content-Type`
   - [ ] C) `Accept-Encoding`

9. **What is the state transition sequence for an update request requiring manager approval?**
   - [ ] A) `REQUEST_RECEIVED` $\rightarrow$ `INTENT_DETECTED` $\rightarrow$ `TOOL_PROPOSED` $\rightarrow$ `APPROVAL_REQUIRED` $\rightarrow$ `APPROVED` $\rightarrow$ `EXECUTING` $\rightarrow$ `COMPLETED`
   - [ ] B) `REQUEST_RECEIVED` $\rightarrow$ `COMPLETED` $\rightarrow$ `APPROVED`
   - [ ] C) `TOOL_PROPOSED` $\rightarrow$ `EXECUTING` $\rightarrow$ `APPROVAL_REQUIRED`

10. **What minimum test coverage percentage is required to pass the Week 4 automated release gate?**
    - [ ] A) 50%
    - [ ] B) 70%
    - [ ] C) 99%

---

## 2. Answer Key & Self-Scoring Rubric

| Question | Correct Answer | Topic |
|---|---|---|
| 1 | **B** | Deterministic Error Contracts & Backoff |
| 2 | **B** | Idempotency & Replay Safety |
| 3 | **B** | Human-in-the-Loop Governance |
| 4 | **B** | Deterministic RBAC vs Prompt Guarding |
| 5 | **B** | Access-Aware RAG Retrieval |
| 6 | **B** | Production Health & Readiness Probes |
| 7 | **A** | Prompt Injection & Delimiter Defense |
| 8 | **A** | Distributed Context Propagation |
| 9 | **A** | Finite State Machine Transitions |
| 10 | **B** | CI/CD Automated Quality Gates |

### Mastery Levels:
- **9-10 Correct:** Master Level — Ready for senior platform architect review!
- **7-8 Correct:** Proficient — Review the specific lab exercises for missed topics.
- **< 7 Correct:** Needs Revision — Review [`WEEK4-STUDY-PLAN.md`](file:///d:/week1_kpmg/case-management-backend/WEEK4-STUDY-PLAN.md) and re-read the core modules.
