# Week 4 — AI Tool Contracts Specification

> **Subsystem:** Controlled AI Tools (`tools/`)  
> **Document Version:** 1.0.0  
> **Standard:** Pydantic v2 JSON Schema & OpenAPI 3.0

---

## 1. Tool 1: `retrieve_case_details` (Read Operation)

### 1.1 Purpose & Scope
Retrieves verified case records from the relational database given a positive integer `case_id`.

### 1.2 Access & Operational Rules
- **Operation Type:** Read-only (Non-consequential).
- **Required Permission:** `Permission.READ_CASE` (`agent`, `manager`, `admin`).
- **Human Approval Required:** **NO** (Safe read operation).
- **Idempotency:** Naturally idempotent (pure read operation).
- **Retry Policy:** Retryable on transient database connection errors (Max 2 retries, 500ms backoff). Non-retryable on `CASE_NOT_FOUND` or `UNAUTHORIZED`.
- **Default Timeout:** 2.0 seconds.

### 1.3 JSON Input Contract
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RetrieveCaseInput",
  "type": "object",
  "properties": {
    "case_id": {
      "type": "integer",
      "exclusiveMinimum": 0,
      "description": "Positive integer identifier of the case"
    }
  },
  "required": ["case_id"],
  "additionalProperties": false
}
```

### 1.4 JSON Output Contract
```json
{
  "case_id": 101,
  "title": "Customer Billing Dispute",
  "description": "Discrepancy in monthly invoice line items",
  "status": "open",
  "priority": "high",
  "case_type": "dispute",
  "created_by": 12,
  "assigned_to": 15,
  "created_at": "2026-09-20T10:00:00Z",
  "resolved_at": null,
  "audit_notes": "Retrieved via authorized AI read tool"
}
```

### 1.5 Deterministic Error Codes
| Error Code | HTTP Equivalent | Retryable | Cause |
|---|---|---|---|
| `CASE_NOT_FOUND` | 404 Not Found | False | Specified `case_id` does not exist in SQLite |
| `INVALID_CASE_ID` | 400 Bad Request | False | Argument is $\le 0$ or non-integer |
| `UNAUTHORIZED` | 403 Forbidden | False | Caller role (e.g. `viewer`) lacks `case:read` |
| `DATABASE_TIMEOUT` | 504 Gateway Timeout | True | SQLite query exceeded 2.0s deadline |

---

## 2. Tool 2: `update_ticket` (Consequential Write Operation)

### 2.1 Purpose & Scope
Mutates ticket/case status and records an audit trail entry.

### 2.2 Strict Safety Constraints
- **Operation Type:** Write Operation (Consequential side effect).
- **Required Permission:** `Permission.EXECUTE_TICKET_UPDATE` (`manager`, `admin`).
- **Human Approval Required:** **MANDATORY**. Execution will be unconditionally rejected if a valid, approved `approval_id` is not supplied.
- **Idempotency:** Enforced via `idempotency_key` or `approval_id`. Submitting the same request twice returns the cached result with `is_idempotent_replay: true` without duplicating database writes.
- **Retry Policy:** Non-retryable on validation/approval errors.
- **Default Timeout:** 3.0 seconds.

### 2.3 JSON Input Contract
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "UpdateTicketInput",
  "type": "object",
  "properties": {
    "ticket_id": {
      "type": "integer",
      "exclusiveMinimum": 0,
      "description": "Target ticket/case ID"
    },
    "status": {
      "type": "string",
      "enum": ["open", "in_progress", "resolved", "closed"],
      "description": "Target status"
    },
    "comment": {
      "type": "string",
      "minLength": 3,
      "maxLength": 500,
      "description": "Mandatory justification note"
    },
    "approval_id": {
      "type": "string",
      "minLength": 8,
      "description": "Mandatory human approval token"
    },
    "idempotency_key": {
      "type": "string",
      "description": "Optional client-supplied idempotency key"
    }
  },
  "required": ["ticket_id", "status", "comment", "approval_id"],
  "additionalProperties": false
}
```

### 2.4 JSON Output Contract
```json
{
  "ticket_id": 101,
  "previous_status": "open",
  "new_status": "resolved",
  "comment": "Reimbursement discrepancy approved and processed",
  "approval_id": "appr_7f8a9b2c3d4e",
  "updated_by": "manager_jane",
  "updated_at": "2026-09-23T12:00:00Z",
  "is_idempotent_replay": false,
  "audit_event_id": "evt_9a8b7c6d5e4f"
}
```

### 2.5 Deterministic Error Codes
| Error Code | HTTP Equivalent | Retryable | Cause |
|---|---|---|---|
| `APPROVAL_REQUIRED` | 400 Bad Request / 403 Forbidden | False | No approval, approval is pending, or approval was rejected |
| `UNAUTHORIZED` | 403 Forbidden | False | User role lacks `ticket:update` |
| `VALIDATION_ERROR` | 422 Unprocessable Entity | False | Argument missing or length bounds violated |
| `TICKET_NOT_FOUND` | 404 Not Found | False | Target `ticket_id` does not exist |
| `INVALID_STATUS` | 400 Bad Request | False | Status not in allowed enum list |
