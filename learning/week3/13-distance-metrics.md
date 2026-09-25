# Vector Distance Metrics: Cosine, Dot Product & L2

## 1. What It Is
Mathematical comparison of Cosine Similarity, Dot Product of unit vectors, and Euclidean L2 distance.

## 2. Why It Exists
Vanilla Large Language Models suffer from knowledge cutoffs, zero private domain awareness, and hallucination risks. In enterprise environments, decisions must be grounded in verified, auditable corporate policies with explicit citations.

## 3. Why It Matters
Without grounded retrieval and strict context boundaries, an enterprise AI assistant will generate plausible-sounding but legally inaccurate answers, exposing the organization to compliance violations, operational disputes, and financial loss.

## 4. How It Works
1. **Document Ingestion:** Raw Markdown and PDF documents are sanitized, frontmatter is parsed, and metadata is structured.
2. **Chunking & Indexing:** Text is partitioned into semantically intact sections and indexed into dual dense vector and sparse BM25 indices.
3. **Hybrid Retrieval & Reranking:** Queries retrieve candidates across both indices, combined via score fusion, and promoted by a cross-score reranker.
4. **Context Assembly & Generation:** Context is bounded by a token budget, injected into a grounded prompt template, and evaluated by the generator.
5. **Verification & Refusal:** Citations are cross-checked against source chunk IDs, and unanswerable queries trigger formal refusals.

## 5. Important Terminology
- **Parametric Memory:** Knowledge baked into the neural weights of an LLM during training.
- **Non-Parametric Memory:** External document index retrieved dynamically at query time.
- **Chunking:** Partitioning large documents into smaller passages suitable for vector search and LLM context windows.
- **BM25:** Best Matching 25, a probabilistic ranking function used in information retrieval.
- **Cosine Similarity:** Dot product of two normalized unit vectors measuring geometric angle.
- **Hit Rate:** Proportion of benchmark queries where the ground-truth document appears in top-k results.
- **Faithfulness:** Proportion of generated statements that can be directly inferred from the retrieved context.

## 6. Simple Example
```python
# Minimal conceptual hybrid scoring
def hybrid_score(vector_sim, bm25_score, alpha=0.6):
    return alpha * vector_sim + (1 - alpha) * bm25_score
```

## 7. Real-World Example
An employee asks: *"What is the meal allowance during domestic travel?"*  
The RAG system retrieves `EXPENSE-POLICY-003`, Section 4.2 ($75/day limit), injects it into the prompt, and responds with exact dollar figures and the clause citation `[EXPENSE-POLICY-003, Section 4.2]`.

## 8. Example from This Project
In `rag/generation/generator.py`, `GroundedAnswerGenerator` validates every bracketed citation against the retrieved chunks. If an out-of-domain query is asked (e.g. *"What is the weather in Paris?"*), the system outputs:
*"I am unable to answer this question based on the provided policy documents."*

## 9. Common Mistakes
- Using fixed-size chunking that cuts sentences or tables mid-thought.
- Relying solely on vector embeddings for exact policy IDs, acronyms, or numbers.
- Flooding the LLM context window with excess irrelevant text causing attention dilution.
- Allowing the LLM to answer using outside parametric knowledge when evidence is missing.

## 10. Good Practices
- Use section-aware chunking for structured policy and legal documentation.
- Implement hybrid retrieval (Dense Vector + Lucene Smoothed BM25) with candidate reranking.
- Enforce hard token budgets during context assembly (e.g. 2,000 tokens maximum).
- Validate all citations against retrieved chunk metadata before returning answers.

## 11. Bad Practices
- Fine-tuning an LLM whenever corporate policies change (expensive, slow, prone to hallucination).
- Ignoring negative IDF values in un-smoothed BM25 implementations on small collections.
- Returning answers without verifiable document citations.

## 12. When to Use It
Use RAG whenever answering questions over dynamic, private, rapidly changing, or compliance-critical documents where hallucinations cannot be tolerated.

## 13. When Not to Use It
For general open-ended creative writing, style transformation, or basic grammar correction where domain document retrieval is unnecessary.

## 14. Security Implications
Ensures enterprise data privacy by running retrieval locally without sending proprietary contracts to third-party model retraining pipelines. When combined with access-aware filtering, unauthorized users cannot retrieve sensitive policies.

## 15. Testing Implications
Automated tests verify:
- Parsing of YAML frontmatter and PDF documents.
- Mathematical correctness of Cosine, Dot Product, and BM25 smoothing.
- Token budget truncation behavior.
- Out-of-domain refusal enforcement.
- Citation cross-validation.

## 16. Practical Exercise
Run the Week 3 RAG test suite to verify this component:
```bash
pytest tests/ -k rag -v
```

## 17. Senior Interview Questions
- **Q:** *Why does Hybrid Search (Dense + Sparse) outperform pure Vector Search on enterprise policies?*  
  **A:** *Dense embeddings excel at semantic paraphrasing but fail on exact keyword codes, acronyms, and clause numbers. BM25 provides exact keyword precision, while vector search provides semantic recall; fusing them eliminates blind spots of both approaches.*

## 18. Self-Test
1. What distance metric between unit vectors is mathematically identical to Dot Product?  
   *(Answer: Cosine Similarity)*
2. What response behavior is mandatory when retrieved context contains no relevant evidence?  
   *(Answer: Formal out-of-domain refusal with zero hallucination)*
