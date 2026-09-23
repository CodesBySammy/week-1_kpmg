# Fallback Strategies & Graceful Degradation

## 1. Deterministic Fallbacks
When tools or models encounter unrecoverable errors, the system triggers graceful fallback paths:
1. **RAG Downstream Failure:** Returns formal grounded refusal with no fabricated facts.
2. **Tool Execution Failure:** Explains the specific failure reason (e.g. 'Ticket 42 not found') rather than silent omission.
3. **Approval Required:** Halts execution and presents a structured pending approval payload with a direct URL for authorized managers to review.
4. **Unauthorized Access:** Rejects action cleanly with required permission details without exposing underlying stack traces.
