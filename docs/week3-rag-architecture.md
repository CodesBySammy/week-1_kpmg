# Week 3 — Grounded Policy Assistant: Architecture & System Design

> **Document Version:** 1.0.0  
> **Status:** Implemented, Tested, Production-Ready  
> **Repository Integration:** Extends Week 1 (FastAPI & Case Management) + Week 2 (Data Pipeline & Analytics)

---

## 1. System Overview

The **Grounded Policy Assistant** provides an enterprise policy retrieval and question-answering service built into the existing Case Management ecosystem. It enables compliance officers, caseworkers, and employees to ask natural language questions about corporate policies and verify case compliance with automated citations.

```
                           +----------------------------------------+
                           |           Client / Frontend            |
                           +-------------------+--------------------+
                                               |
                                     HTTP REST / JSON
                                               |
+----------------------------------------------v-----------------------------------------------+
|                                      FastAPI Gateway                                         |
|                                                                                              |
|  /api/v1/cases/*              /api/v1/pipeline/*             /api/v1/rag/*                   |
|  (Week 1 Case Management)     (Week 2 Data Ingestion)        - /rag/policies (Corpus list)   |
|                                                              - /rag/ingest (Reindex)         |
|                                                              - /rag/retrieve (Candidate kNN) |
|                                                              - /rag/query (Grounded Answer)  |
|                                                              - /rag/benchmark (A/B Eval)     |
|                                                              - /rag/cases/{id}/policy-check  |
+----------------------------------------------+-----------------------------------------------+
                                               |
                                     [RAG Core Engine]
                                               |
         +-------------------------------------+-------------------------------------+
         |                                                                           |
         v                                                                           v
+-------------------------+                                               +--------------------------+
|      Vector Index       |                                               |        BM25 Index        |
| (Dense Hashing/Cosine)  |                                               | (Lucene TF-IDF / Okapi)  |
+------------+------------+                                               +-------------+------------+
             |                                                                          |
             +----------------------------------+---------------------------------------+
                                                |
                                                v
                                      +--------------------+
                                      | Hybrid Fusion Node |
                                      | (Weighted / RRF)   |
                                      +---------+----------+
                                                |
                                                v
                                      +--------------------+
                                      | CrossScoreReranker |
                                      +---------+----------+
                                                |
                                                v
                                      +--------------------+
                                      |  Context Assembler |
                                      |  (Token Bounded)   |
                                      +---------+----------+
                                                |
                                                v
                                      +--------------------+
                                      | Grounded Generator |
                                      | (Strict Citations) |
                                      +--------------------+
```

---

## 2. Directory Layout & Module Structure

```
case-management-backend/
├── app/
│   ├── api/routes/
│   │   ├── cases.py               # Week 1 Case CRUD
│   │   ├── mock_api.py            # Week 1 External mock
│   │   └── rag.py                 # Week 3 RAG REST Endpoints (100% coverage)
│   ├── main.py                    # FastAPI entrypoint with rag_router registered
│   └── database/                  # SQLite DB session & models
├── data/
│   └── policies/                  # Corporate policy corpus (6 documents)
│       ├── HR-POLICY-001.md       # HR General Policy
│       ├── LEAVE-POLICY-002.md    # Leave & Absence Policy
│       ├── EXPENSE-POLICY-003.md  # Expense Reimbursement Policy
│       ├── TRAVEL-POLICY-004.md   # Travel Policy
│       ├── IT-SECURITY-005.md     # IT Security & Acceptable Use
│       └── COMPLIANCE-POLICY-006.md # Ethics, Whistleblower, Gifts
├── rag/                           # Week 3 RAG Package
│   ├── config.py                  # Settings & environment parameters
│   ├── schemas.py                 # Pydantic schemas (Chunks, Queries, Results)
│   ├── ingestion/
│   │   ├── parser.py              # Frontmatter, Markdown, PDF, Plain text parsers
│   │   └── preprocessor.py        # Normalization, whitespace, token estimators
│   ├── chunking/
│   │   └── strategies.py          # Fixed, Recursive, Markdown Section chunkers
│   ├── embeddings/
│   │   ├── base.py                # BaseEmbeddingProvider interface
│   │   └── providers.py           # DenseHash, SentenceTransformer, Mock providers
│   ├── indexing/
│   │   ├── vector_index.py        # Vector index with cosine similarity
│   │   ├── bm25_index.py          # Lucene-formula BM25 index
│   │   └── hybrid_index.py        # Weighted and RRF fusion index
│   ├── retrieval/
│   │   ├── reranker.py            # CrossScore candidate reranker
│   │   └── retriever.py           # Unified multi-mode retriever
│   ├── context/
│   │   └── assembler.py           # Token-bounded prompt context assembler
│   ├── llm/
│   │   └── provider.py            # BaseLLMProvider, MockLLMProvider, OpenAILLMProvider
│   ├── generation/
│   │   ├── prompts.py             # Grounding prompt templates & refusal rules
│   │   └── generator.py           # Grounded answer & citation verification engine
│   ├── evaluation/
│   │   ├── metrics.py             # Precision@k, Recall@k, MRR, Hit Rate, Faithfulness
│   │   └── evaluator.py           # Benchmark evaluator comparing Strategy A vs B
│   └── pipeline.py                # End-to-end RAG orchestrator
└── tests/
    ├── test_rag_ingestion.py      # Ingestion & preprocessing tests
    ├── test_rag_chunking.py       # Chunking strategies tests
    ├── test_rag_embeddings_indices.py # Vector, BM25, Hybrid index tests
    ├── test_rag_retrieval_rerank.py   # Retrieval & reranker tests
    ├── test_rag_context_generation.py # Grounding & refusal tests
    ├── test_rag_evaluation.py     # Benchmark & metrics tests
    └── test_rag_api.py            # FastAPI route integration tests
```

---

## 3. Case Management Integration

The system unifies the **Week 1 Case Management database** with the **Week 3 RAG Knowledge Assistant**:
- When an employee or manager opens a case (e.g. `Case(title="Employee expense dispute", description="Submitted flight receipts for domestic conference booked 3 days before departure")`),
- Calling `POST /api/v1/rag/cases/{id}/policy-check`:
  1. Queries the SQLite database for the case record.
  2. Extracts the case title, description, and metadata.
  3. Translates the case context into an automated policy search query.
  4. Retrieves relevant sections from `TRAVEL-POLICY-004.md` and `EXPENSE-POLICY-003.md`.
  5. Evaluates compliance (e.g. flagging that flights must be booked 14 days in advance under Section 2.1).
  6. Returns structured policy guidance and verified citations directly to the case audit log.
