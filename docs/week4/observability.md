# Observability Architecture

## 1. Core Pillars
1. **Correlation ID:** Propagated via `X-Correlation-ID` header across all loggers, spans, and metrics.
2. **Structured Events:** Logged as JSON lines with standardized schemas.
3. **Tracing:** Distributed spans capturing component execution latency.
4. **Metrics:** Latency percentiles (P50/P95/P99), error counters, and token usage metrics.
