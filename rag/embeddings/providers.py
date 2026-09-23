"""
Embedding provider implementations:
1. DenseHashEmbeddingProvider (deterministic, zero-dependency, n-gram hashed dense vector)
2. MockEmbeddingProvider (for unit tests with predictable vectors)
3. SentenceTransformerEmbeddingProvider (uses sentence-transformers if installed)
"""
import hashlib
import math
from typing import List, Optional
import numpy as np

from rag.embeddings.base import BaseEmbeddingProvider


class DenseHashEmbeddingProvider(BaseEmbeddingProvider):
    """
    Deterministic dense embedding provider using token and character n-gram hashing.
    Outputs L2-normalized float vectors of dimension d (default 384).
    Zero external API requirement, fast, offline, and consistent across platforms.
    """

    def __init__(self, dimension: int = 384):
        self._dim = dimension

    @property
    def dimension(self) -> int:
        return self._dim

    def _hash_token(self, token: str, seed: int = 0) -> int:
        data = f"{seed}:{token}".encode("utf-8")
        h = hashlib.md5(data).hexdigest()
        return int(h, 16) % self._dim

    STOPWORDS = {
        "a", "an", "the", "and", "or", "but", "if", "because", "as", "what",
        "which", "this", "that", "these", "those", "then", "just", "so", "than",
        "such", "both", "through", "about", "for", "is", "of", "while", "during",
        "to", "from", "in", "out", "on", "off", "again", "further", "then", "once",
        "here", "there", "when", "where", "why", "how", "all", "any", "both", "each",
        "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only",
        "own", "same", "so", "than", "too", "very", "can", "will", "just", "don",
        "should", "now", "are", "was", "were", "be", "been", "being", "have", "has", "had"
    }

    def embed_text(self, text: str) -> List[float]:
        vec = np.zeros(self._dim, dtype=np.float32)
        if not text.strip():
            vec[0] = 1.0
            return vec.tolist()

        words = text.lower().split()
        total_tokens = len(words)

        for i, word in enumerate(words):
            clean_word = "".join(ch for ch in word if ch.isalnum() or ch in "_-")
            if not clean_word:
                continue

            is_stop = clean_word in self.STOPWORDS
            weight = 0.1 if is_stop else (1.0 + min(len(clean_word) / 10.0, 1.5))

            # Unigram hash
            idx1 = self._hash_token(clean_word, seed=42)
            vec[idx1] += weight

            # Bigram hash (skip pure stopword pairs)
            if i < total_tokens - 1:
                next_word = "".join(ch for ch in words[i+1] if ch.isalnum() or ch in "_-")
                if next_word:
                    next_is_stop = next_word in self.STOPWORDS
                    if not (is_stop and next_is_stop):
                        bigram = f"{clean_word}_{next_word}"
                        idx2 = self._hash_token(bigram, seed=101)
                        vec[idx2] += 1.2

            # Character tri-grams for subword matching (skip for stopwords)
            if len(clean_word) >= 3 and not is_stop:
                for k in range(len(clean_word) - 2):
                    trigram = clean_word[k:k+3]
                    idx3 = self._hash_token(trigram, seed=203)
                    vec[idx3] += 0.35

        # L2 Normalization
        norm = np.linalg.norm(vec)
        if norm > 1e-8:
            vec = vec / norm
        else:
            vec[0] = 1.0

        return vec.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]


class MockEmbeddingProvider(BaseEmbeddingProvider):
    """
    Mock embedding provider for unit testing.
    Allows injecting fixed vectors or generating controlled dimensional vectors.
    """

    def __init__(self, dimension: int = 384, fixed_vector: Optional[List[float]] = None):
        self._dim = dimension
        self.fixed_vector = fixed_vector

    @property
    def dimension(self) -> int:
        return self._dim

    def embed_text(self, text: str) -> List[float]:
        if self.fixed_vector is not None:
            return list(self.fixed_vector)
        # Deterministic generation from text length & ascii
        val = sum(ord(c) for c in text[:20]) % 100 / 100.0
        vec = [val] * self._dim
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]


class SentenceTransformerEmbeddingProvider(BaseEmbeddingProvider):
    """
    Wrapper for HuggingFace sentence-transformers models (e.g., all-MiniLM-L6-v2).
    Falls back gracefully to DenseHashEmbeddingProvider if library is not installed.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        self._dim = 384
        self._fallback = None

    def _load_model(self):
        if self._model is None and self._fallback is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
                self._dim = self._model.get_sentence_embedding_dimension()
            except Exception:
                # Fallback to DenseHash
                self._fallback = DenseHashEmbeddingProvider(dimension=384)
                self._dim = 384

    @property
    def dimension(self) -> int:
        self._load_model()
        return self._dim

    def embed_text(self, text: str) -> List[float]:
        self._load_model()
        if self._model:
            emb = self._model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
            return emb.tolist()
        return self._fallback.embed_text(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        self._load_model()
        if self._model:
            embs = self._model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
            return embs.tolist()
        return self._fallback.embed_batch(texts)


def get_embedding_provider(provider_type: str = "dense_hash", dimension: int = 384) -> BaseEmbeddingProvider:
    """Factory function for embedding providers."""
    pt = provider_type.lower()
    if pt in ["dense_hash", "dense", "hash"]:
        return DenseHashEmbeddingProvider(dimension=dimension)
    elif pt in ["mock"]:
        return MockEmbeddingProvider(dimension=dimension)
    elif pt in ["sentence_transformers", "hf", "huggingface"]:
        return SentenceTransformerEmbeddingProvider()
    else:
        raise ValueError(f"Unknown embedding provider: {provider_type}")
