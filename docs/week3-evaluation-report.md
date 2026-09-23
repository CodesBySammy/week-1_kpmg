# Week 3 — RAG Benchmark Evaluation & Comparison Report

> **Evaluation Date:** September 2026  
> **Test Suite:** Enterprise Policy Retrieval Benchmark (8 Standard Test Queries)  
> **Corpus:** 6 Corporate Policy Documents (100 Chunks)

---

## 1. Executive Summary

This report evaluates two retrieval architectures for the Corporate Policy Knowledge Assistant:
- **Strategy A:** Baseline Dense Vector Search Only (top_k=5)
- **Strategy B:** Hybrid Retrieval (Dense Vector + BM25 Lexical with Weighted Fusion $\alpha=0.6$) and CrossScore Reranking (top_k=3)

### Key Results Summary Table

| Metric | Strategy A: Vector Only (k=5) | Strategy B: Hybrid + Reranking (k=3) | Delta / Improvement |
|---|---|---|---|
| **Hit Rate** | 100.0% | 100.0% | Parity (100% reliability) |
| **MRR (Mean Reciprocal Rank)** | 0.7917 | **0.9375** | **+18.4% improvement** |
| **Precision@k** | 0.2000 | **0.3333** | **+66.7% improvement** |
| **Recall@k** | 1.0000 | 1.0000 | Parity |
| **Average Latency** | **0.18 ms** | 0.35 ms | Sub-millisecond (Real-time) |
| **Faithfulness Score** | 0.9420 | **0.9650** | **+2.4% higher grounding** |

---

## 2. In-Depth Metric Analysis

### 2.1 Mean Reciprocal Rank (MRR)
- **Strategy A (0.7917):** In queries with technical identifiers (such as `IT-SECURITY-005` or numerical thresholds like `14 days`), the dense vector embedding occasionally ranked general policy overviews above the specific clause.
- **Strategy B (0.9375):** The inclusion of BM25 exact keyword matching combined with CrossScore term coverage boosted the exact clause containing the answer to Rank 1 in 7 out of 8 queries.

### 2.2 Precision@k & Context Efficiency
- By reducing the required context window from $k=5$ chunks down to $k=3$ chunks without sacrificing recall, **Strategy B reduces prompt token overhead by 40%**, cutting LLM inference costs and latency.

### 2.3 Qualitative Case Study: Query BM-002
- **Query:** *"How many days in advance must business flights be booked?"*
- **Target Clause:** `TRAVEL-POLICY-004`, Section 2.1 (*"Domestic flights must be booked in economy class at least 14 days prior to departure."*)
- **Strategy A Result:** Returned `EXPENSE-POLICY-003` at Rank 1 (general expense overview), and `TRAVEL-POLICY-004` at Rank 2. ($RR = 0.50$).
- **Strategy B Result:** The BM25 lexical signal matched `"business flights booked"`, while CrossScore reranker boosted the section title `2.1 Booking Window`. Result: `TRAVEL-POLICY-004` ranked at Rank 1. ($RR = 1.00$).

---

## 3. Engineering Recommendations

1. **Deploy Strategy B in Production:** Hybrid retrieval with CrossScore reranking delivers superior rank precision with negligible compute overhead (0.35 ms).
2. **Metadata Pre-Filtering:** Apply category filters (e.g. `filters={"category": "Finance"}`) for case management compliance workflows to restrict search space and eliminate cross-department noise.
3. **Continuous Grounding Auditing:** Maintain automated tests that assert faithfulness scores above 0.90 to guard against prompt degradation.
