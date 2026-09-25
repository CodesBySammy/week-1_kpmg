# Updated Technical Backlog (Post-Scope-Change)

The following backlog item was incorporated following SCR-2026-05:

### SLICE-005: Case Escalation Tiering & Departmental Isolation
- **Backlog ID**: SLICE-005
- **Components**: `app/models/case.py`, `app/schemas/case.py`, `app/services/case_service.py`, `tools/update_ticket.py`, `security/rbac.py`.
- **User Journey**: Operator initiates case escalation; system verifies department access; if escalating to `CRITICAL_ESC`, requires supervisor approval token; persists change and writes audit trail.
- **Acceptance Criteria**: AC-011, AC-012, AC-013.
- **Automated Verification**: `tests/e2e/test_scope_change_escalation.py`.
