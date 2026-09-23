"""
Tests for chunking strategies: FixedSizeChunker, RecursiveCharacterChunker, MarkdownSectionChunker.
"""
import pytest
from rag.schemas import Document, DocumentMetadata
from rag.chunking.strategies import (
    FixedSizeChunker,
    RecursiveCharacterChunker,
    MarkdownSectionChunker,
    get_chunker,
)


@pytest.fixture
def sample_document():
    meta = DocumentMetadata(
        document_id="TEST-CHUNKS-001",
        title="Test Chunking Document",
        category="Policy Test",
        department="Quality Assurance",
        effective_date="2025-01-01",
    )
    content = """# Test Chunking Document

## 1. Introduction
This is the introductory section explaining the general guidelines and rules for testing.

## 2. Policy Requirements
All personnel must follow the specific rules listed below:
- Requirement 2.1: First requirement text with sufficient length.
- Requirement 2.2: Second requirement text with detailed rules and conditions.
- Requirement 2.3: Third requirement text with escalation pathways and penalties.

## 3. Exceptions and Contact
For exceptions or questions, reach out to the administrative contact team.
"""
    return Document(
        document_id="TEST-CHUNKS-001",
        metadata=meta,
        raw_content=content,
    )


def test_fixed_size_chunker(sample_document):
    chunker = FixedSizeChunker(chunk_size=150, chunk_overlap=30)
    chunks = chunker.split_document(sample_document)
    assert len(chunks) > 1
    for ch in chunks:
        assert ch.document_id == "TEST-CHUNKS-001"
        assert ch.char_count <= 150
        assert ch.metadata["chunking_strategy"] == "fixed_size"


def test_recursive_character_chunker(sample_document):
    chunker = RecursiveCharacterChunker(chunk_size=200, chunk_overlap=50)
    chunks = chunker.split_document(sample_document)
    assert len(chunks) >= 2
    for ch in chunks:
        assert ch.document_id == "TEST-CHUNKS-001"
        assert ch.metadata["category"] == "Policy Test"


def test_markdown_section_chunker(sample_document):
    chunker = MarkdownSectionChunker(chunk_size=500, chunk_overlap=100)
    chunks = chunker.split_document(sample_document)
    assert len(chunks) >= 3
    section_titles = [c.section_title for c in chunks]
    assert any("Introduction" in (st or "") for st in section_titles)
    assert any("Policy Requirements" in (st or "") for st in section_titles)
    assert any("Exceptions and Contact" in (st or "") for st in section_titles)
    assert chunks[0].metadata["department"] == "Quality Assurance"


def test_chunker_factory():
    c1 = get_chunker("markdown")
    assert isinstance(c1, MarkdownSectionChunker)
    c2 = get_chunker("recursive")
    assert isinstance(c2, RecursiveCharacterChunker)
    c3 = get_chunker("fixed")
    assert isinstance(c3, FixedSizeChunker)
    with pytest.raises(ValueError):
        get_chunker("unknown_strategy")
