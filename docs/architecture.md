# Master System Architecture Document — Enterprise Case & Policy Knowledge Platform

> **Status:** Production-Ready (Week 1 + Week 2 + Week 3 Fully Integrated)  
> **Test Suite:** 100 Tests Passing (86.78% Total Code Coverage)

---

## 1. Executive Summary

The **Enterprise Case & Policy Knowledge Platform** is a unified, production-grade enterprise software system combining:
1. **Transactional Backend (Week 1):** FastAPI, SQLAlchemy, SQLite, Clean Architecture, and Audit Logging for Case Management.
2. **Analytical Lakehouse Pipeline (Week 2):** Medallion Architecture (Raw → Standardized → Curated), Data Profiling, Quarantine Isolation, and Automated Reconciliation.
3. **Grounded Policy Knowledge Assistant (Week 3):** Retrieval-Augmented Generation (RAG) system with Ingestion, Markdown Section Chunking, Dense Vector + Lucene BM25 Hybrid Indexing, CrossScore Reranking, Token-Bounded Context Assembly, and Zero-Hallucination Grounded Generation with verified citations.

---

## 2. Multi-Pillar Solution Architecture

```mermaid
graph TB
    subgraph Client & Consumer Layer
        User[Human Users / Caseworkers]
        Compliance[Compliance Officers & Auditors]
        External[External API Clients]
    end

    subgraph Ingress & Web Gateway : app/
        FastAPI[FastAPI Gateway :8000]
        OpenAPI[Swagger UI /docs & OpenAPI Specs]
        ExHandler[Centralized Exception Handlers]
    end

    subgraph Pillar 1: Case Management Service (Week 1)
        CaseAPI[app/api/routes/cases.py]
        CaseService[app/services/case_service.py]
        CaseRepo[app/repositories/case_repository.py]
        SQLite[(SQLite DB: case_management.db)]
    end

    subgraph Pillar 2: Analytical Data Pipeline (Week 2)
        Sources[Multi-Source Ingestion: CSV, JSON, Parquet, API]
        Raw[Raw Storage Layer]
        Validation[Quality Rules & Schema Contracts]
        Standardized[Standardized Storage Layer]
        Curated[Curated Aggregations & Joins]
        Quarantine[Quarantine Dead-Letter Storage]
        Reconciliation[Row-Count & Sum Reconciler]
    end

    subgraph Pillar 3: Grounded Policy Assistant (Week 3)
        PolicyCorpus[data/policies/: HR, Travel, Expense, Security, Ethics]
        Ingestion[rag/ingestion: Markdown & PDF Parsers, Sanitizer]
        Chunking[rag/chunking: Section & Recursive Chunkers]
        VectorIdx[rag/indexing: Dense Vector Index - Cosine]
        BM25Idx[rag/indexing: Lucene Smoothed BM25 Index]
        HybridFusion[rag/indexing: Weighted & RRF Fusion Engine]
        Reranker[rag/retrieval: CrossScore Reranker]
        Context[rag/context: Token-Bounded Context Assembler]
        LLMGen[rag/generation: Grounded Answer Generator]
        CitationEngine[Citation Cross-Verification Engine]
    end

    User --> FastAPI
    Compliance --> FastAPI
    External --> FastAPI

    FastAPI --> CaseAPI
    CaseAPI --> CaseService
    CaseService --> CaseRepo
    CaseRepo --> SQLite

    SQLite -.->|Data Source| Sources
    Sources --> Raw --> Validation --> Standardized --> Curated
    Validation -.->|Failed Rules| Quarantine
    Curated -.-> Reconciliation

    PolicyCorpus --> Ingestion --> Chunking
    Chunking --> VectorIdx & BM25Idx
    
    FastAPI -->|/api/v1/rag/*| Reranker
    FastAPI -->|/api/v1/rag/cases/{id}/policy-check| CaseService
    CaseService -.->|Case Context| Reranker

    VectorIdx & BM25Idx --> HybridFusion --> Reranker --> Context --> LLMGen --> CitationEngine --> FastAPI
```

---

## 3. Pillar 3: Grounded RAG Assistant Deep Dive

### 3.1 Document Ingestion & Section-Aware Chunking
- **Corpus:** 6 enterprise policies (`HR-POLICY-001` through `COMPLIANCE-POLICY-006`) containing structured YAML frontmatter.
- **Preprocessing:** Sanitizes control characters (`[\x00-\x1f]`), normalizes CRLF line breaks, collapses excess whitespace, and estimates token budgets.
- **Section Chunking:** The `MarkdownSectionChunker` recognizes markdown header tags (`#`, `##`, `###`), preserving entire rule clauses and attaching section metadata to prevent sentence-severing bugs common in fixed-size chunking.

### 3.2 Dual-Engine Hybrid Retrieval & Fusion
- **Dense Vector Search:** Employs `DenseHashEmbeddingProvider` (384-dimensional unit vectors with stopword downweighting and character n-gram projections). Unit vectors enable computing Cosine Similarity strictly through fast NumPy dot products.
- **Sparse BM25 Search:** Employs Lucene non-negative smoothed IDF formulation $\ln(1 + \frac{N - n + 0.5}{n + 0.5})$, eliminating zero or negative IDF bugs found in standard Okapi formulas on small collections.
- **Weighted Score Fusion:** Combines scores via $S = 0.6 \cdot S_{\text{vector}} + 0.4 \cdot S_{\text{bm25}}$.

### 3.3 Candidate Reranking
- Top candidate chunks are evaluated by `CrossScoreReranker` using exact term coverage, phrase matching bonuses, and section header alignment, promoting the exact rule clause to Rank 1.

### 3.4 Context Assembly & Grounded Generation
- **Token Budget:** `ContextAssembler` enforces strict `max_context_tokens` (default 2000), protecting LLM context windows and reducing inference latency.
- **Grounding Instructions:** Strict prompt directives prohibit outside knowledge.
- **Citation Validation:** Every bracketed citation (e.g. `[IT-SECURITY-005, Section 2.1]`) is cross-checked against the retrieved chunk index.
- **Refusal Behavior:** Out-of-domain queries trigger formal refusal responses (*"I am unable to answer this question based on the provided policy documents"*).

---

## 4. Integration: Automated Case Compliance Checking

The platform bridges operational case management and corporate policy knowledge:
1. When a case is updated or investigated, calling `POST /api/v1/rag/cases/{case_id}/policy-check` initiates an automated compliance audit.
2. The endpoint retrieves the case title, description, and status from SQLite.
3. Formulates a compliance inquiry and executes hybrid retrieval against the corporate policy corpus.
4. Generates verified policy advice citing specific clauses (e.g., flight booking advance notice in `TRAVEL-POLICY-004` or meal allowance caps in `EXPENSE-POLICY-003`).

---

## 5. Security & Observability

1. **Deterministic Offline Operation:** The entire RAG pipeline, embedding engine, and evaluation harness run locally without external cloud API dependencies.
2. **Citation Provenance:** Every statement is backed by an auditable citation traceable to physical files in `data/policies/`.
3. **Structured JSON Logs:** All operations across Case Management, Data Pipeline, and RAG log structured JSON events with timestamps, component names, and request IDs.
4. **Data Isolation:** Zero secrets or credentials are hardcoded.
