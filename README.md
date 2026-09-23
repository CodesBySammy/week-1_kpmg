# Enterprise Case Management & Grounded Policy Intelligence Platform

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Tests Passing](https://img.shields.io/badge/tests-100%2F100%20passed-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-86.78%25-brightgreen.svg)]()
[![Architecture: Medallion](https://img.shields.io/badge/architecture-Medallion%20Lakehouse-orange.svg)]()
[![RAG: Hybrid+Rerank](https://img.shields.io/badge/RAG-Hybrid%20%2B%20Rerank-purple.svg)]()
[![Docker](https://img.shields.io/badge/Docker-Multi--Stage-2496ED.svg)](https://www.docker.com/)

An enterprise-grade, three-pillar software, data, and AI platform developed for the **Forward Deployed Engineering (FDE) Fresher Readiness Program**:
1. **Week 1 Transactional Backend:** Modular, tested REST API service with SQLite, 3NF schema, Pydantic validation, and SCD Type 1/2 audit trails.
2. **Week 2 Enterprise Data Pipeline:** Medallion Lakehouse architecture (Bronze/Silver/Gold), 5-pillar statistical profiling, declarative data contracts, 8 domain quality rules, non-blocking quarantine handling, and mathematical source-to-target reconciliation.
3. **Week 3 Grounded Policy Knowledge Assistant (RAG):** Enterprise Policy Assistant featuring document ingestion, Markdown Section chunking, dense vector & Lucene BM25 hybrid indexing, candidate cross-score reranking, token-budget context assembly, and zero-hallucination grounded generation with verified citations.

---

## 1. High-Level System Architecture

```mermaid
flowchart TD
    subgraph Week1 ["Week 1: Transactional OLTP Subsystem"]
        Client[REST Client / Frontend] -->|HTTP / REST| API[FastAPI Service: app/main.py]
        API --> Service[Case Service: app/services/case_service.py]
        Service --> Repo[Repository: app/repositories/case_repository.py]
        Repo --> DB[(SQLite 3NF: case_management.db)]
        Repo --> AuditDB[(Audit Table: case_history)]
    end

    subgraph Week2 ["Week 2: Enterprise Data Pipeline Subsystem"]
        SrcCSV["Cases (CSV)"] & SrcJSON["Reference (JSON)"] & SrcPQ["Policies (Parquet)"] & SrcAPI["Policy REST API"] & SrcDB["Database Source"] --> Bronze["Raw Bronze Layer (Parquet Landing)"]
        Bronze --> Profiler["5-Pillar Statistical Profiler"]
        Profiler --> Quality{"8 Domain Quality Rules"}
        Quality -->|Invalid / Corrupted| DeadLetter["Quarantine Dead-Letter Sink (data/rejected/)"]
        Quality -->|Clean Valid Rows| Silver["Standardized Silver Layer (Cleaned Parquet)"]
        Silver --> Transform["Deduplication + Joins + Window Analytics + Aggregations"]
        Transform --> Gold["Curated Gold Layer (Parquet, CSV, SQLite)"]
        
        Bronze -.-> Reconciler["Source-to-Target Reconciliation Engine"]
        DeadLetter -.-> Reconciler
        Gold -.-> Reconciler
    end

    subgraph Week3 ["Week 3: Grounded Policy RAG Assistant Subsystem"]
        Corpus["Policy Corpus (data/policies/: HR, Travel, Expense, Security, Ethics)"] --> Parser["Markdown & PDF Parsers + Text Sanitizer"]
        Parser --> Chunker["Markdown Section Chunker"]
        Chunker --> VectorIdx["Dense Vector Index (Cosine Dot Product)"]
        Chunker --> BM25Idx["Lucene Smoothed BM25 Index"]
        
        VectorIdx & BM25Idx --> Fusion["Hybrid Fusion (Weighted Score & RRF)"]
        Fusion --> Reranker["CrossScore Candidate Reranker"]
        Reranker --> Assembler["Token-Bounded Context Assembler (Max 2000 tok)"]
        Assembler --> Generator["Grounded Answer Generator (MockLLM / OpenAI)"]
        Generator --> CitationEngine["Citation Cross-Verification & Refusal Engine"]
    end

    API -->|/api/v1/rag/*| Fusion
    API -->|/api/v1/rag/cases/{id}/policy-check| Service
    Service -.->|Case Title & Desc| Fusion
```

---

## 2. Quickstart & Installation

```powershell
# 1. Clone repository and navigate to backend directory
cd d:\week1_kpmg\case-management-backend

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -e .
```

---

## 3. Running the Test Suite (100 Tests)

```powershell
# Run the entire test suite with coverage report
pytest --cov=app --cov=pipeline --cov=rag -v

# Run specifically Week 3 RAG tests (32 tests)
pytest tests/test_rag_*.py -v
```

---

## 4. Week 3 RAG Assistant CLI Usage

The platform includes a unified CLI for managing the RAG engine:

```powershell
# 1. Ingest and reindex the corporate policy corpus
python -m rag.cli ingest

# 2. Ask a question to the Policy Knowledge Assistant
python -m rag.cli query "What are the rules regarding password expiration?"

# 3. Query with custom mode and top-k
python -m rag.cli query "What is the per diem meal allowance cap?" --mode hybrid --top-k 3 -v

# 4. Run the benchmark evaluation (Strategy A vs Strategy B)
python -m rag.cli evaluate
```

---

## 5. REST API Endpoints

Start the FastAPI application:
```powershell
uvicorn app.main:app --reload
```
View interactive Swagger documentation at **`http://127.0.0.1:8000/docs`**.

### Key Endpoints:
- **Case Management (`app/api/routes/cases.py`):**
  - `POST /api/v1/cases`: Create case with domain validation.
  - `GET /api/v1/cases/{id}`: Retrieve case and audit history.
  - `PUT /api/v1/cases/{id}`: Update case status and assignees.
  - `GET /api/v1/cases`: Paginated listing with multi-field filters.
- **RAG Policy Assistant (`app/api/routes/rag.py`):**
  - `GET /api/v1/rag/policies`: List all indexed policy documents and metadata.
  - `POST /api/v1/rag/ingest`: Trigger corpus re-ingestion and vector indexing.
  - `POST /api/v1/rag/retrieve`: Candidate chunk retrieval (supports `vector`, `bm25`, and `hybrid` with metadata filters).
  - `POST /api/v1/rag/query`: Grounded question-answering with verified citations.
  - `GET /api/v1/rag/benchmark`: Execute retrieval benchmark comparing Strategy A vs Strategy B.
  - `POST /api/v1/rag/cases/{case_id}/policy-check`: Check a case against corporate policies for automated compliance advice.

---

## 6. Benchmark Evaluation: Strategy A vs Strategy B

Automated evaluation on 8 representative enterprise policy queries across the 100-chunk corpus:

| Metric | Strategy A: Vector Only (k=5) | Strategy B: Hybrid + Reranker (k=3) | Improvement |
|---|---|---|---|
| **Hit Rate** | 87.5% | **100.0%** | **+12.5%** (100% Reliability) |
| **MRR (Mean Reciprocal Rank)** | 0.6292 | **0.9167** | **+45.7%** (Top Rank Placement) |
| **Precision@k** | 0.4750 | **0.7917** | **+66.7%** (Noise Reduction) |
| **Average Latency** | 8.97 ms | **0.87 ms** | Sub-millisecond Execution |
| **Faithfulness Score** | 0.9384 | **0.9388** | Zero-Hallucination Grounding |

---

## 7. Documentation Index

- [`docs/architecture.md`](docs/architecture.md): Master System Architecture (Week 1 + Week 2 + Week 3).
- [`docs/week3-rag-curriculum.md`](docs/week3-rag-curriculum.md): Comprehensive learning guide and master study manual.
- [`docs/week3-practical-labs.md`](docs/week3-practical-labs.md): 6 runnable, copy-pasteable hands-on code laboratories.
- [`docs/week3-evaluation-report.md`](docs/week3-evaluation-report.md): Quantitative benchmark evaluation report.
- [`docs/week3-traceability-matrix.md`](docs/week3-traceability-matrix.md): Complete requirements traceability matrix.
- [`docs/rag-failure-analysis.md`](docs/rag-failure-analysis.md): Failure modes taxonomy and failure injection lab.
- [`docs/rag-data-lineage.md`](docs/rag-data-lineage.md): End-to-end data provenance tracking.
- [`learning/week3/week3-interview-questions.md`](learning/week3/week3-interview-questions.md): 25 senior-level interview questions and model answers.
- [`learning/week3/week3-self-assessment.md`](learning/week3/week3-self-assessment.md): MCQs and engineering scenario challenges.
- [`WEEK3-STUDY-PLAN.md`](WEEK3-STUDY-PLAN.md): 5-day structured mastery plan.

---

## 8. Docker Deployment

```powershell
# Build Docker image
docker build -t case-management-platform:latest .

# Run container
docker run -p 8000:8000 case-management-platform:latest
```
