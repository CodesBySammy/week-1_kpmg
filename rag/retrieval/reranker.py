"""
Reranking modules for post-retrieval relevance refinement.
"""
from abc import ABC, abstractmethod
from typing import List
import re

from rag.schemas import RetrievedChunk


class BaseReranker(ABC):
    """Abstract base class for chunk rerankers."""

    @abstractmethod
    def rerank(self, query: str, candidates: List[RetrievedChunk], top_k: int = 3) -> List[RetrievedChunk]:
        """Reranks candidate chunks and returns refined top_k list."""
        pass


class CrossScoreReranker(BaseReranker):
    """
    Lightweight, fast, cross-feature scoring reranker.
    Computes fine-grained lexical and contextual signals:
    1. Exact query terms coverage
    2. Exact multi-word phrase matching bonus
    3. Section title alignment bonus
    4. Base retrieval score combination
    """

    def __init__(self, phrase_bonus: float = 0.25, title_bonus: float = 0.20):
        self.phrase_bonus = phrase_bonus
        self.title_bonus = title_bonus

    def _compute_score(self, query: str, item: RetrievedChunk) -> float:
        text = item.chunk.clean_text.lower()
        sec_title = (item.chunk.section_title or "").lower()
        doc_title = item.chunk.title.lower()
        q_lower = query.lower().strip()

        # 1. Base score (vector or hybrid score)
        base = item.score

        # 2. Term coverage score
        terms = [t for t in re.findall(r"[a-zA-Z0-9_\-]+", q_lower) if len(t) > 2]
        if not terms:
            return base

        matched_terms = sum(1 for t in terms if t in text or t in sec_title or t in doc_title)
        coverage_ratio = matched_terms / len(terms)

        # 3. Exact phrase match bonus
        has_phrase = 1.0 if q_lower in text or q_lower in sec_title else 0.0

        # 4. Section/Title alignment
        title_match = 1.0 if any(t in sec_title or t in doc_title for t in terms) else 0.0

        # Final rerank composite score
        rerank_score = (
            (0.40 * base)
            + (0.35 * coverage_ratio)
            + (self.phrase_bonus * has_phrase)
            + (self.title_bonus * title_match)
        )
        return round(rerank_score, 4)

    def rerank(self, query: str, candidates: List[RetrievedChunk], top_k: int = 3) -> List[RetrievedChunk]:
        if not candidates:
            return []

        scored_items = []
        for item in candidates:
            r_score = self._compute_score(query, item)
            # Clone item with new rerank_score
            new_item = RetrievedChunk(
                chunk=item.chunk,
                score=r_score,
                vector_score=item.vector_score,
                bm25_score=item.bm25_score,
                rerank_score=r_score,
                rank=0,
            )
            scored_items.append(new_item)

        # Sort descending by rerank_score
        scored_items.sort(key=lambda x: x.rerank_score or 0.0, reverse=True)

        # Re-assign ranks
        final_list = []
        for r, item in enumerate(scored_items[:top_k], start=1):
            item.rank = r
            final_list.append(item)

        return final_list


def get_reranker(reranker_type: str = "cross_score") -> BaseReranker:
    """Factory method for reranker instances."""
    rt = reranker_type.lower()
    if rt in ["cross_score", "default", "fast"]:
        return CrossScoreReranker()
    else:
        raise ValueError(f"Unknown reranker type: {reranker_type}")
