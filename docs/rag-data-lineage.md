# Week 3 — RAG Data Lineage & Provenance Specification

> **Document Version:** 1.0.0  
> **Topic:** End-to-End Data Transformation Lineage from Unstructured Policy Files to Citation-Attributed Answers

---

## 1. End-to-End Lineage Flow Diagram

```
+---------------------------------------------------------------------------------+
| 1. RAW POLICY SOURCE                                                            |
| Source File: data/policies/IT-SECURITY-005.md                                   |
| Format: Markdown with YAML Frontmatter                                          |
+---------------------------------------+-----------------------------------------+
                                        |
                                        v
+---------------------------------------------------------------------------------+
| 2. PARSED DOCUMENT (Document Object)                                            |
| Parser: rag.ingestion.parser.MarkdownDocumentParser                             |
| Extracted Metadata:                                                             |
|   document_id: "IT-SECURITY-005"                                                |
|   title: "Information Security and Acceptable Use Policy"                       |
|   category: "IT & Security"                                                     |
|   effective_date: "2025-01-01"                                                  |
+---------------------------------------+-----------------------------------------+
                                        |
                                        v
+---------------------------------------------------------------------------------+
| 3. PREPROCESSED TEXT                                                            |
| Preprocessor: rag.ingestion.preprocessor.DocumentPreprocessor                    |
| - Stripped ASCII control characters ([\x00-\x1f])                               |
| - Normalized Windows CRLF to standard LF                                        |
| - Collapsed whitespace while preserving paragraph headers                       |
| - Computed estimated token count                                                |
+---------------------------------------+-----------------------------------------+
                                        |
                                        v
+---------------------------------------------------------------------------------+
| 4. CHUNK GENERATION (Chunk Object)                                              |
| Chunker: rag.chunking.strategies.MarkdownSectionChunker                         |
| Generated Chunk ID: "IT-SECURITY-005_s002"                                      |
| Section Header: "2.1 Password Complexity Standards"                             |
| Chunk Metadata: {document_id, title, category, section_title, chunk_index: 2}   |
| Chunk Body: "All corporate user accounts must enforce a minimum length of 14..."|
+---------------------------------------+-----------------------------------------+
                                        |
                   +--------------------+--------------------+
                   |                                         |
                   v                                         v
+--------------------------------------+  +---------------------------------------+
| 5A. DENSE VECTORIZATION              |  | 5B. SPARSE TOKENIZATION               |
| Provider: DenseHashEmbeddingProvider |  | Index: rag.indexing.bm25_index        |
| Dimension: 384                       |  | Tokens: ["it-security-005", "password"|
| Norm: Unit Length (||v||_2 = 1.0)    |  |          "complexity", "standards"...]|
| Matrix: vector_matrix.npy            |  | Model: Lucene Smoothed IDF BM25       |
+------------------+-------------------+  +-------------------+-------------------+
                   |                                          |
                   +--------------------+---------------------+
                                        |
                                        v
+---------------------------------------------------------------------------------+
| 6. CANDIDATE RETRIEVAL & HYBRID FUSION                                          |
| Engine: rag.retrieval.retriever.Retriever                                       |
| User Query: "What are password requirements and expiration?"                    |
| Vector Cosine Dot: 0.2896 | BM25 Lexical Score: 1.0000                          |
| Weighted Fusion (alpha=0.6): Score = (0.6 * 0.2896) + (0.4 * 1.0) = 0.5738     |
+---------------------------------------+-----------------------------------------+
                                        |
                                        v
+---------------------------------------------------------------------------------+
| 7. RERANKING                                                                    |
| Reranker: rag.retrieval.reranker.CrossScoreReranker                             |
| Terms Matched: ["password", "requirements", "expiration"] (100% coverage)       |
| Section Alignment Bonus: Matched "Password Complexity Standards"                |
| Final Rerank Score: 0.9167 -> Assigned Rank 1                                   |
+---------------------------------------+-----------------------------------------+
                                        |
                                        v
+---------------------------------------------------------------------------------+
| 8. TOKEN-BOUND CONTEXT ASSEMBLY                                                 |
| Assembler: rag.context.assembler.ContextAssembler                               |
| Provenance Tag Injected:                                                        |
|   [Source 1: IT-SECURITY-005 — Information Security Policy | Section: 2.1]       |
| Token Budget Enforced: Max 2000 tokens                                          |
+---------------------------------------+-----------------------------------------+
                                        |
                                        v
+---------------------------------------------------------------------------------+
| 9. GROUNDED ANSWER GENERATION & CITATION VALIDATION                             |
| Generator: rag.generation.generator.GroundedAnswerGenerator                     |
| Generated Answer:                                                               |
|   "According to official policy [IT-SECURITY-005], user accounts require a      |
|    minimum length of 14 characters and expire every 90 days. [Source 1]"        |
| Citation Cross-Check: Verified [IT-SECURITY-005] against Citation Index         |
| Status: is_grounded = True | refusal = False                                    |
+---------------------------------------------------------------------------------+
```

---

## 2. Lineage Audit Fields in `RAGResponse`

Every API query returned by `/api/v1/rag/query` contains complete lineage traceability in its JSON response:
- `question`: Original user prompt.
- `citations[].document_id`: Traceable back to `data/policies/*.md`.
- `citations[].chunk_id`: Traceable back to exact chunk in `vector_index` and `bm25_index`.
- `citations[].section_title`: Traceable back to source document markdown header.
- `retrieved_chunks[].score`: Lineage of hybrid and rerank scores.
- `execution_time_ms`: Sub-millisecond performance audit.
- `context_token_count`: Prompt budget accounting.
