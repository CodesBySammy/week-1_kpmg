"""
Tests for RAG document parsing, metadata extraction, and preprocessing.
"""
import pytest
from pathlib import Path
from rag.ingestion.parser import MarkdownDocumentParser, DocumentParser
from rag.ingestion.preprocessor import DocumentPreprocessor


def test_preprocessor_normalize_whitespace():
    raw = "Hello   world!\r\n\r\n\n\nThis is   a test.\t\tGood."
    cleaned = DocumentPreprocessor.normalize_whitespace(raw)
    assert "Hello world!" in cleaned
    assert "\r" not in cleaned
    assert "\n\n\n" not in cleaned
    assert "This is a test." in cleaned


def test_preprocessor_clean_control_characters():
    raw = "Test\x00\x07string\x1bwith\x0bcontrol chars"
    cleaned = DocumentPreprocessor.clean_text(raw)
    assert "\x00" not in cleaned
    assert "\x07" not in cleaned
    assert "Teststringwithcontrolchars" in cleaned.replace(" ", "")


def test_preprocessor_estimate_token_count():
    text = "The quick brown fox jumps over the lazy dog."
    tokens = DocumentPreprocessor.estimate_token_count(text)
    assert tokens > 0
    assert 5 <= tokens <= 20
    assert DocumentPreprocessor.estimate_token_count("") == 0


def test_markdown_parser_with_frontmatter():
    md_content = """---
document_id: TEST-001
title: Test Policy Document
category: Engineering
policy_type: Technical
version: "1.0"
department: Core Engineering
effective_date: "2025-01-01"
status: Active
---

# Test Policy Document

## 1. Scope
This is the scope section.
"""
    doc = MarkdownDocumentParser.parse_text(md_content, default_id="FALLBACK")
    assert doc.document_id == "TEST-001"
    assert doc.metadata.title == "Test Policy Document"
    assert doc.metadata.category == "Engineering"
    assert doc.metadata.policy_type == "Technical"
    assert doc.metadata.version == "1.0"
    assert doc.metadata.department == "Core Engineering"
    assert "1. Scope" in doc.raw_content


def test_markdown_parser_without_frontmatter():
    md_content = """# Untitled Policy Guide

Here is some policy text without YAML header.
"""
    doc = MarkdownDocumentParser.parse_text(md_content, default_id="DOC-999")
    assert doc.document_id == "DOC-999"
    assert doc.metadata.title == "Untitled Policy Guide"
    assert doc.metadata.category == "General"


def test_document_parser_load_policies_dir():
    docs = DocumentParser.load_directory("data/policies")
    assert len(docs) >= 6
    doc_ids = {d.document_id for d in docs}
    assert "HR-POLICY-001" in doc_ids
    assert "LEAVE-POLICY-002" in doc_ids
    assert "EXPENSE-POLICY-003" in doc_ids
    assert "TRAVEL-POLICY-004" in doc_ids
    assert "IT-SECURITY-005" in doc_ids
    assert "COMPLIANCE-POLICY-006" in doc_ids
