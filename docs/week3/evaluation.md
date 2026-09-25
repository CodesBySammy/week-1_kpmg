# Quantitative RAG Evaluation Framework

## 1. Benchmark Metrics
- **Hit Rate:** Proportion of queries where the correct document appears in top-k.
- **MRR (Mean Reciprocal Rank):** Average reciprocal rank of the first relevant document ($1/\text{rank}$).
- **Precision@k:** Proportion of retrieved chunks that are relevant.
- **Faithfulness Score:** Proportion of generated statements supported by retrieved context.

## 2. A/B Strategy Benchmark Results
| Metric | Strategy A (Vector Only) | Strategy B (Hybrid + Reranker) | Improvement |
|---|:---:|:---:|:---:|
| **Hit Rate** | 87.5% | **100.0%** | **+12.5%** |
| **MRR** | 0.6292 | **0.9167** | **+45.7%** |
| **Precision@k** | 0.4750 | **0.7917** | **+66.7%** |
| **Average Latency** | 8.97 ms | **0.87 ms** | Sub-millisecond |
| **Faithfulness** | 0.9384 | **0.9388** | Grounded |
