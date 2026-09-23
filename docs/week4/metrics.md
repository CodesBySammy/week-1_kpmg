# Production Metrics & Telemetry

## 1. Exposed Metrics
Exposed via `GET /metrics` and `MetricsCollector`:
- `request_count`: Total requests processed.
- `error_count`: Total failures categorized by error code.
- `workflow_duration_ms`: Duration histograms (P50, P90, P99).
- `token_usage`: Prompt tokens, completion tokens, and total tokens tracked.
