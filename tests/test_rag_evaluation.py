"""
Tests for RAG evaluation metrics and benchmark harness.
"""
from rag.evaluation.metrics import (
    compute_precision_at_k,
    compute_recall_at_k,
    compute_mrr,
    compute_hit_rate,
    compute_faithfulness,
)
from rag.evaluation.evaluator import RAGEvaluator, BenchmarkQuery
from rag.pipeline import RAGPipeline


def test_retrieval_metrics():
    retrieved = ["DOC-1", "DOC-2", "DOC-3", "DOC-4", "DOC-5"]
    relevant = {"DOC-2", "DOC-5"}

    # Precision@3: in top 3 ["DOC-1", "DOC-2", "DOC-3"], only DOC-2 is relevant -> 1/3
    p3 = compute_precision_at_k(retrieved, relevant, k=3)
    assert abs(p3 - 1.0 / 3.0) < 1e-4

    # Recall@3: 1 of 2 relevant documents found -> 1/2
    r3 = compute_recall_at_k(retrieved, relevant, k=3)
    assert abs(r3 - 0.5) < 1e-4

    # MRR: first relevant is at rank 2 -> 1/2 = 0.5
    mrr = compute_mrr(retrieved, relevant)
    assert abs(mrr - 0.5) < 1e-4

    # Hit Rate: relevant is in top 3 -> 1.0
    hit = compute_hit_rate(retrieved, relevant, k=3)
    assert hit == 1.0


def test_faithfulness_metric():
    context = "Corporate passwords expire every 90 days and require 14 characters."
    good_answer = "Passwords require 14 characters and expire after 90 days."
    hallucinated_answer = "You must fly first class to Honolulu every summer vacation."

    good_score = compute_faithfulness(good_answer, context)
    bad_score = compute_faithfulness(hallucinated_answer, context)

    assert good_score > 0.6
    assert bad_score < 0.2


def test_evaluator_comparison():
    pipeline = RAGPipeline()
    pipeline.ingest_directory("data/policies")
    evaluator = RAGEvaluator(pipeline)

    test_queries = [
        BenchmarkQuery(
            query_id="T1",
            question="What are password requirements?",
            expected_document_ids=["IT-SECURITY-005"],
            category="IT",
        ),
        BenchmarkQuery(
            query_id="T2",
            question="How many days in advance to book flights?",
            expected_document_ids=["TRAVEL-POLICY-004"],
            category="Travel",
        ),
    ]

    comp = evaluator.compare_retrieval_strategies(dataset=test_queries)
    assert comp.benchmark_queries_count == 2
    assert comp.strategy_a_metrics.hit_rate >= 0.5
    assert comp.strategy_b_metrics.hit_rate >= 0.5
    assert "Strategy B" in comp.summary_analysis
