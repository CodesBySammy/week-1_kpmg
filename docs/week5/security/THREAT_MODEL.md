# Enterprise Platform Threat Model (STRIDE Methodology)

## 1. System Assets & Security Boundaries
The Enterprise Case Management Platform processes sensitive client financial records, investigative findings, and automated case actions.
Key Trust Boundaries:
1. **Perimeter / Public Boundary**: External API clients communicating with the FastAPI Gateway over TLS.
2. **Identity Boundary**: JWT Bearer token claims establishing `UserPrincipal` and role entitlements.
3. **AI / Model Boundary**: Untrusted user prompt inputs passed to LLM and RAG context assemblers.
4. **Tool Execution Boundary**: Consequential database write actions initiated by agentic tools.
5. **Persistence Boundary**: PostgreSQL/SQLite case repositories and Parquet lakehouse storage.

## 2. STRIDE Threat Analysis

| Threat Category | Threat Description | Vulnerable Component | Mitigation in Place |
|---|---|---|---|
| **Spoofing** | Forged JWT tokens or impersonated user headers | Auth Gateway | HMAC-SHA256 signature verification with rotating secret, token expiration checks |
| **Tampering** | Modifying case status or escalation tier without authorization | Case API / `update_ticket` tool | Two-man rule cryptographic approval tokens for consequential state transitions |
| **Repudiation** | An operator updates a ticket and denies having made the change | Audit Subsystem | Immutable `audit_logs` table recording user ID, action, timestamp, and diff |
| **Information Disclosure** | Prompt injection exfiltrating system prompt or other departments' cases | RAG / LLM Guardrails | Regex guardrails, department isolation filters in SQL queries, context sanitization |
| **Denial of Service** | Oversized payloads, recursive prompt attacks, DB connection starvation | Ingestion & API | Payload size caps (1MB), rate limiting, bounded LLM timeout (5.0s) |
| **Elevation of Privilege** | Investigator role attempting to assign `CRITICAL_ESC` or bypass approval | RBAC Guardrails | Hardcoded Python RBAC checks; LLM proposals cannot execute without code verification |
