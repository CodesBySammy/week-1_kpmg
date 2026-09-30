# Week 5 Technical Capstone Self-Assessment

Test your mastery of the enterprise FDE concepts implemented across Weeks 1 through 5. Answer all questions before checking the answer key at the bottom.

---

## Section 1: Technical Discovery & Architecture (Questions 1–5)

1. What are the three primary components of an RFC 2119 requirement statement?
2. In the Medallion Architecture, what specific data quality operations occur between the Bronze and Silver layers?
3. What is the fundamental difference between an Architecture Decision Record (ADR) and a software design document?
4. Why must correlation IDs be generated at the outermost ASGI middleware layer rather than inside individual endpoint handlers?
5. How does a hybrid RAG system combine dense vector search and sparse BM25 scores?

---

## Section 2: Security & Adversarial Testing (Questions 6–10)

6. State the core architectural principle governing tool execution in enterprise AI platforms.
7. Explain the difference between direct prompt injection and indirect prompt injection.
8. Why is department-level data filtering enforced at the repository query level rather than in the presentation layer?
9. What four elements are bound inside our cryptographic HMAC-SHA256 approval token?
10. Name the four core attack vectors tested in the Week 5 Red-Team test suite.

---

## Section 3: Reliability, Failures & SRE (Questions 11–15)

11. What HTTP status code should be returned when a client submits valid JSON that violates Pydantic business constraints?
12. What happens to corrupted records during the lakehouse ingestion pipeline in Week 2/5?
13. If an external LLM inference endpoint experiences a network timeout, how does the platform maintain reliability?
14. What are the two Kubernetes health probe endpoints implemented in the platform, and what does each verify?
15. What are the required criteria for declaring an automated test suite completely passing in this project?

---

## Section 4: Handover & Operations (Questions 16–20)

16. What is the purpose of an Ownership & Escalation Matrix in a production handover package?
17. What information must be documented in an incident runbook entry?
18. Why must an engineering Known Limitations Register never hide technical debt?
19. What triggers an automated rollback in the platform's deployment runbook?
20. How many total automated tests exist in the cumulative Week 1–5 test suite?

---

# ============================================================
# ANSWER KEY (Do Not Check Until You Have Attempted All Questions)
# ============================================================

1. **RFC 2119 Components**: Normative keywords (`MUST`, `SHOULD`, `MAY`), clear operational scope, and verifiable acceptance criteria.
2. **Bronze to Silver Operations**: Schema validation against contracts, type casting, date normalization, deduplication, and routing invalid rows to quarantine.
3. **ADR vs. Design Doc**: An ADR captures a single significant architectural decision, its context, evaluated alternatives, and permanent trade-offs; a design doc describes the overall feature design at a point in time.
4. **Correlation ID Middleware**: Outermost placement ensures that even early gateway failures (e.g. 422 parser errors or 401 unauthenticated requests) are stamped with a correlation ID.
5. **Hybrid RAG Fusion**: Vector search calculates cosine semantic similarity; BM25 calculates keyword frequency-inverse document frequency. Scores are normalized and weighted (e.g. 60% vector, 40% BM25) or merged using Reciprocal Rank Fusion.
6. **Core Principle**: "The model may propose; deterministic application code must decide."
7. **Prompt Injection Types**: Direct injection comes directly from the user's prompt text; indirect injection is embedded within ingested external data (documents, emails, web pages).
8. **Repository-Level Filtering**: Enforcing filters in SQL queries prevents unauthorized tenant records from entering memory, token budgets, logs, or LLM contexts.
9. **HMAC Approval Binding**: 1) Ticket/Case ID, 2) Proposed status/action, 3) Timestamp/TTL, 4) Approver User ID.
10. **Red-Team Vectors**: 1) Prompt Injection, 2) Access Leakage, 3) Malformed Data Injection, 4) Unsafe Tool Requests.
11. **Validation HTTP Code**: HTTP 422 Unprocessable Entity (or HTTP 400 Bad Request).
12. **Quarantine Handling**: Corrupted records are isolated in `data/quarantine/` with structured failure reasons, incrementing error metrics without halting the pipeline.
13. **LLM Timeout Handling**: Bounded timeouts trigger circuit breaking and graceful fallback to a deterministic policy message.
14. **Health Probes**: `/health/live` verifies worker process execution; `/health/ready` verifies database connectivity and vector index readiness.
15. **Passing Criteria**: 100% test pass rate (0 failures, 0 errors) with measurable statement coverage (>70%) and zero mocked test cheating.
16. **Ownership Matrix**: Clearly designates primary and secondary engineering contacts, escalation tiers, and Slack channels for every subsystem.
17. **Runbook Entry**: Symptom, verification check, log/trace query, root cause, remediation steps, validation command, and escalation path.
18. **Limitations Transparency**: Honest disclosure prevents dangerous misuse in production, maintains client trust, and establishes sprint priorities.
19. **Rollback Triggers**: Elevated 5xx error rates (>1% for 5 min) or failure of Kubernetes readiness probes to pass within 5 minutes.
20. **Total Tests**: Exactly 221 automated tests.
