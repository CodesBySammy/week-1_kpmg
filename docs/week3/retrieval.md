# Dual-Engine Hybrid Retrieval & Fusion

## 1. Dense Vector Retrieval
- **Embedding Model:** 384-dimensional dense vectors with stopword downweighting and character n-gram projections.
- **Normalization:** Vectors are pre-normalized to unit length (L2 norm = 1.0).
- **Similarity Calculation:** Fast NumPy dot product equivalent to Cosine Similarity.

## 2. Sparse Lexical Search (BM25)
- **Algorithm:** BM25 with Lucene smoothed IDF formulation $\ln(1 + \frac{N - n + 0.5}{n + 0.5})$.
- **Strength:** Captures exact alphanumeric policy codes (e.g. `EXPENSE-POLICY-003`, `IT-SECURITY-005`).

## 3. Score Fusion
- **Algorithm:** Weighted Score Fusion with $\alpha = 0.6$ vector weight and $0.4$ BM25 weight:
  $$\text{Score} = 0.6 \cdot S_{\text{vector}} + 0.4 \cdot S_{\text{bm25}}$$
