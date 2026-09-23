# Week 3 — 5-Day Study & Mastery Plan

> **Program:** FDE Fresher Readiness Program — Week 3  
> **Topic:** Grounded RAG Policy Knowledge Assistant  
> **Methodology:** LEARN → PRACTICE → BUILD → TEST → EVALUATE → DEBUG → DOCUMENT → REVIEW

---

## Daily Schedule Breakdown

### Day 1: Foundations & Document Ingestion
- **LEARN:** Understand RAG vs Fine-Tuning. Study non-parametric memory, LLM hallucinations, and why enterprises require grounded answers with citations.
- **PRACTICE:** Read [`docs/week3-rag-curriculum.md`](file:///d:/week1_kpmg/case-management-backend/docs/week3-rag-curriculum.md) Sections 1 & 2. Complete Lab 1 in [`docs/week3-practical-labs.md`](file:///d:/week1_kpmg/case-management-backend/docs/week3-practical-labs.md).
- **BUILD:** Inspect [`rag/ingestion/parser.py`](file:///d:/week1_kpmg/case-management-backend/rag/ingestion/parser.py) and [`rag/ingestion/preprocessor.py`](file:///d:/week1_kpmg/case-management-backend/rag/ingestion/preprocessor.py). Verify parsing of Markdown frontmatter and PDF documents.
- **TEST:** Run `pytest tests/test_rag_ingestion.py -v`.

---

### Day 2: Chunking Strategies & Vector Embeddings
- **LEARN:** Compare Fixed-Size vs Recursive Character vs Markdown Section chunking. Study mathematical definitions of Cosine Similarity, Dot Product, and Euclidean L2 distance.
- **PRACTICE:** Execute Lab 2 and Lab 3 in [`docs/week3-practical-labs.md`](file:///d:/week1_kpmg/case-management-backend/docs/week3-practical-labs.md). Observe how boundary selection affects retrieval precision.
- **BUILD:** Review [`rag/chunking/strategies.py`](file:///d:/week1_kpmg/case-management-backend/rag/chunking/strategies.py) and [`rag/embeddings/providers.py`](file:///d:/week1_kpmg/case-management-backend/rag/embeddings/providers.py).
- **TEST:** Run `pytest tests/test_rag_chunking.py -v`.

---

### Day 3: Lexical Search (BM25) & Hybrid Fusion
- **LEARN:** Understand lexical blindness in pure vector search. Study Robertson-Spärck Jones IDF vs Lucene smoothed IDF. Understand Weighted Score Fusion ($\alpha=0.6$) and Reciprocal Rank Fusion (RRF).
- **PRACTICE:** Complete Lab 4 in [`docs/week3-practical-labs.md`](file:///d:/week1_kpmg/case-management-backend/docs/week3-practical-labs.md).
- **BUILD:** Inspect [`rag/indexing/bm25_index.py`](file:///d:/week1_kpmg/case-management-backend/rag/indexing/bm25_index.py) and [`rag/indexing/hybrid_index.py`](file:///d:/week1_kpmg/case-management-backend/rag/indexing/hybrid_index.py).
- **TEST:** Run `pytest tests/test_rag_embeddings_indices.py -v`.

---

### Day 4: Candidate Reranking & Grounded Generation
- **LEARN:** Study two-stage retrieval: Bi-Encoder first stage + Cross-Encoder reranking stage. Study token budget enforcement, prompt templates, citation validation, and formal refusals.
- **PRACTICE:** Complete Lab 5 in [`docs/week3-practical-labs.md`](file:///d:/week1_kpmg/case-management-backend/docs/week3-practical-labs.md). Test how out-of-domain queries trigger formal refusals.
- **BUILD:** Review [`rag/retrieval/reranker.py`](file:///d:/week1_kpmg/case-management-backend/rag/retrieval/reranker.py) and [`rag/generation/generator.py`](file:///d:/week1_kpmg/case-management-backend/rag/generation/generator.py).
- **TEST:** Run `pytest tests/test_rag_retrieval_rerank.py tests/test_rag_context_generation.py -v`.

---

### Day 5: Evaluation, Case Integration & Senior Review
- **LEARN:** Study evaluation metrics: Precision@k, Recall@k, MRR (Mean Reciprocal Rank), Hit Rate, and Faithfulness.
- **EVALUATE:** Run `python -m rag.cli evaluate` to compare Strategy A (Vector Only) vs Strategy B (Hybrid + Reranker).
- **INTEGRATE:** Inspect [`app/api/routes/rag.py`](file:///d:/week1_kpmg/case-management-backend/app/api/routes/rag.py) and test `POST /api/v1/rag/cases/{id}/policy-check`.
- **DOCUMENT & REVIEW:** Read [`docs/rag-failure-analysis.md`](file:///d:/week1_kpmg/case-management-backend/docs/rag-failure-analysis.md) and [`learning/week3/week3-interview-questions.md`](file:///d:/week1_kpmg/case-management-backend/learning/week3/week3-interview-questions.md). Complete the self-assessment in [`learning/week3/week3-self-assessment.md`](file:///d:/week1_kpmg/case-management-backend/learning/week3/week3-self-assessment.md).
- **FINAL VERIFICATION:** Run `pytest --cov=app --cov=pipeline --cov=rag` to verify 100 passing tests and 86%+ code coverage.
