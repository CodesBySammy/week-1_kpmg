# Distributed Tracing & Span Lifecycle

## 1. Trace Hierarchy
```text
Trace [corr_12345]
 ├── Span: api_gateway_request
 ├── Span: workflow_orchestration
 │    ├── Span: intent_routing
 │    ├── Span: approval_verification
 │    └── Span: tool_execution [update_ticket]
 │         └── Span: db_case_update
 └── Span: response_serialization
```
Each span records `span_id`, `parent_span_id`, `start_time`, `end_time`, `duration_ms`, and contextual attributes.
