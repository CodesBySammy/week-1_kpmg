"""
BM25 Keyword Index implementation using rank_bm25.
"""
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import json
import re
import math
from rank_bm25 import BM25Plus, BM25Okapi

from rag.schemas import Chunk, RetrievedChunk


class BM25Index:
    """
    BM25 Keyword Index using Lucene/Elasticsearch non-negative smoothed IDF formula.
    Provides fast token-based exact match, handles acronyms, codes, and numerical clauses.
    """

    STOPWORDS = {
        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
        "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
        "to", "was", "were", "will", "with", "or", "if", "this", "all",
    }

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.chunks: List[Chunk] = []
        self._corpus_tokens: List[List[str]] = []
        self._doc_lens: List[int] = []
        self._avg_doc_len: float = 0.0
        self._idf: Dict[str, float] = {}

    def __len__(self) -> int:
        return len(self.chunks)

    def _tokenize(self, text: str) -> List[str]:
        tokens = re.findall(r"[a-zA-Z0-9_\-]+", text.lower())
        return [t for t in tokens if t not in self.STOPWORDS and len(t) > 1]

    def add_chunks(self, chunks: List[Chunk]):
        """Indexes a list of Chunk objects."""
        if not chunks:
            return

        for ch in chunks:
            self.chunks.append(ch)
            indexable_text = f"{ch.document_id} {ch.title} {ch.section_title or ''} {ch.clean_text}"
            tokens = self._tokenize(indexable_text)
            self._corpus_tokens.append(tokens)

        # Build Lucene BM25 model
        corpus_size = len(self._corpus_tokens)
        self._doc_lens = [len(doc) for doc in self._corpus_tokens]
        self._avg_doc_len = sum(self._doc_lens) / max(corpus_size, 1)

        doc_freqs: Dict[str, int] = {}
        for doc in self._corpus_tokens:
            for term in set(doc):
                doc_freqs[term] = doc_freqs.get(term, 0) + 1

        self._idf = {}
        for term, freq in doc_freqs.items():
            self._idf[term] = math.log(1.0 + (corpus_size - freq + 0.5) / (freq + 0.5))

    def _matches_filters(self, chunk: Chunk, filters: Optional[Dict[str, Any]]) -> bool:
        if not filters:
            return True
        for key, expected_val in filters.items():
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
        Runs BM25 scoring across indexed chunks.
        Normalizes raw BM25 scores to [0, 1] using max scaling for combination with vector scores.
        """
        if not self._corpus_tokens or len(self.chunks) == 0:
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        raw_scores: List[float] = []
        for i, doc in enumerate(self._corpus_tokens):
            sc = 0.0
            doc_len = self._doc_lens[i]
            len_norm = 1.0 - self.b + self.b * (doc_len / max(self._avg_doc_len, 1e-6))
            
            # Count terms in doc
            counts: Dict[str, int] = {}
            for t in doc:
                counts[t] = counts.get(t, 0) + 1

            for q in query_tokens:
                if q in counts:
                    freq = counts[q]
                    idf_val = self._idf.get(q, 0.0)
                    tf_norm = (freq * (self.k1 + 1.0)) / (freq + self.k1 * len_norm)
                    sc += idf_val * tf_norm

            raw_scores.append(sc)

        max_score = float(max(raw_scores)) if raw_scores else 0.0
        if max_score <= 0.0:
            return []

        # Sort indices descending
        sorted_indices = sorted(range(len(raw_scores)), key=lambda i: raw_scores[i], reverse=True)

        results: List[RetrievedChunk] = []
        rank = 1

        for idx in sorted_indices:
            raw_sc = raw_scores[idx]
            if raw_sc <= 0.0:
                continue

            norm_score = raw_sc / max_score
            if norm_score < min_score:
                continue

            chunk = self.chunks[idx]
            if not self._matches_filters(chunk, filters):
                continue

            results.append(
                RetrievedChunk(
                    chunk=chunk,
                    score=norm_score,
                    vector_score=None,
                    bm25_score=norm_score,
                    rerank_score=None,
                    rank=rank,
                )
            )
            rank += 1
            if len(results) >= top_k:
                break

        return results

    def save(self, directory: Union[str, Path]):
        """Persists chunks to disk."""
        target_dir = Path(directory)
        target_dir.mkdir(parents=True, exist_ok=True)
        chunks_data = [ch.model_dump(exclude={"embedding"}) for ch in self.chunks]
        with open(target_dir / "bm25_chunks.json", "w", encoding="utf-8") as f:
            json.dump(chunks_data, f, indent=2)

    def load(self, directory: Union[str, Path]):
        """Loads chunks and rebuilds BM25 index."""
        target_dir = Path(directory)
        chunks_file = target_dir / "bm25_chunks.json"
        if chunks_file.exists():
            with open(chunks_file, "r", encoding="utf-8") as f:
                raw_list = json.load(f)
            chunks = [Chunk(**d) for d in raw_list]
            self.chunks = []
            self._corpus_tokens = []
            self.add_chunks(chunks)
