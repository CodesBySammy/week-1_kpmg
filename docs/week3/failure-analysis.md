# RAG Failure Mode Taxonomy & Mitigation

## 1. Ingestion Failures
- **Symptom:** Missing sections or corrupted characters.
- **Mitigation:** Control character stripping (`\x00-\x1f`) and YAML frontmatter validation.

## 2. Chunking Failures
- **Symptom:** Cut-off sentences or severed tabular data.
- **Mitigation:** Markdown section-aware chunking preserving whole heading blocks.

## 3. Retrieval Failures
- **Symptom:** Exact policy IDs missed by vector embeddings.
- **Mitigation:** Lucene smoothed BM25 sparse keyword fusion.

## 4. Generation Failures
- **Symptom:** Hallucinated rules or citations.
- **Mitigation:** Citation cross-verification against chunk IDs and formal out-of-domain refusals.
