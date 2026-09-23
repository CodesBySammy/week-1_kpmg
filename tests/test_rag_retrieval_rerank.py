"""
Tests for Retriever and Reranker components.
"""
import pytest
from rag.schemas import Chunk, RetrievedChunk, RetrievalQuery
from rag.embeddings.providers import DenseHashEmbeddingProvider
from rag.indexing.hybrid_index import HybridIndex
from rag.retrieval.reranker import CrossScoreReranker
from rag.retrieval.retriever import Retriever


@pytest.fixture
def retriever_setup():
    c1 = Chunk(
        chunk_id="CHK-1",
        document_id="EXP-1",
        title="Expense Policy",
        section_title="Meal Allowances",
        text="Daily meal allowance during business trips is capped at $75 per day.",
        clean_text="Daily meal allowance during business trips is capped at $75 per day.",
        chunk_index=0,
        char_count=69,
        token_count=15,
        metadata={"category": "Finance"},
    )
    c2 = Chunk(
        chunk_id="CHK-2",
        document_id="EXP-2",
        title="Expense Policy",
        section_title="Hotel Lodging",
        text="Standard hotel rates must not exceed $200 per night for domestic travel.",
        clean_text="Standard hotel rates must not exceed $200 per night for domestic travel.",
        chunk_index=1,
        char_count=73,
        token_count=16,
        metadata={"category": "Finance"},
    )
    provider = DenseHashEmbeddingProvider(dimension=128)
    idx = HybridIndex(embedding_provider=provider)
    idx.add_chunks([c1, c2])
    reranker = CrossScoreReranker()
    retriever = Retriever(index=idx, reranker=reranker)
    return retriever


def test_cross_score_reranker():
    reranker = CrossScoreReranker()
    ch1 = Chunk(
        chunk_id="A1",
        document_id="D1",
        title="Doc",
        section_title="Section",
        text="Irrelevant text about animals and plants.",
        clean_text="Irrelevant text about animals and plants.",
        chunk_index=0,
        char_count=40,
        token_count=8,
    )
    ch2 = Chunk(
        chunk_id="A2",
        document_id="D2",
        title="Doc",
        section_title="Section",
        text="Special corporate credit card reimbursement rules and receipts.",
        clean_text="Special corporate credit card reimbursement rules and receipts.",
        chunk_index=0,
        char_count=65,
        token_count=10,
    )
    candidates = [
        RetrievedChunk(chunk=ch1, score=0.6, rank=1),
        RetrievedChunk(chunk=ch2, score=0.5, rank=2),
    ]

    reranked = reranker.rerank(query="corporate credit card receipts", candidates=candidates, top_k=2)
    assert len(reranked) == 2
    # ch2 has much higher keyword and term match, so should be promoted to rank 1
    assert reranked[0].chunk.chunk_id == "A2"
    assert reranked[0].rank == 1


def test_retriever_multi_modes(retriever_setup):
    retriever = retriever_setup

    # Vector mode
    q_vec = RetrievalQuery(query="meal allowance cap", retrieval_mode="vector", top_k=1)
    res_vec = retriever.retrieve(q_vec)
    assert len(res_vec.results) == 1
    assert res_vec.results[0].chunk.chunk_id == "CHK-1"

    # BM25 mode
    q_bm = RetrievalQuery(query="hotel rates domestic", retrieval_mode="bm25", top_k=1)
    res_bm = retriever.retrieve(q_bm)
    assert len(res_bm.results) == 1
    assert res_bm.results[0].chunk.chunk_id == "CHK-2"

    # Hybrid with reranker
    q_hyb = RetrievalQuery(query="daily meal trip cap", retrieval_mode="hybrid", top_k=1, use_reranker=True)
    res_hyb = retriever.retrieve(q_hyb)
    assert len(res_hyb.results) == 1
    assert res_hyb.results[0].chunk.chunk_id == "CHK-1"
    assert res_hyb.results[0].rerank_score is not None
