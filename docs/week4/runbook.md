# Operational Runbook: Controlled AI Workflows & Tool Integrations

## 1. System Topology & Core Components

The Week 4 Controlled AI platform connects FastAPI case operations, Lakehouse Parquet pipelines, and Grounded RAG with safety, RBAC, and observability:

```
[Client / UI / Agent]
         │ (HTTP + X-Correlation-ID + Bearer Token)
         ▼
[Correlation & Auth Middleware] ──> [RBAC Verification]
         │
         ▼
[Workflow Orchestrator]
   ├── [Prompt Injection & Length Guardrails]
   ├── [Deterministic Intent Router]
   ├── [OpenTelemetry-Style Distributed Tracer]
   ├── [Tool Execution Engine (Timeouts & Backoff Retries)]
   │      ├── [retrieve_case] (Safe Read)
   │      └── [update_ticket] (Consequential Write ──> Requires Approval)
   ├── [Human Approval Manager (TTL, Replay-Protected)]
   └── [Event & Latency Metrics Collector]
```

---

## 2. Key Health & Observability Endpoints

| Endpoint | Method | Purpose | Normal Response |
|---|---|---|---|
| `/health` | GET | Liveness probe; verifies process is alive | `{"status": "healthy"}` |
| `/ready` | GET | Readiness probe; verifies SQLite, RAG, and Workflow engines | `{"status": "ready", "checks": {...}}` |
| `/api/v1/workflow/metrics` | GET | Real-time execution stats, error counts, latency histograms | `{"total_executions": N, "latencies_ms": {...}}` |
| `/api/v1/workflow/approvals` | GET | List pending approval requests awaiting human review | `{"approvals": [...]}` |

---

## 3. High-Priority Alert Responses & Troubleshooting

### Scenario A: High Rate of `APPROVAL_EXPIRED`
- **Symptom:** Workflow returns error `Approval token has expired`.
- **Root Cause:** Reviewer took longer than the configured approval TTL (default 15 minutes / 900 seconds) to respond.
- **Action:**
  1. Advise the user/agent to re-trigger the workflow request to generate a fresh approval token.
  2. If business requirements necessitate a longer review window, adjust `settings.approval_ttl_seconds` in `app/config.py`.

### Scenario B: Prompt Injection False Positives
- **Symptom:** User inputs flagged with `Input contains prohibited prompt injection patterns`.
- **Root Cause:** Legitimate technical queries mentioning phrases like `system prompt` or `ignore previous instructions` inside quotes.
- **Action:**
  1. Check correlation trace for the exact input string.
  2. Verify if the query comes from an internal auditor.
  3. If genuine, tune regex patterns in `security/guardrails.py` to require unquoted imperative sentence structures.

### Scenario C: SQLite Database Lock or Read Timeout
- **Symptom:** `ToolError(error_code='CASE_NOT_FOUND' or 'DB_LOCK_TIMEOUT')` during heavy concurrency.
- **Root Cause:** SQLite WAL mode not enabled or concurrent writes contending on transaction lock.
- **Action:**
  1. Verify SQLite pragma: `PRAGMA journal_mode=WAL;`.
  2. Ensure all database sessions use context managers with guaranteed `db.close()`.
