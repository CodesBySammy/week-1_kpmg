"""
Tests for ContextAssembler, MockLLMProvider, and GroundedAnswerGenerator.
"""
import pytest
from rag.schemas import Chunk, RetrievedChunk
from rag.context.assembler import ContextAssembler
from rag.llm.provider import MockLLMProvider
from rag.generation.generator import GroundedAnswerGenerator


@pytest.fixture
def test_chunks():
    c1 = Chunk(
        chunk_id="C1",
        document_id="IT-SEC-01",
        title="IT Security Policy",
        section_title="MFA Requirements",
        text="Multi-Factor Authentication (MFA) is strictly mandatory for all SSO portals and VPN connections.",
        clean_text="Multi-Factor Authentication (MFA) is strictly mandatory for all SSO portals and VPN connections.",
        chunk_index=0,
        char_count=100,
        token_count=20,
    )
    c2 = Chunk(
        chunk_id="C2",
        document_id="IT-SEC-01",
        title="IT Security Policy",
        section_title="Lockout Policy",
        text="Account lockout occurs after 5 consecutive failed login attempts within 15 minutes.",
        clean_text="Account lockout occurs after 5 consecutive failed login attempts within 15 minutes.",
        chunk_index=1,
        char_count=85,
        token_count=18,
    )
    return [
        RetrievedChunk(chunk=c1, score=0.9, rank=1),
        RetrievedChunk(chunk=c2, score=0.85, rank=2),
    ]


def test_context_assembler(test_chunks):
    assembler = ContextAssembler(max_context_tokens=150)
    ctx = assembler.assemble(test_chunks)
    assert ctx.total_tokens > 0
    assert len(ctx.included_chunks) == 2
    assert "IT-SEC-01" in ctx.formatted_context
    assert "MFA Requirements" in ctx.formatted_context
    assert "IT-SEC-01" in ctx.citation_index


def test_context_assembler_budget_truncation(test_chunks):
    # Restrict to tiny token budget
    assembler = ContextAssembler(max_context_tokens=30)
    ctx = assembler.assemble(test_chunks)
    assert len(ctx.included_chunks) <= 2
    assert ctx.dropped_chunk_count >= 1 or ctx.total_tokens <= 35


def test_grounded_generator_accurate_answer(test_chunks):
    assembler = ContextAssembler()
    ctx = assembler.assemble(test_chunks)
    llm = MockLLMProvider()
    generator = GroundedAnswerGenerator(llm_provider=llm)

    answer, citations, is_grounded, is_refusal = generator.generate_answer(
        question="When does account lockout occur?",
        context=ctx,
    )
    assert not is_refusal
    assert is_grounded
    assert "5 consecutive failed" in answer or "lockout" in answer.lower()
    assert len(citations) >= 1
    assert citations[0].document_id == "IT-SEC-01"


def test_grounded_generator_out_of_domain_refusal(test_chunks):
    assembler = ContextAssembler()
    ctx = assembler.assemble(test_chunks)
    llm = MockLLMProvider()
    generator = GroundedAnswerGenerator(llm_provider=llm)

    answer, citations, is_grounded, is_refusal = generator.generate_answer(
        question="What is the recipe for chocolate chip cookies?",
        context=ctx,
    )
    assert is_refusal
    assert any(w in answer.lower() for w in ["unable", "cannot", "do not contain", "no relevant"])
