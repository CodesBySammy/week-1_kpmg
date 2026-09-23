# Human-in-the-Loop (HITL) Governance

## 1. Why HITL is Mandatory
Autonomous LLMs are probabilistic models. Allowing an AI model to directly execute state-modifying operations (such as updating case status, modifying client tickets, or issuing financial refunds) creates severe operational risk.

## 2. Approval Lifecycle
1. **Request:** When `update_ticket` is proposed, `ApprovalManager.request_approval(...)` generates an approval request with a unique ID (e.g. `appr_3f2b1c8a`) and a 10-minute TTL.
2. **Review:** An authorized manager (`role in ['manager', 'admin']`) reviews the proposed ticket ID, new status, and justification via `POST /api/v1/workflow/approval/{id}/approve`.
3. **Verification:** The workflow validates that:
   - The token exists and is in `APPROVED` status.
   - The token has not expired.
   - The ticket ID and target status match the approved parameters exactly.
4. **Execution:** Once verified, the update executes and marks the token as used.
