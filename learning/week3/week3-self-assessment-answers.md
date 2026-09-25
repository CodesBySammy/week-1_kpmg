# Week 3 Self-Assessment Detailed Answers & Explanations

This document provides detailed answers, explanations, and engineering context for the questions in `learning/week3/week3-self-assessment.md`.

---

### Question 1: Why does RAG outperform Fine-Tuning for corporate policy Q&A?
**Answer:**
RAG decouples knowledge storage from language generation. Updating corporate policies in RAG simply requires re-indexing the updated text document (seconds/minutes), whereas fine-tuning requires hours of GPU compute, expensive data preparation, and still suffers from hallucination because neural weights cannot guarantee exact quote retrieval or verifiable citations.

---

### Question 2: Why does Markdown Section Chunking preserve more semantic value than Fixed-Size Chunking?
**Answer:**
Fixed-size chunking blindly splits text at arbitrary character or token counts, often cutting sentences in half or separating a list item from its parent clause. Markdown Section Chunking respects structural header tags (`#`, `##`, `###`), ensuring that an entire policy rule, condition, and exception remain together in a single coherent passage.

---

### Question 3: How does unit vector normalization simplify Cosine Similarity computation?
**Answer:**
Cosine similarity is defined as $(u \cdot v) / (||u||_2 \times ||v||_2)$. When all embedding vectors are pre-normalized to have an L2 norm of 1.0 ($||u|| = 1$), the denominator becomes $1 \times 1 = 1$. Consequently, Cosine Similarity simplifies to the pure dot product $\sum u_i v_i$, which is computed at high speed using vectorized matrix multiplications in NumPy or BLAS.

---

### Question 4: What is the primary weakness of pure Dense Vector Search that BM25 solves?
**Answer:**
Vector embeddings compress text into continuous semantic space. While this excels at synonyms and conceptual matches, it struggles with exact alphanumeric identifiers, policy codes (e.g. `HR-POLICY-001` vs `HR-POLICY-002`), product SKUs, and specialized abbreviations. BM25 inverted indices excel at exact token frequency matching, making hybrid search essential.

---

### Question 5: Why is Lucene smoothing applied to Robertson-Spärck Jones IDF?
**Answer:**
In standard Okapi BM25, the inverse document frequency term can become zero or negative when a term appears in more than half of the corpus documents ($n > N/2$). Lucene smoothed IDF formulation $\ln(1 + \frac{N - n + 0.5}{n + 0.5})$ ensures that the IDF weight is strictly non-negative, preventing common terms from subtracting from a document's relevance score.

---

### Question 6: What is the purpose of candidate reranking in two-stage retrieval?
**Answer:**
First-stage retrieval (Bi-encoder vectors and BM25) prioritizes high recall and computational speed across thousands of documents. The candidate reranker (Cross-encoder or multi-factor scorer) prioritizes high precision across the top-10 or top-20 candidates, analyzing exact phrase positioning, clause alignment, and header relevance to place the single most accurate passage at Rank 1.

---

### Question 7: Why is token budgeting mandatory during context assembly?
**Answer:**
Context windows in Large Language Models are finite and costly. Packing excessive retrieved text into the prompt leads to:
1. Higher inference latency and token billing.
2. "Lost in the Middle" attention degradation, where LLMs miss critical facts buried in long contexts.
A token-bounded context assembler caps the total injected context (e.g. max 2,000 tokens), selecting only the highest-ranked evidence passages.

---

### Question 8: How does the system handle queries when retrieved evidence is insufficient?
**Answer:**
The grounded generator enforces a deterministic out-of-domain refusal directive:
*"I am unable to answer this question based on the provided policy documents."*
It will never fabricate advice or hallucinate rules outside the provided context passages.

---

### Question 9: What do Precision@k and Recall@k measure in RAG evaluation?
**Answer:**
- **Precision@k:** The proportion of the top-k retrieved chunks that are genuinely relevant to the query.
- **Recall@k:** The proportion of all relevant policy passages in the corpus that were successfully retrieved in the top-k results.

---

### Question 10: How does the platform connect Case Management with Policy Knowledge?
**Answer:**
Via the `POST /api/v1/rag/cases/{id}/policy-check` endpoint. When a case is updated, the system fetches the case description and status from the SQLite database, runs hybrid retrieval against corporate policy manuals, and generates compliance guidance citing exact policy clauses.
