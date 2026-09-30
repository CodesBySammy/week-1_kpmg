# Level 1/2/3 Support & Operational Runbook

## 1. Severity Levels & Response Times
- **SEV-1 (Critical Outage)**: System down, complete API failure. Response: < 15 min.
- **SEV-2 (Degraded Operation)**: RAG search down, tool updates failing. Response: < 1 hour.
- **SEV-3 (Minor / Inconvenience)**: Telemetry latency, sporadic 422 errors. Response: < 4 hours.

## 2. Diagnostic Flowcharts

### Incident A: Gateway Returning HTTP 500
1. Extract `correlation_id` from client error response header.
2. Query centralized logs: `grep $CORRELATION_ID /var/log/app.log`.
3. Check database connection pool saturation.
4. If database connection timeout, restart idle DB pool connections or scale DB read replicas.

### Incident B: Grounded RAG Returning "I cannot answer..." to Valid Queries
1. Check if the relevant compliance policy document was ingested into `HybridIndex`.
2. Inspect `rag_indexing_errors_total` metric.
3. Trigger re-indexing job: `python -m rag.ingestion.pipeline --reindex`.

### Incident C: Consequential Ticket Update Stalled at "APPROVAL_REQUIRED"
1. Verify if an approval request was generated for the case.
2. Check approval token TTL (has 30 minutes elapsed?).
3. Instruct supervisor user to review the approval queue and submit cryptographically signed grant token.
