"""
Unified Retriever engine for semantic, lexical, and hybrid search with reranking.
"""
import time
from typing import List, Optional, Dict, Any

from rag.schemas import RetrievalQuery, RetrievalResult, RetrievedChunk
from rag.indexing.hybrid_index import HybridIndex
from rag.retrieval.reranker import BaseReranker, CrossScoreReranker


class Retriever:
    """
    Orchestrates candidate retrieval across dense vector and sparse keyword indices,
    applies metadata filtering, and triggers reranking pipelines.
    """

    def __init__(self, index: HybridIndex, reranker: Optional[BaseReranker] = None):
        self.index = index
        self.reranker = reranker or CrossScoreReranker()

    def retrieve(self, query_obj: RetrievalQuery) -> RetrievalResult:
        start_time = time.perf_counter()
        mode = query_obj.retrieval_mode.lower()
        top_k = query_obj.top_k
        filters = query_obj.filters
        min_score = query_obj.min_score or 0.0

        # Retrieve candidates based on requested mode
        if mode == "vector":
            candidates = self.index.search_vector_only(
                query=query_obj.query,
                top_k=top_k * 2 if query_obj.use_reranker else top_k,
                filters=filters,
                min_score=min_score,
            )
        elif mode == "bm25":
            candidates = self.index.search_bm25_only(
                query=query_obj.query,
                top_k=top_k * 2 if query_obj.use_reranker else top_k,
                filters=filters,
                min_score=min_score,
            )
        elif mode == "hybrid":
            candidates = self.index.search_hybrid(
                query=query_obj.query,
                top_k=top_k * 2 if query_obj.use_reranker else top_k,
                alpha=0.6,
                fusion_method="weighted",
                filters=filters,
                min_score=min_score,
            )
        else:
            raise ValueError(f"Unsupported retrieval mode: {mode}")

        total_found = len(candidates)

        # Optional reranking step
        if query_obj.use_reranker and candidates:
            rerank_k = min(query_obj.rerank_top_k or top_k, top_k)
            final_results = self.reranker.rerank(
                query=query_obj.query,
                candidates=candidates,
                top_k=rerank_k,
            )
        else:
            final_results = candidates[:top_k]

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return RetrievalResult(
            query=query_obj.query,
            retrieval_mode=mode,
            total_candidates_found=total_found,
            results=final_results,
            execution_time_ms=round(elapsed_ms, 2),
            filters_applied=filters,
        )
