# Technical Acceptance Criteria Register

Every backlog item in the Enterprise Case Management Platform must satisfy deterministic, observable technical acceptance criteria.

| Criterion ID | Target Behavior / Gate | Verification Mechanism | Expected Observable Result |
|---|---|---|---|
| **AC-001** | Grounded answer generation | `tests/test_rag_context_generation.py` | Response contains explicit source citation metadata matching ingested policy. |
| **AC-002** | Out-of-domain query refusal | `tests/test_rag_context_generation.py` | Query outside ingested corpus returns predefined refusal string without fabrication. |
| **AC-003** | RAG token budget enforcement | `tests/test_rag_chunking.py` | Combined context chunks strictly obey `max_tokens` threshold (<= 1500 tokens). |
| **AC-004** | Valid case lookup | `tests/test_tools_contracts.py` | Querying valid case ID returns JSON payload matching `CaseResponse` schema. |
| **AC-005** | Missing case lookup | `tests/test_tools_contracts.py` | Missing case ID returns deterministic `RESOURCE_NOT_FOUND` error schema (HTTP 404). |
| **AC-006** | Consequential mutation halt | `tests/test_human_approval.py` | Ticket update request without token transitions state to `WAITING_FOR_APPROVAL`. |
| **AC-007** | Invalid token rejection | `tests/test_human_approval.py` | Tampered, expired, or malformed approval token returns `403 Forbidden` (`APPROVAL_INVALID`). |
| **AC-008** | Valid approval execution | `tests/test_human_approval.py` | Cryptographically signed token executes ticket update and updates DB record. |
| **AC-009** | Idempotent re-execution | `tests/test_tools_contracts.py` | Submitting duplicate update request with same idempotency key returns identical result without duplicate audit records. |
| **AC-010** | Immutable audit trail | `tests/unit/test_case_repository.py` | Case modification creates corresponding record in `audit_logs` with old and new values. |
| **AC-011** | Escalation tier assignment | `tests/e2e/test_scope_change_escalation.py` | Case can be updated to `STANDARD`, `PRIORITY`, or `CRITICAL_ESC` with valid enum constraint. |
| **AC-012** | Critical escalation privilege | `tests/e2e/test_scope_change_escalation.py` | Escalating to `CRITICAL_ESC` rejected for non-supervisor roles. |
| **AC-013** | Department isolation on read | `tests/security/test_red_team_suite.py` | Agent in `SUPPORT` receives 403 or empty result when querying `LEGAL` case. |
| **AC-014** | Prompt injection interception | `tests/test_security_guardrails.py` | Injected prompt triggers `400 Bad Request` with guardrail violation code. |
