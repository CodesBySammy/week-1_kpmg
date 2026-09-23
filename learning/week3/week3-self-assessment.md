# Week 3 — Self-Assessment & Knowledge Check

> **Self-Evaluation:** Complete the questions below to test your mastery of Week 3 RAG concepts.  
> **Target:** 85%+ score indicates full readiness for senior RAG engineering.

---

## Part 1: Multiple Choice Questions (MCQs)

#### 1. Why do we normalize embedding vectors to unit length ($\|v\|_2 = 1$)?
- [ ] A) To compress 32-bit floats into 8-bit integers.
- [x] B) So that Cosine Similarity becomes a simple dot product, eliminating expensive square root and norm operations during search.
- [ ] C) To prevent gradient explosion during LLM inference.
- [ ] D) Because BM25 requires unit-length document vectors.
*Explanation:* For unit vectors, $\|\mathbf{u}\| = 1$ and $\|\mathbf{v}\| = 1$. The cosine similarity $\frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\| \|\mathbf{v}\|}$ simplifies directly to $\mathbf{u} \cdot \mathbf{v}$.

#### 2. When does standard BM25Okapi fail on small document collections ($N < 5$)?
- [ ] A) It throws a division by zero error on short texts.
- [ ] B) Document lengths cannot be averaged.
- [x] C) When a term appears in more than half the documents, the Robertson-Spärck Jones IDF becomes zero or negative.
- [ ] D) Tokenizers cannot handle stop words in small files.
*Explanation:* In Robertson-Spärck Jones IDF formula $\ln(\frac{N - n + 0.5}{n + 0.5})$, when $n > N/2$, the ratio is $< 1$, making $\ln(\text{ratio}) < 0$. Lucene fixes this by adding 1 inside the logarithm.

#### 3. What is the primary advantage of Markdown Section Chunking over Fixed-Size Chunking?
- [ ] A) It produces chunks of identical character length.
- [x] B) It respects document hierarchy, keeps clauses with their parent headers, and avoids cutting sentences mid-thought.
- [ ] C) It does not require tokenization.
- [ ] D) It eliminates the need for vector embeddings.
*Explanation:* Markdown section chunkers use heading tags (`#`, `##`) as natural semantic boundaries.

#### 4. In a two-stage retrieval pipeline, why do we not run the Reranker on the entire corpus?
- [ ] A) Rerankers cannot handle markdown text.
- [x] B) Cross-encoder rerankers require joint self-attention across query and document tokens, making them 100x slower than vector dot products.
- [ ] C) Vector indexes cannot store rerank scores.
- [ ] D) Rerankers only work on metadata, not text.
*Explanation:* Cross-encoders evaluate query and candidate chunks jointly through full attention layers, which is computationally prohibitive over thousands of chunks.

#### 5. If a user asks *"What is the policy for international travel to Mars?"*, what should a well-engineered RAG system do?
- [ ] A) Speculate based on general airline policies.
- [ ] B) Return the top 3 closest chunks about domestic airfare.
- [x] C) Recognize that context lacks relevant facts and emit an explicit formal refusal.
- [ ] D) Crash with an HTTP 500 error.
*Explanation:* Zero-hallucination systems enforce strict grounding and formal refusal when similarity thresholds or keyword overlaps indicate out-of-domain queries.

---

## Part 2: Calculation & Scenario Problems

### Problem 1: Retrieval Metrics Calculation
Given 10 retrieved chunks for a query where the ground-truth relevant documents are `{D3, D7}`:
- Retrieved list: `[D1, D4, D3, D9, D7, D2, D8, D10, D5, D6]`

Calculate:
1. **Precision@3:**
   - In top 3 `[D1, D4, D3]`, only `D3` is relevant.
   - $\text{Precision@3} = \frac{1}{3} \approx 0.3333$.
2. **Recall@5:**
   - In top 5 `[D1, D4, D3, D9, D7]`, both `D3` and `D7` are found.
   - $\text{Recall@5} = \frac{2}{2} = 1.0000$ (100% recall).
3. **MRR (Mean Reciprocal Rank):**
   - First relevant document (`D3`) appears at Rank 3.
   - $\text{MRR} = \frac{1}{3} \approx 0.3333$.
4. **Hit Rate@3:**
   - At least one relevant document is in top 3 (`D3` is at Rank 3).
   - $\text{Hit Rate@3} = 1.0$.

---

## Part 3: Architecture Challenge

**Scenario:** An employee submits an expense of $120 for dinner with a client. The system must verify whether this requires Department Head pre-approval.
- Explain which policy documents and sections must be retrieved.
- Explain how the query should be routed.

**Model Answer:**
1. **Target Policy:** `COMPLIANCE-POLICY-006.md`, Section 2.1 (*Gifts, Hospitality, and Entertainment*).
2. **Rule Checked:** Section 2.1 states:
   - Modest Hospitality ($< $50): No prior approval needed.
   - Moderate Hospitality ($50 to $150): Requires documented pre-approval from Department Head.
   - High-Value ($> $150): Requires Chief Compliance Officer approval.
3. **Conclusion:** Because $120 falls in the $50–$150 band, Department Head pre-approval is required. The assistant cites `[COMPLIANCE-POLICY-006, Section 2.1]`.
