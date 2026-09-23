"""
Tests for embedding providers and index structures (Vector, BM25, Hybrid).
"""
import pytest
import numpy as np
from rag.schemas import Chunk
from rag.embeddings.providers import DenseHashEmbeddingProvider, MockEmbeddingProvider
from rag.indexing.vector_index import VectorIndex
from rag.indexing.bm25_index import BM25Index
from rag.indexing.hybrid_index import HybridIndex


@pytest.fixture
def sample_chunks():
    c1 = Chunk(
        chunk_id="C001",
        document_id="DOC-1",
        title="Password Policy",
        section_title="Complexity",
        text="Passwords must be at least 14 characters long and contain numbers.",
        clean_text="Passwords must be at least 14 characters long and contain numbers.",
        chunk_index=0,
        char_count=67,
        token_count=15,
        metadata={"category": "IT & Security", "department": "Security"},
    )
    c2 = Chunk(
        chunk_id="C002",
        document_id="DOC-2",
        title="Travel Policy",
        section_title="Airfare",
        text="All commercial domestic flights must be booked in economy class at least 14 days in advance.",
        clean_text="All commercial domestic flights must be booked in economy class at least 14 days in advance.",
        chunk_index=0,
        char_count=93,
        token_count=20,
        metadata={"category": "Finance", "department": "Finance"},
    )
    c3 = Chunk(
        chunk_id="C003",
        document_id="DOC-3",
        title="Leave Policy",
        section_title="Annual Vacation",
        text="Employees receive 18 days of paid annual vacation each calendar year.",
        clean_text="Employees receive 18 days of paid annual vacation each calendar year.",
        chunk_index=0,
        char_count=71,
        token_count=16,
        metadata={"category": "Human Resources", "department": "HR"},
    )
    return [c1, c2, c3]


def test_dense_hash_embedding_provider():
    provider = DenseHashEmbeddingProvider(dimension=128)
    assert provider.dimension == 128
    vec = provider.embed_text("Password security requirements")
    assert len(vec) == 128
    norm = np.linalg.norm(vec)
    assert abs(norm - 1.0) < 1e-4

    # Empty text returns valid normalized vector
    vec_empty = provider.embed_text("")
    assert len(vec_empty) == 128


def test_vector_index(sample_chunks):
    provider = DenseHashEmbeddingProvider(dimension=128)
    index = VectorIndex(embedding_provider=provider)
    index.add_chunks(sample_chunks)
    assert len(index) == 3

    results = index.search("What are the password rules?", top_k=2)
    assert len(results) > 0
    assert results[0].chunk.document_id == "DOC-1"
    assert results[0].vector_score is not None

    # Test metadata filter
    filtered = index.search("rules", top_k=5, filters={"category": "Finance"})
    assert len(filtered) == 1
    assert filtered[0].chunk.document_id == "DOC-2"


def test_bm25_index(sample_chunks):
    index = BM25Index()
    index.add_chunks(sample_chunks)
    assert len(index) == 3

    results = index.search("economy class flights", top_k=2)
    assert len(results) > 0
    assert results[0].chunk.document_id == "DOC-2"
    assert results[0].bm25_score is not None

    # Filtered search
    filtered = index.search("vacation", top_k=5, filters={"department": "HR"})
    assert len(filtered) == 1
    assert filtered[0].chunk.document_id == "DOC-3"


def test_hybrid_index(sample_chunks):
    provider = DenseHashEmbeddingProvider(dimension=128)
    hybrid = HybridIndex(embedding_provider=provider)
    hybrid.add_chunks(sample_chunks)
    assert len(hybrid) == 3

    # Weighted search
    weighted_res = hybrid.search_hybrid("annual vacation leave days", top_k=2, fusion_method="weighted")
    assert len(weighted_res) > 0
    assert weighted_res[0].chunk.document_id == "DOC-3"

    # RRF search
    rrf_res = hybrid.search_hybrid("economy flight domestic", top_k=2, fusion_method="rrf")
    assert len(rrf_res) > 0
    assert rrf_res[0].chunk.document_id == "DOC-2"
