"""
Evaluation metrics for RAG retrieval and generation quality.
"""
from typing import List, Set, Optional
import re


def compute_precision_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    """Fraction of retrieved items in top_k that are truly relevant."""
    if k <= 0 or not retrieved_ids:
        return 0.0
    top_k_items = retrieved_ids[:k]
    hits = sum(1 for item in top_k_items if item in relevant_ids)
    return hits / float(k)


def compute_recall_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    """Fraction of all relevant items that were retrieved in top_k."""
    if not relevant_ids or k <= 0:
        return 0.0
    top_k_items = retrieved_ids[:k]
    hits = sum(1 for item in top_k_items if item in relevant_ids)
    return hits / float(len(relevant_ids))


def compute_mrr(retrieved_ids: List[str], relevant_ids: Set[str]) -> float:
    """Mean Reciprocal Rank (MRR): 1 / rank of first relevant item, or 0 if none found."""
    for rank, item in enumerate(retrieved_ids, start=1):
        if item in relevant_ids:
            return 1.0 / rank
    return 0.0


def compute_hit_rate(retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    """Hit Rate: 1.0 if any relevant item is present in top_k, else 0.0."""
    top_k_items = retrieved_ids[:k]
    return 1.0 if any(item in relevant_ids for item in top_k_items) else 0.0


def compute_faithfulness(answer: str, context_text: str) -> float:
    """
    Computes lexical grounding faithfulness of answer statements against context.
    Evaluates what fraction of answer claims / key terms are grounded in context.
    """
    if not answer or not context_text:
        return 0.0

    # Extract claims / words from answer
    answer_terms = [t.lower() for t in re.findall(r"[a-zA-Z0-9_\-]+", answer) if len(t) > 3]
    if not answer_terms:
        return 1.0

    grounded_terms = sum(1 for t in answer_terms if t in context_text.lower())
    return round(grounded_terms / len(answer_terms), 4)
