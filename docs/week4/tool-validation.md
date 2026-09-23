# Tool Input & Output Validation

## 1. Schema Driven Contracts
Every tool in the system strictly validates input and output using Pydantic V2 models.

### Tool 1: retrieve_case_details
- **Input:** `RetrieveCaseInput` (`case_id > 0`)
- **Output:** `RetrieveCaseOutput` (`case_id`, `title`, `description`, `status`, `priority`, `case_type`, `created_by`, `assigned_to`, `created_at`, `resolved_at`, `audit_notes`)
- **Errors:** `CASE_NOT_FOUND`, `INVALID_CASE_ID`, `UNAUTHORIZED`

### Tool 2: update_ticket
- **Input:** `UpdateTicketInput` (`ticket_id > 0`, `status` in `['open', 'in_progress', 'resolved', 'closed']`, `comment`, `approval_id`, `idempotency_key`)
- **Output:** `UpdateTicketOutput` (`ticket_id`, `previous_status`, `new_status`, `comment`, `approval_id`, `updated_by`, `updated_at`, `is_idempotent_replay`, `audit_event_id`)
- **Errors:** `APPROVAL_REQUIRED`, `INVALID_APPROVAL`, `TICKET_NOT_FOUND`, `INVALID_STATUS`, `UNAUTHORIZED`, `VALIDATION_ERROR`

## 2. Deterministic ToolError Model
Tool failures return a structured error model:
```json
{
  "error_code": "CASE_NOT_FOUND",
  "message": "Case with ID 9999 was not found in the database.",
  "details": {"case_id": 9999},
  "retryable": false
}
```
