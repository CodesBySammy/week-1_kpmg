# Architecture Decision Records (ADRs)

## ADR-001: Technical Discovery to Architecture Mapping
- **Status**: Accepted
- **Context**: The client operates multiple departments (Billing, Tech Support, Legal) with strict SLA escalation procedures.
- **Decision**: Integrate relational OLTP case storage with an offline grounded RAG engine and a stateful agentic tool workflow in a single modular FastAPI release.
- **Consequences**: Unifies disparate capabilities into a single cohesive service with zero external network dependencies for testing.

## ADR-002: Controlled Scope Change — Case Escalation Tiering
- **Status**: Accepted
- **Context**: High-impact enterprise escalations require specialized SLA handling and supervisor signoffs.
- **Decision**: Introduce `escalation_tier` (`STANDARD`, `PRIORITY`, `CRITICAL_ESC`) and `department` fields to Case models and schemas. Updates to `CRITICAL_ESC` tier mandate supervisor HMAC approval tokens.
- **Consequences**: Enhanced governance without breaking backward compatibility; existing cases default to `STANDARD`.

## ADR-003: Deterministic Hybrid Indexing for Testing Portability
- **Status**: Accepted
- **Context**: Evaluation and CI/CD testing require offline execution without external API keys or heavy GPU runtimes.
- **Decision**: Couple a deterministic SHA-256 hash projection vector provider with a sparse BM25 keyword index and cross-score reranker.
- **Consequences**: Guaranteed reproducibility, lightning-fast test execution (sub-20ms per query), zero external billing risk.

## ADR-004: Dual-Layer Security Verification (Application over Model)
- **Status**: Accepted
- **Context**: Generative models cannot be trusted as authoritative authorization or security boundaries.
- **Decision**: Apply deterministic regex guardrails and JWT-based RBAC in application code before any workflow or tool execution.
- **Consequences**: The LLM suggests actions, but deterministic code validates authorization and executes mutations.

## ADR-005: Performance and Latency Budgets
- **Status**: Accepted
- **Context**: Enterprise users demand responsive interactive querying.
- **Decision**: Enforce a token budget of 1,500 tokens for RAG context assembly and cap local API read latency under 200ms.
- **Consequences**: Fast response times and predictable token consumption.

## ADR-006: Self-Contained SQLite Persistence with WAL Mode
- **Status**: Accepted
- **Context**: Standalone deployment, local developer testing, and automated rollback validation.
- **Decision**: Use SQLite with Write-Ahead Logging (WAL) and foreign keys enabled for all test and evaluation environments.
- **Consequences**: Simple deployment, transactional consistency, instant zero-downtime database snapshots for rollbacks.

## ADR-007: Transparent Known Limitations Register
- **Status**: Accepted
- **Context**: Production handover must communicate clear operational boundaries rather than claiming nonexistent perfection.
- **Decision**: Maintain a first-class `KNOWN_LIMITATIONS.md` document detailing in-memory state limits, single-node SQLite constraints, and offline hash embedding trade-offs.
- **Consequences**: Establishes trust with receiving engineering teams and defines clear roadmaps for future enhancements.
