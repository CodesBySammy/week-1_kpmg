# Health & Readiness Probes

## 1. Liveness Probe (`GET /health`)
Verifies that the HTTP process is running and accepting connections. Returns `{"status": "healthy"}`.

## 2. Readiness Probe (`GET /ready`)
Verifies that critical dependencies are operational before routing traffic:
- Database connectivity test (`SELECT 1`).
- Workflow orchestrator initialization.
- Returns 200 OK when ready, or 503 Service Unavailable if dependencies are degraded.
