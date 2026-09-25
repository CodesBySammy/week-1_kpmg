# Non-Functional Requirements Matrix

| Metric / Dimension | Target / SLA | Measurement Method | Verification Status |
|---|---|---|---|
| **API Read Latency** | p95 < 200 ms | Pytest benchmark fixture (	ests/performance/) | PASS (Avg: 12ms) |
| **RAG Query Latency** | p95 < 300 ms | Synthetic benchmark run across 50 iterations | PASS (Avg: 38ms) |
| **Test Coverage** | >= 70% Statement Coverage | pytest --cov=app | PASS (90.63%) |
| **Error Handshake** | Deterministic JSON Error schema | Status codes 400, 401, 403, 404, 422, 500 | PASS (Standard RFC 7807) |
| **Health Check SLA** | 100% uptime on /health | Liveness & readiness probes | PASS (HTTP 200 OK) |
| **Traceability** | 100% requests correlated | X-Correlation-ID in HTTP headers & logs | PASS |
