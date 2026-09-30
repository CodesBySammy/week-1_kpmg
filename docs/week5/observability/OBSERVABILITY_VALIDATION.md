# Observability & Distributed Tracing Validation

## 1. Tracing Architecture
Every incoming request is tagged with a UUID4 `correlation_id` by `CorrelationIdMiddleware`.
This ID propagates across:
1. HTTP request/response headers (`X-Correlation-ID`).
2. Log records (structlog formatting).
3. OpenTelemetry spans (`span.set_attribute("correlation_id", ...)`).
4. Workflow execution states (`WorkflowExecutionResult.correlation_id`).
5. Audit log entries (`audit_logs.correlation_id`).

## 2. End-to-End Trace Verification
Automated test `tests/test_observability.py` verifies that a full workflow request produces matching trace attributes across the API, tool, approval, and audit layers.

```text
[Trace: a81f48b0-18e3-4c92-b43a-7ef001938a12]
  ├── [Span: api.handle_request]
  ├── [Span: security.verify_jwt]
  ├── [Span: workflow.orchestrate]
  │     ├── [Span: rag.hybrid_search]
  │     └── [Span: tool.update_ticket]
  └── [Span: database.commit_audit_log]
```
