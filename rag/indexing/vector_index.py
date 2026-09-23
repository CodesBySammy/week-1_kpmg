"""
Vector Index implementation supporting cosine similarity, L2 distance,
metadata filtering, and serialization.
"""
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
import json
import numpy as np

from rag.schemas import Chunk, RetrievedChunk
from rag.embeddings.base import BaseEmbeddingProvider


class VectorIndex:
    """
    In-memory vector index with NumPy acceleration.
    Stores chunks, embeddings, and supports filtered k-NN search.
    """

    def __init__(self, embedding_provider: BaseEmbeddingProvider):
        self.embedding_provider = embedding_provider
        self.chunks: List[Chunk] = []
        self._id_to_index: Dict[str, int] = {}
        self._matrix: Optional[np.ndarray] = None  # shape: (N, D)

    def __len__(self) -> int:
        return len(self.chunks)

    def add_chunks(self, chunks: List[Chunk]):
        """Embeds and indexes a list of Chunk objects."""
        if not chunks:
            return

        texts_to_embed = []
        new_chunks = []

        for ch in chunks:
            if ch.chunk_id in self._id_to_index:
                continue  # Skip duplicates
            new_chunks.append(ch)
            # Embed section header + clean text for optimal retrieval relevance
            embed_input = f"{ch.title} {ch.section_title or ''}: {ch.clean_text}".strip()
            texts_to_embed.append(embed_input)

        if not new_chunks:
            return

        embeddings = self.embedding_provider.embed_batch(texts_to_embed)
        new_matrix = np.array(embeddings, dtype=np.float32)

        start_idx = len(self.chunks)
        for i, (ch, emb) in enumerate(zip(new_chunks, embeddings)):
            ch.embedding = emb
            self.chunks.append(ch)
            self._id_to_index[ch.chunk_id] = start_idx + i

        if self._matrix is None:
            self._matrix = new_matrix
        else:
            self._matrix = np.vstack([self._matrix, new_matrix])

    def _matches_filters(self, chunk: Chunk, filters: Optional[Dict[str, Any]]) -> bool:
        if not filters:
            return True
        for key, expected_val in filters.items():
            # Check top-level chunk attributes or metadata dict
            actual_val = getattr(chunk, key, None)
            if actual_val is None:
                actual_val = chunk.metadata.get(key)
            if actual_val is None:
                return False

            if isinstance(expected_val, list):
                if actual_val not in expected_val:
                    return False
            elif str(actual_val).lower() != str(expected_val).lower():
                return False
        return True

    def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        min_score: float = 0.0,
    ) -> List[RetrievedChunk]:
        """
        Cosine similarity search over normalized embeddings.
        Returns top_k matching chunks with similarity scores.
        """
        if self._matrix is None or len(self.chunks) == 0:
            return []

        query_emb = np.array(self.embedding_provider.embed_text(query), dtype=np.float32)
        # Cosine similarity for unit vectors is simply dot product
        similarities = np.dot(self._matrix, query_emb)

        # Sort indices in descending order
        sorted_indices = np.argsort(-similarities)

        results: List[RetrievedChunk] = []
        rank = 1

        for idx in sorted_indices:
            score = float(similarities[idx])
            if score < min_score:
                continue

            chunk = self.chunks[idx]
            if not self._matches_filters(chunk, filters):
                continue

            results.append(
                RetrievedChunk(
                    chunk=chunk,
                    score=score,
                    vector_score=score,
                    bm25_score=None,
                    rerank_score=None,
                    rank=rank,
                )
            )
            rank += 1
            if len(results) >= top_k:
                break

        return results

    def save(self, directory: Union[str, Path]):
        """Persists chunks and embedding matrix to disk."""
        target_dir = Path(directory)
        target_dir.mkdir(parents=True, exist_ok=True)

        chunks_data = [ch.model_dump(exclude={"embedding"}) for ch in self.chunks]
        with open(target_dir / "vector_chunks.json", "w", encoding="utf-8") as f:
            json.dump(chunks_data, f, indent=2)

        if self._matrix is not None:
            np.save(target_dir / "vector_matrix.npy", self._matrix)

    def load(self, directory: Union[str, Path]):
        """Loads chunks and embedding matrix from disk."""
        target_dir = Path(directory)
        chunks_file = target_dir / "vector_chunks.json"
        matrix_file = target_dir / "vector_matrix.npy"

        if chunks_file.exists():
            with open(chunks_file, "r", encoding="utf-8") as f:
                raw_list = json.load(f)
            self.chunks = [Chunk(**d) for d in raw_list]
            self._id_to_index = {ch.chunk_id: i for i, ch in enumerate(self.chunks)}

        if matrix_file.exists():
            self._matrix = np.load(matrix_file)
