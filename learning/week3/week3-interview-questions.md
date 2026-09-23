# Week 3 — Senior AI & RAG Engineer Interview Preparation Guide

> **Target Roles:** Senior AI Engineer, RAG Architect, LLM Application Engineer  
> **Topic:** 25 In-Depth Technical Interview Questions with Production-Grade Model Answers

---

### Q1: What is the difference between Fine-Tuning and RAG? When should you use which?
**Answer:**
- **RAG (Retrieval-Augmented Generation):** Keeps the model frozen and supplies external knowledge at runtime via prompt context. Use RAG when:
  1. Knowledge changes frequently (daily policies, stock prices, news).
  2. Exact, auditable source citations (clause IDs, page numbers) are mandatory.
  3. Hallucination risk must be minimized through factual constraints.
  4. Role-based access control (RBAC) is needed (users only retrieve chunks they are authorized to see).
- **Fine-Tuning:** Updates the internal model weights. Use Fine-Tuning when:
  1. Teaching the model a specialized output style, syntax, or tone (e.g., generating proprietary SQL or diagnostic code).
  2. Distilling a 70B parameter model into an 8B model for latency/cost reduction.
  3. The task requires broad domain understanding rather than specific factual retrieval.
*Best Practice:* In enterprise systems, combine them: Fine-tune for form/style, use RAG for factual content.

---

### Q2: Why does Cosine Similarity equal the Dot Product for normalized vectors?
**Answer:**
Cosine similarity is defined as:
$$\cos(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2}$$
When embedding vectors are pre-normalized to unit Euclidean length ($\|\mathbf{u}\|_2 = 1$ and $\|\mathbf{v}\|_2 = 1$), the denominator equals $1 \times 1 = 1$. Therefore:
$$\cos(\mathbf{u}, \mathbf{v}) = \mathbf{u} \cdot \mathbf{v} = \sum_{i=1}^D u_i v_i$$
This is a critical production optimization: computing a matrix dot product using optimized BLAS/NumPy routines (`np.dot`) avoids expensive square root and norm calculations during k-NN queries.

---

### Q3: Why is Vector Search alone insufficient for enterprise policy search?
**Answer:**
Dense vector embeddings map semantic concepts well ("inexpensive flights" $\approx$ "cheap airfare"), but suffer from **lexical blindness**:
1. Exact identifiers (e.g., `HR-POLICY-001` vs `HR-POLICY-002`) have nearly identical embeddings because their surrounding context is identical.
2. Exact numeric values (`$150` vs `$50`) are frequently clustered together in dense semantic space.
3. Acronyms and rare jargon (e.g., `OFAC`, `FCPA`, `FIDO2`) may not have strong representations in general embedding models.
*Solution:* Hybrid retrieval pairing dense vectors with sparse lexical BM25 search.

---

### Q4: Explain the difference between Bi-Encoders and Cross-Encoders. Why use Cross-Encoders for Reranking?
**Answer:**
- **Bi-Encoder (Embedding Model):** Embeds the query and document independently into separate vectors: $\mathbf{u} = E(Q)$ and $\mathbf{v} = E(D)$. The similarity is computed via dot product $\mathbf{u} \cdot \mathbf{v}$. This allows pre-computing document vectors offline, making search across millions of documents feasible in milliseconds via ANN indexes.
- **Cross-Encoder (Reranker):** Passes the query and document *together* into the transformer: $S = \text{Model}(Q \oplus D)$. Self-attention layers compute cross-token attention between every word in the query and every word in the document simultaneously.
*Why Rerank:* Cross-encoders are 100x more computationally expensive than dot products, so we cannot run them on the entire corpus. Instead, we use a two-stage retrieval:
1. Fast Bi-Encoder + BM25 retrieves top-20 candidates.
2. Cross-Encoder reranks the top-20 candidates down to the top-3 most authoritative chunks.

---

### Q5: What is Reciprocal Rank Fusion (RRF) and why is it preferred over Weighted Score Fusion?
**Answer:**
- **Weighted Score Fusion:** $S = \alpha \cdot S_{\text{vec}} + (1 - \alpha) \cdot S_{\text{bm25}}$. Requires calibrating $\alpha$ and requires both scores to be normalized to the same scale $[0, 1]$. Because BM25 scores are unbounded $[0, \infty)$ and vector cosine similarities are $[-1, 1]$, normalization requires min-max scaling which is sensitive to outliers.
- **Reciprocal Rank Fusion (RRF):**
  $$\text{RRF}(d) = \sum_{m} \frac{1}{k + \text{Rank}_m(d)}$$
  RRF relies strictly on candidate *rank positions* rather than raw scores. It is completely distribution-free, requires no score normalization, and penalizes candidates that appear deep in rank lists. $k=60$ is the standard smoothing constant.

---

### Q6: How do you measure Groundedness / Faithfulness in RAG?
**Answer:**
Faithfulness measures whether every claim made in the generated answer can be mathematically or logically deduced from the retrieved context:
1. **Sentence Claim Decomposition:** Break down the generated answer into atomic claims $C_1, C_2, \dots, C_n$.
2. **Context Entailment Verification:** For each claim $C_i$, evaluate whether context $T$ entails $C_i$ (using Natural Language Inference models or an LLM-as-judge prompt).
3. **Score:**
   $$\text{Faithfulness} = \frac{\text{Number of substantiated claims}}{\text{Total number of claims in answer}}$$
In our test suite, we also implement exact citation cross-checking: if an answer cites a document ID not present in the retrieved chunk index, the answer is flagged as ungrounded (`is_grounded = False`).

---

### Q7: What is Mean Reciprocal Rank (MRR)? Compute it for this example:
*Queries:*
- Query 1: First relevant document at Rank 2.
- Query 2: First relevant document at Rank 1.
- Query 3: First relevant document at Rank 4.
**Answer:**
MRR is the average of reciprocal ranks of the first relevant document across all queries:
$$\text{MRR} = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{Rank}_i}$$
$$\text{Reciprocal Ranks:} \quad Q_1 = \frac{1}{2} = 0.50, \quad Q_2 = \frac{1}{1} = 1.00, \quad Q_3 = \frac{1}{4} = 0.25$$
$$\text{MRR} = \frac{0.50 + 1.00 + 0.25}{3} = \frac{1.75}{3} \approx 0.5833$$

---

### Q8: How do you prevent context poisoning and prompt injection in RAG?
**Answer:**
1. **Structural Delimiters:** Enclose context chunks in strict XML or markdown tags (`<context>...</context>`).
2. **Role Separation:** Enforce system instructions in the `system` role message that cannot be overridden by user inputs or context strings.
3. **Pre-processing Sanitization:** Strip out system prompt override triggers (e.g. `Ignore previous instructions and do X`) from untrusted uploaded documents before indexing.
4. **Output Verification:** Assert that model output citations map strictly to known internal document IDs and do not leak hidden system prompts.
