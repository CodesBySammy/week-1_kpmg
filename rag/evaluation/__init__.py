"""
RAG Evaluation and Benchmarking subpackage.
"""
from .metrics import (
    compute_precision_at_k,
    compute_recall_at_k,
    compute_mrr,
    compute_hit_rate,
    compute_faithfulness,
)
from .evaluator import RAGEvaluator, BenchmarkQuery

__all__ = [
    "compute_precision_at_k",
    "compute_recall_at_k",
    "compute_mrr",
    "compute_hit_rate",
    "compute_faithfulness",
    "RAGEvaluator",
    "BenchmarkQuery",
]
