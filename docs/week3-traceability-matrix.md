# Week 3 — Requirement Traceability Matrix (RTM)

> **Program:** FDE Fresher Readiness Program — Week 3  
> **Topic:** Grounded RAG Policy Knowledge Assistant  
> **Regression Baseline:** 68 passed (Week 1 + Week 2)  
> **Current Test Status:** **100 passed, 0 failed, 86.78% total code coverage**

---

| Curriculum Requirement | Implementation Source Files | Primary Classes / Functions | Test Files & Verifications |
|---|---|---|---|
| **1. Grounded RAG Service** | `rag/pipeline.py` | `RAGPipeline` | `tests/test_rag_context_generation.py`, `tests/test_rag_api.py` |
| **2. Document Ingestion** | `rag/ingestion/parser.py` | `DocumentParser`, `MarkdownDocumentParser`, `PDFDocumentParser` | `tests/test_rag_ingestion.py::test_markdown_parser_with_frontmatter`, `test_document_parser_load_policies_dir` |
| **3. Document Preprocessing** | `rag/ingestion/preprocessor.py` | `DocumentPreprocessor` | `tests/test_rag_ingestion.py::test_preprocessor_normalize_whitespace`, `test_preprocessor_clean_control_characters`, `test_preprocessor_estimate_token_count` |
| **4. Chunking Strategies** | `rag/chunking/strategies.py` | `FixedSizeChunker`, `RecursiveCharacterChunker`, `MarkdownSectionChunker` | `tests/test_rag_chunking.py::test_fixed_size_chunker`, `test_recursive_character_chunker`, `test_markdown_section_chunker`, `test_chunker_factory` |
| **5. Chunk Metadata Tracking** | `rag/chunking/strategies.py`, `rag/schemas.py` | `Chunk`, `DocumentMetadata` | `tests/test_rag_chunking.py`, `tests/test_rag_api.py::test_api_list_policies` |
| **6. Vector Embeddings** | `rag/embeddings/providers.py`, `rag/embeddings/base.py` | `DenseHashEmbeddingProvider`, `MockEmbeddingProvider`, `SentenceTransformerEmbeddingProvider` | `tests/test_rag_embeddings_indices.py::test_dense_hash_embedding_provider` |
| **7. Vector Indexing** | `rag/indexing/vector_index.py` | `VectorIndex` (Cosine similarity, L2 distance) | `tests/test_rag_embeddings_indices.py::test_vector_index` |
| **8. Keyword / BM25 Indexing** | `rag/indexing/bm25_index.py` | `BM25Index` (Lucene TF-IDF & Robertson-Spärck Jones smoothing) | `tests/test_rag_embeddings_indices.py::test_bm25_index` |
| **9. Hybrid Retrieval & Fusion** | `rag/indexing/hybrid_index.py` | `HybridIndex` (Weighted Score Fusion & RRF) | `tests/test_rag_embeddings_indices.py::test_hybrid_index` |
| **10. Metadata Filtering** | `rag/indexing/vector_index.py`, `rag/indexing/bm25_index.py` | `_matches_filters()` | `tests/test_rag_embeddings_indices.py`, `tests/test_rag_api.py::test_api_retrieve_with_filter` |
| **11. Candidate Reranking** | `rag/retrieval/reranker.py` | `CrossScoreReranker` | `tests/test_rag_retrieval_rerank.py::test_cross_score_reranker`, `test_retriever_multi_modes` |
| **12. Multi-Mode Retrieval Engine** | `rag/retrieval/retriever.py` | `Retriever` | `tests/test_rag_retrieval_rerank.py::test_retriever_multi_modes` |
| **13. Controlled Context Assembly** | `rag/context/assembler.py` | `ContextAssembler` (Token budgeting, source blocks) | `tests/test_rag_context_generation.py::test_context_assembler`, `test_context_assembler_budget_truncation` |
| **14. Grounded Answer Generation** | `rag/generation/generator.py` | `GroundedAnswerGenerator` | `tests/test_rag_context_generation.py::test_grounded_generator_accurate_answer` |
| **15. Citation Attribution & Validation** | `rag/generation/generator.py` | `_extract_and_verify_citations()` | `tests/test_rag_context_generation.py::test_grounded_generator_accurate_answer` |
| **16. Out-of-Domain Refusal** | `rag/generation/generator.py`, `rag/llm/provider.py` | `MockLLMProvider`, `_is_refusal()` | `tests/test_rag_context_generation.py::test_grounded_generator_out_of_domain_refusal`, `tests/test_rag_api.py::test_api_query_unanswerable_refusal` |
| **17. Evaluation Metrics** | `rag/evaluation/metrics.py` | `compute_precision_at_k`, `compute_recall_at_k`, `compute_mrr`, `compute_hit_rate`, `compute_faithfulness` | `tests/test_rag_evaluation.py::test_retrieval_metrics`, `test_faithfulness_metric` |
| **18. Comparative Benchmark Suite** | `rag/evaluation/evaluator.py` | `RAGEvaluator`, `BenchmarkQuery` | `tests/test_rag_evaluation.py::test_evaluator_comparison`, `tests/test_rag_api.py::test_api_benchmark_endpoint` |
| **19. FastAPI RAG Endpoints** | `app/api/routes/rag.py` | `POST /query`, `POST /retrieve`, `POST /ingest`, `GET /policies`, `GET /benchmark` | `tests/test_rag_api.py` (100% route coverage) |
| **20. Case Management Policy Check** | `app/api/routes/rag.py` | `POST /cases/{id}/policy-check` | `tests/test_rag_api.py::test_api_case_policy_check`, `test_api_case_policy_check_missing_case` |
| **21. Policy Corpus** | `data/policies/*.md` | 6 Realistic Policy Documents | Loaded and verified in `tests/test_rag_ingestion.py` |
| **22. Curriculum & Study Guide** | `docs/week3-rag-curriculum.md` | Master study guide | Markdown reference artifact |
| **23. System Architecture Doc** | `docs/week3-rag-architecture.md` | System design & module layouts | Markdown reference artifact |
| **24. Practical Hands-On Labs** | `docs/week3-practical-labs.md` | 6 Runnable laboratory exercises | Python code snippets and verification scripts |
| **25. Evaluation Benchmark Report** | `docs/week3-evaluation-report.md` | Strategy A vs Strategy B comparison | Quantitative benchmark report |
