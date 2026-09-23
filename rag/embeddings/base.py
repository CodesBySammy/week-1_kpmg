"""
Base abstract interface for embedding providers.
"""
from abc import ABC, abstractmethod
from typing import List


class BaseEmbeddingProvider(ABC):
    """Abstract base class for all embedding generators."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the dimension of generated embedding vectors."""
        pass

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generate a normalized embedding vector for a single text."""
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate normalized embedding vectors for a batch of texts."""
        pass
