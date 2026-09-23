# Structured Audit Logging

## 1. Audit Trail Requirements
Every consequential workflow event produces a structured audit record containing:
- `event_id`: Unique event identifier (e.g. `evt_...`)
- `correlation_id`: Distributed transaction correlation ID
- `username` & `user_role`
- `tool_name` & `ticket_id`
- `approval_id` & `approver`
- `previous_status` & `new_status`
- `timestamp`: UTC ISO-8601 timestamp
