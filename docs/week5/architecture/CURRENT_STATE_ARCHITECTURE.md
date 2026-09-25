# Current-State Architecture (Weeks 1–4 Cumulative System)

## 1. System Components & Responsibilities
- **API Gateway / Web Layer (`app/api/`)**: FastAPI HTTP router handling request validation, dependency injection, and correlation ID extraction.
- **Relational Domain Service (`app/services/case_service.py`)**: Business logic orchestration, validation of user roles and case lifecycle transitions.
- **Data Persistence Layer (`app/database/`, `app/repositories/`)**: SQLAlchemy models (`Case`, `User`, `AuditLog`) with transactional commit, rollback, and audit log generation.
- **Lakehouse Data Pipeline (`pipeline/`)**: Multi-stage medallion pipeline for processing raw data dumps into standardized and curated Parquet tables with data quality verification and financial reconciliation.
- **Grounded RAG System (`rag/`)**: Knowledge ingestion, token-budgeted context assembly, hybrid indexing (vector + BM25), cross-score reranking, and hallucination-free generation with source citations.
- **Agentic Workflow Engine (`workflow/`, `tools/`)**: Stateful LangGraph-style workflow orchestrator, deterministic router, typed Pydantic tool contracts (`retrieve_case`, `update_ticket`), and HMAC-SHA256 cryptographic approval verification.
- **Security & Observability Subsystems (`security/`, `observability/`)**: Prompt injection guardrails, JWT authentication, RBAC policy enforcement, OpenTelemetry distributed tracing, and Prometheus metrics.

## 2. Failure Points & Mitigations
- **Upstream Network Latency**: Handled via configurable client timeouts and bounded exponential retries.
- **Empty Retrieval**: Evaluated in RAG pipeline; produces a deterministic out-of-domain refusal instead of fabricating an answer.
- **Unapproved Consequential Action**: Workflow halts in `WAITING_FOR_APPROVAL` state; execution blocked until a signed cryptographic token is supplied.
