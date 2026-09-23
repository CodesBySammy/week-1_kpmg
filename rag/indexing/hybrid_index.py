"""
Hybrid Index combining VectorIndex and BM25Index.
Implements Weighted Score Fusion and Reciprocal Rank Fusion (RRF).
"""
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

from rag.schemas import Chunk, RetrievedChunk
from rag.indexing.vector_index import VectorIndex
from rag.indexing.bm25_index import BM25Index
from rag.embeddings.base import BaseEmbeddingProvider


class HybridIndex:
    """
    Coordinates simultaneous dense vector search and sparse BM25 search.
    Merges candidates using either Weighted Score Fusion or Reciprocal Rank Fusion (RRF).
    """

    def __init__(self, embedding_provider: BaseEmbeddingProvider):
        self.vector_index = VectorIndex(embedding_provider=embedding_provider)
        self.bm25_index = BM25Index()

    def __len__(self) -> int:
        return len(self.vector_index)

    def add_chunks(self, chunks: List[Chunk]):
        """Adds chunks to both vector and BM25 indices."""
        self.vector_index.add_chunks(chunks)
        self.bm25_index.add_chunks(chunks)

    def search_vector_only(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        min_score: float = 0.0,
    ) -> List[RetrievedChunk]:
        """Vector-only search."""
        return self.vector_index.search(query=query, top_k=top_k, filters=filters, min_score=min_score)

    def search_bm25_only(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        min_score: float = 0.0,
    ) -> List[RetrievedChunk]:
        """BM25 keyword-only search."""
        return self.bm25_index.search(query=query, top_k=top_k, filters=filters, min_score=min_score)

    def search_hybrid(
        self,
        query: str,
        top_k: int = 5,
        alpha: float = 0.6,
        fusion_method: str = "weighted",  # "weighted" or "rrf"
        rrf_k: int = 60,
        filters: Optional[Dict[str, Any]] = None,
        min_score: float = 0.0,
    ) -> List[RetrievedChunk]:
        """
        Executes hybrid search combining dense semantic and sparse lexical signals.
        """
        # Retrieve candidate pools from both indices (larger pool for fusion)
        candidate_k = max(top_k * 3, 20)
        vector_candidates = self.vector_index.search(
            query=query, top_k=candidate_k, filters=filters, min_score=0.0
        )
        bm25_candidates = self.bm25_index.search(
            query=query, top_k=candidate_k, filters=filters, min_score=0.0
        )

        chunk_map: Dict[str, Chunk] = {}
        vec_scores: Dict[str, float] = {}
        bm25_scores: Dict[str, float] = {}
        vec_ranks: Dict[str, int] = {}
        bm25_ranks: Dict[str, int] = {}

        for item in vector_candidates:
            cid = item.chunk.chunk_id
            chunk_map[cid] = item.chunk
            vec_scores[cid] = item.score
            vec_ranks[cid] = item.rank

        for item in bm25_candidates:
            cid = item.chunk.chunk_id
            chunk_map[cid] = item.chunk
            bm25_scores[cid] = item.score
            bm25_ranks[cid] = item.rank

        fused_scores: Dict[str, float] = {}

        if fusion_method == "rrf":
            # Reciprocal Rank Fusion: sum(1 / (k + rank))
            for cid in chunk_map.keys():
                rrf_score = 0.0
                if cid in vec_ranks:
                    rrf_score += 1.0 / (rrf_k + vec_ranks[cid])
                if cid in bm25_ranks:
                    rrf_score += 1.0 / (rrf_k + bm25_ranks[cid])
                fused_scores[cid] = rrf_score
        else:
            # Weighted Score Fusion: alpha * vector + (1 - alpha) * bm25
            for cid in chunk_map.keys():
                v_sc = vec_scores.get(cid, 0.0)
                b_sc = bm25_scores.get(cid, 0.0)
                fused_scores[cid] = (alpha * v_sc) + ((1.0 - alpha) * b_sc)

        # Sort descending by fused score
        sorted_cids = sorted(fused_scores.keys(), key=lambda cid: fused_scores[cid], reverse=True)

        results: List[RetrievedChunk] = []
        rank = 1

        for cid in sorted_cids:
            score = fused_scores[cid]
            if score < min_score:
                continue

            results.append(
                RetrievedChunk(
                    chunk=chunk_map[cid],
                    score=round(score, 4),
                    vector_score=round(vec_scores.get(cid, 0.0), 4) if cid in vec_scores else None,
                    bm25_score=round(bm25_scores.get(cid, 0.0), 4) if cid in bm25_scores else None,
                    rerank_score=None,
                    rank=rank,
                )
            )
            rank += 1
            if len(results) >= top_k:
                break

        return results

    def save(self, directory: Union[str, Path]):
        """Persists both indices to directory."""
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        self.vector_index.save(dir_path)
        self.bm25_index.save(dir_path)

    def load(self, directory: Union[str, Path]):
        """Loads both indices from directory."""
        dir_path = Path(directory)
        self.vector_index.load(dir_path)
        self.bm25_index.load(dir_path)
