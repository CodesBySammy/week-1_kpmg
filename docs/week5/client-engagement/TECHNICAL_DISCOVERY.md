# Technical Discovery Document

## 1. System Inventory & Architecture Invariants
- **Backend Framework**: FastAPI with Python 3.14 on Uvicorn.
- **Relational Storage**: SQLite with SQLAlchemy ORM (WAL mode, foreign keys enabled).
- **Data Engineering**: Medallion pipeline (Raw -> Standardized -> Curated) with schema enforcement and quarantine.
- **RAG Architecture**: Markdown ingestion, fixed/recursive/section chunking, dense hash vector embeddings + BM25 sparse index, cross-score reranking, and grounded generation with strict refusal behavior.
- **Agentic Workflow**: State machine with deterministic routing, typed tool contracts (
etrieve_case, update_ticket), cryptographic HMAC-SHA256 human approval tokens, and Prometheus metrics.

## 2. Integration Interfaces
- GET /health & GET /ready: Kubernetes-compatible liveness and readiness probes.
- GET /api/v1/cases/: Case query and filtering endpoint.
- POST /api/v1/rag/query: Grounded policy Q&A with source citations.
- POST /api/v1/workflow/execute: Controlled agentic entry point.
- POST /api/v1/workflow/token: Development JWT token generator.
- GET /api/v1/workflow/metrics: Operational metrics endpoint.

## 3. Data Sources & Formats
- Structured OLTP: Cases, Users, Audit Logs in SQLite.
- Semi-structured: Regulatory policies in data/policies/*.md.
- Batch Lakehouse: Parquet/CSV medallion layers in data/raw, data/standardized, data/curated.

## 4. Discovery Findings & Gaps
1. **Single Priority Field**: Case priority is currently limited to Low, Medium, High without formal escalation tier tracking.
2. **Missing Department Scoping**: Agents currently query cases across all departments without departmental boundary validation.
3. **Failure Resilience Gap**: System needs explicit automated resilience tests for external timeouts, corrupted documents, and model service degradation.
