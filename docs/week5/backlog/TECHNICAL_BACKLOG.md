# Technical Backlog — Vertical Slices

## Overview
This backlog decomposes the complete cumulative Weeks 1–5 Enterprise Case Management Platform into traceable, multi-layer vertical slices. Each slice cuts across all relevant architectural layers (API, Security, Workflow, Tools, Database, Observability).

---

### SLICE-001: Grounded Policy Question & Answering
- **Requirement ID**: REQ-FR-002, REQ-FR-003, REQ-SEC-001
- **User/System Behavior**: Authenticated user submits an unstructured question regarding corporate escalation or compliance policies. System performs hybrid retrieval, reranks top chunks, formats prompt with strict isolation, synthesizes answer with citations, or issues refusal if confidence is below threshold.
- **Impacted Layers**: `app/api/routes/rag.py`, `rag/retrieval/`, `rag/generation/`, `security/guardrails.py`, `observability/`.
- **Interface**: `POST /api/v1/rag/query`
- **Acceptance Criteria**: AC-001, AC-002, AC-003.
- **Status**: IMPLEMENTED & TESTED.

---

### SLICE-002: Safe Read Tool Execution (Case Inspection)
- **Requirement ID**: REQ-FR-004, REQ-SEC-001
- **User/System Behavior**: User requests case details via workflow engine or REST API. System checks user permissions, executes `retrieve_case` tool with schema validation, extracts record from database, formats response, and emits structured audit log.
- **Impacted Layers**: `workflow/orchestrator.py`, `tools/case_tool.py`, `app/repositories/case_repository.py`.
- **Interface**: `POST /api/v1/workflow/execute` (Tool: `retrieve_case`)
- **Acceptance Criteria**: AC-004, AC-005.
- **Status**: IMPLEMENTED & TESTED.

---

### SLICE-003: Consequential Mutation & Human Approval Halt
- **Requirement ID**: REQ-FR-005, REQ-FR-006
- **User/System Behavior**: User requests a ticket modification (status change, title change). Workflow engine marks action as consequential, detects absence of an approval token, halts state machine in `WAITING_FOR_APPROVAL` state, and returns pending approval details.
- **Impacted Layers**: `workflow/state_machine.py`, `workflow/orchestrator.py`, `app/api/routes/workflow.py`.
- **Interface**: `POST /api/v1/workflow/execute` (Tool: `update_ticket`)
- **Acceptance Criteria**: AC-006, AC-007.
- **Status**: IMPLEMENTED & TESTED.

---

### SLICE-004: Cryptographic Approval Verification & Tool Execution
- **Requirement ID**: REQ-FR-005, REQ-OPS-002
- **User/System Behavior**: Supervisor signs approval payload producing HMAC-SHA256 token. Operator re-submits action with approval token. Workflow validates token signature, applies mutation to relational database, records `AuditLog` entry, and increments execution counter.
- **Impacted Layers**: `tools/ticket_tool.py`, `security/rbac.py`, `app/database/`, `app/repositories/case_repository.py`.
- **Interface**: `POST /api/v1/workflow/execute` (with `approval_token`)
- **Acceptance Criteria**: AC-008, AC-009, AC-010.
- **Status**: IMPLEMENTED & TESTED.

---

### SLICE-005: Case Escalation Tiering & SLA Recalculation (Scope Change)
- **Requirement ID**: REQ-FR-007, REQ-SEC-001
- **User/System Behavior**: Operator requests case escalation to `CRITICAL_ESC`. System verifies supervisor role, verifies policy compliance via RAG check, updates `escalation_tier`, adjusts SLA deadline, and records immutable escalation audit entry.
- **Impacted Layers**: `app/models/case.py`, `app/schemas/case.py`, `tools/ticket_tool.py`, `workflow/`.
- **Interface**: `POST /api/v1/workflow/execute`, `PATCH /api/v1/cases/{id}`
- **Acceptance Criteria**: AC-011, AC-012.
- **Status**: IMPLEMENTED & TESTED.

---

### SLICE-006: Cross-Department Boundary Isolation
- **Requirement ID**: REQ-SEC-003
- **User/System Behavior**: User assigned to Department A attempts to query or modify a case in Department B. Application-level RBAC filter intercepts request and returns 403 Forbidden or empty filtered list without leaking cross-tenant data.
- **Impacted Layers**: `security/rbac.py`, `app/api/routes/cases.py`, `tools/case_tool.py`.
- **Interface**: `GET /api/v1/cases/`, `POST /api/v1/workflow/execute`
- **Acceptance Criteria**: AC-013, AC-014.
- **Status**: IMPLEMENTED & TESTED.
