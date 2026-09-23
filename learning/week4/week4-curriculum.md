# Week 4 Curriculum: Controlled AI Workflows, Tool Integrations & Production Engineering

## 1. Curriculum Overview & Objectives
Welcome to **Week 4 of the FDE Fresher Readiness Program**. 
In Week 1, you built a relational case management backend with FastAPI and SQLite. 
In Week 2, you built an analytical Lakehouse pipeline with Medallion architecture (Bronze/Silver/Gold) and data reconciliation. 
In Week 3, you built an enterprise Grounded RAG assistant with semantic embeddings, hybrid retrieval, and citation verification.

Now in **Week 4**, you elevate your AI capabilities from passive answering to **Active, Controlled Agency**. You convert your RAG service into a reliable, enterprise-grade AI workflow that safely inspects databases, executes mutations, strictly respects security boundaries, enforces human approval for high-risk actions, and maintains production-grade observability and CI/CD automation.

---

## 2. Core Learning Modules

```
┌────────────────────────────────────────────────────────────────────────┐
│                        WEEK 4 PLATFORM ARCHITECTURE                    │
└────────────────────────────────────────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────┐
    ▼                               ▼                               ▼
[Module 1: Typed Tools]   [Module 2: Orchestration]   [Module 3: Security & RBAC]
- Pydantic I/O Schemas    - Explicit State Machine    - HMAC-SHA256 Bearer Auth
- Deterministic Errors    - Intent Router & Fallbacks - Role Hierarchy (4 Roles)
- Idempotent Writes       - Exponential Backoff       - Prompt Injection Defenses
- Strict Schema Validation- Human-in-the-Loop Gating  - Access-Aware Retrieval
                                    │
                                    ▼
                      [Module 4: Observability & SRE]
                      - Correlation ID Propagation
                      - Distributed Tracing (Spans)
                      - Latency & Token Metrics
                      - CI/CD & Automated Release Gates
```

---

## 3. Syllabus Breakdown

### Module 1: Typed AI Tool Integrations & Contracts
- Why untyped LLM actions cause production outages and silent data corruption.
- Defining strict Pydantic schemas for inputs and outputs.
- Building deterministic, non-retryable vs retryable error models (`ToolError`).
- Safe Read Tool: `retrieve_case_details` with relational foreign keys.
- Consequential Write Tool: `update_ticket` with status validation and comment logging.
- Designing idempotent mutations with `IdempotencyStore` to prevent duplicate updates.

### Module 2: Stateful Workflow Orchestration & Human Approval
- Finite state machines for AI workflows: `REQUEST_RECEIVED` $\rightarrow$ `ROUTING` $\rightarrow$ `APPROVAL_REQUIRED` $\rightarrow$ `TOOL_EXECUTION` $\rightarrow$ `COMPLETED`.
- Deterministic rule-based and regex intent classification vs brittle prompt steering.
- Handling downstream failures: configurable timeouts, exponential backoff retries, and graceful fallbacks.
- Human-in-the-Loop (HITL) architecture: why AI models must NEVER unilaterally execute consequential actions.
- Approval manager lifecycle: request generation, reviewer cryptographic signing, TTL expiration, and replay prevention.

### Module 3: Security Guardrails, RBAC & Access-Aware Retrieval
- Enterprise authorization vs LLM "prompt-based" safety (why prompt instructions fail as security controls).
- Role-Based Access Control (RBAC): `viewer`, `agent`, `manager`, `admin` permission matrices.
- Token-based identity: HMAC-SHA256 signed bearer tokens with role claims.
- Prompt injection defense: regex signature scanning, input length controls, and control-character sanitization.
- Delimiter boundaries: isolating untrusted user text (`<user_input>`) and document evidence (`<retrieved_evidence>`).
- Access-Aware Retrieval: pre-filtering policy collections and post-retrieval scrubber ensuring users only receive citations they are authorized to see.

### Module 4: Observability, SRE & Automated Deployment
- Distributed context propagation with `X-Correlation-ID` across HTTP headers, logs, traces, and metrics.
- OpenTelemetry-style distributed tracing: Spans, parent-child relationships, durations, and attributes.
- System metrics: P50, P95, P99 latency tracking, token consumption counters, and error rates.
- Production readiness: `/health` liveness probe and `/ready` dependency validation probe.
- CI/CD pipeline automation: linting, packaging, unit/integration testing, and 70%+ coverage gating.
- Deployment operations: canary rollout strategies, automated release gates, rollback runbooks, and incident response.
