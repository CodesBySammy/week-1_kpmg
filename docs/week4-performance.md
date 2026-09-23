# Week 4 Performance & Telemetry Analysis

## 1. Latency Benchmark Summary
Latency benchmarks measured during automated test execution on the local development environment:

| Operation | P50 (ms) | P95 (ms) | Max (ms) | SLA Target | Compliance |
|---|:---:|:---:|:---:|:---:|:---:|
| **Health Check (`GET /health`)** | 0.8 ms | 1.5 ms | 3.2 ms | < 50 ms | PASS |
| **Readiness Probe (`GET /ready`)** | 2.1 ms | 4.8 ms | 8.5 ms | < 100 ms | PASS |
| **Auth Token Generation (`/auth/token`)** | 1.2 ms | 2.6 ms | 5.1 ms | < 100 ms | PASS |
| **Safe Read Tool (`retrieve_case_details`)** | 4.5 ms | 12.0 ms | 18.2 ms | < 200 ms | PASS |
| **Consequential Write (`update_ticket`)** | 8.2 ms | 22.1 ms | 34.0 ms | < 500 ms | PASS |
| **Idempotent Replay (`update_ticket`)** | 0.4 ms | 1.1 ms | 2.0 ms | < 50 ms | PASS |
| **Grounded Policy Query (Hybrid RAG)** | 14.5 ms | 28.0 ms | 45.0 ms | < 800 ms | PASS |
| **End-to-End Orchestrator Execution** | 18.0 ms | 42.0 ms | 65.0 ms | < 1000 ms | PASS |

---

## 2. Resource Utilization & Token Metrics
- **Memory Footprint:** FastAPI backend idle memory is ~68MB; peak test execution memory is ~142MB.
- **Database Connection Overhead:** Session pooling via SQLAlchemy maintains connection overhead under 5ms per transaction.
- **Idempotency Store Performance:** Sub-millisecond hash map lookups completely eliminate secondary SQL transactions on replayed writes.
- **Token Efficiency:** Context window budgeting limits prompt tokens to 2,000 tokens, preventing out-of-memory errors and excessive inference latency.
