# System Requirements Specification (SRS)

## 1. Functional Requirements (FR)
- **REQ-FR-001**: User can query cases by ID, title, status, and department.
- **REQ-FR-002**: Grounded RAG system answers questions strictly based on ingested policy documents with citations.
- **REQ-FR-003**: RAG system reliably produces out-of-domain refusals when evidence is absent.
- **REQ-FR-004**: System provides typed tools (
etrieve_case, update_ticket) with Pydantic contract validation.
- **REQ-FR-005**: Consequential actions (e.g. ticket updates, priority changes) require an HMAC-SHA256 human approval token.
- **REQ-FR-006**: State machine enforces valid state transitions and halts at WAITING_FOR_APPROVAL when an approval token is missing.
- **REQ-FR-007**: Escalation tier management allows cases to be classified into STANDARD, PRIORITY, and CRITICAL_ESC tiers.

## 2. Non-Functional Requirements (NFR)
- **REQ-NFR-001 (Performance)**: Read queries resolve with p95 latency under 150ms locally.
- **REQ-NFR-002 (Availability)**: Health check endpoints (/health, /ready) report operational status within 10ms.
- **REQ-NFR-003 (Reliability)**: Transient downstream errors trigger bounded exponential backoff retries (maximum 3 attempts).
- **REQ-NFR-004 (Maintainability)**: Minimum 70% test coverage maintained across all application code.

## 3. Security Requirements (SEC)
- **REQ-SEC-001**: RBAC enforced: iewer (read-only), operator (read/request update), supervisor / dmin (approve/execute mutations).
- **REQ-SEC-002**: Prompt injection attacks intercepted before model/tool invocation.
- **REQ-SEC-003**: Cross-department data leakage prevented via application-level filtering.
- **REQ-SEC-004**: Zero plaintext secrets in code, logs, or repository artifacts.

## 4. Operational & Audit Requirements (OPS)
- **REQ-OPS-001**: Every request carries an X-Correlation-ID across logs, traces, and metrics.
- **REQ-OPS-002**: Consequential mutations produce immutable database audit entries.
- **REQ-OPS-003**: Containerized deployment runnable via Docker with automated health checks.
