# RAG Failure Resolution Runbook

## Common RAG Failure Modes & Remediations

### 1. Symptom: Low Retrieval Precision (Irrelevant Chunks Retained)
- **Cause**: Overly broad query terms matching generic boilerplate text.
- **Resolution**:
  1. Increase BM25 minimum score threshold in `rag/retrieval/retriever.py`.
  2. Adjust reranker weights (60% vector, 40% BM25).
  3. Verify chunk size is within 300–500 tokens to avoid diluting semantic meaning.

### 2. Symptom: Missing Citations in Model Output
- **Cause**: LLM response omitted bracketed references `[1]`, `[2]`.
- **Resolution**:
  1. Strict post-generation parser extracts source citations.
  2. If citations are missing on factual queries, response is flagged as ungrounded and routed to human review.

### 3. Symptom: Context Token Budget Exceeded
- **Cause**: Top-K retrieval returned chunks totaling > 3000 tokens.
- **Resolution**:
  1. `ContextAssembler` strictly drops lower-ranked chunks when cumulative tokens reach the threshold.
  2. Log dropped chunk count in telemetry.
