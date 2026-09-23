"""
Chunking strategies for RAG documents.
Provides FixedSizeChunker, RecursiveCharacterChunker, and MarkdownSectionChunker.
"""
from abc import ABC, abstractmethod
import re
from typing import List, Optional, Dict, Any

from rag.schemas import Document, Chunk
from rag.ingestion.preprocessor import DocumentPreprocessor


class BaseChunker(ABC):
    """Abstract base class for document chunkers."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be strictly less than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @abstractmethod
    def split_document(self, document: Document) -> List[Chunk]:
        """Split a document into a sequence of Chunk objects."""
        pass


class FixedSizeChunker(BaseChunker):
    """
    Splits text strictly by fixed character length with a specified character overlap.
    """

    def split_document(self, document: Document) -> List[Chunk]:
        text = document.raw_content
        if not text.strip():
            return []

        chunks: List[Chunk] = []
        step = self.chunk_size - self.chunk_overlap
        start = 0
        chunk_idx = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk_text = text[start:end].strip()

            if chunk_text:
                token_count = DocumentPreprocessor.estimate_token_count(chunk_text)
                chunk_id = f"{document.document_id}_c{chunk_idx:03d}"
                meta = {
                    "document_id": document.document_id,
                    "title": document.metadata.title,
                    "category": document.metadata.category,
                    "policy_type": document.metadata.policy_type,
                    "department": document.metadata.department,
                    "effective_date": document.metadata.effective_date,
                    "chunking_strategy": "fixed_size",
                }
                chunks.append(
                    Chunk(
                        chunk_id=chunk_id,
                        document_id=document.document_id,
                        title=document.metadata.title,
                        section_title=None,
                        section_level=None,
                        text=chunk_text,
                        clean_text=chunk_text,
                        chunk_index=chunk_idx,
                        char_count=len(chunk_text),
                        token_count=token_count,
                        metadata=meta,
                    )
                )
                chunk_idx += 1

            start += step
            if start >= len(text):
                break

        return chunks


class RecursiveCharacterChunker(BaseChunker):
    """
    Recursively splits text by natural boundaries (paragraphs, newlines, sentences, words)
    ensuring each chunk fits within chunk_size while maintaining semantic coherence.
    """

    SEPARATORS = ["\n\n", "\n", ". ", "? ", "! ", " ", ""]

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        final_chunks: List[str] = []
        if not separators:
            return [text]

        sep = separators[0]
        remaining_seps = separators[1:]

        if sep == "":
            splits = list(text)
        else:
            splits = text.split(sep)

        current_piece = ""
        for s in splits:
            item = s if sep in ["\n\n", "\n", ""] else s + (sep if not s.endswith(sep) else "")
            candidate = current_piece + item if current_piece else item

            if len(candidate) <= self.chunk_size:
                current_piece = candidate
            else:
                if current_piece:
                    final_chunks.append(current_piece.strip())
                    current_piece = ""

                if len(item) > self.chunk_size and remaining_seps:
                    sub_chunks = self._split_text(item, remaining_seps)
                    final_chunks.extend(sub_chunks)
                else:
                    current_piece = item

        if current_piece.strip():
            final_chunks.append(current_piece.strip())

        return [c for c in final_chunks if c]

    def split_document(self, document: Document) -> List[Chunk]:
        text = document.raw_content
        if not text.strip():
            return []

        raw_chunks = self._split_text(text, self.SEPARATORS)
        chunks: List[Chunk] = []

        for idx, piece in enumerate(raw_chunks):
            chunk_id = f"{document.document_id}_rec_{idx:03d}"
            token_count = DocumentPreprocessor.estimate_token_count(piece)
            meta = {
                "document_id": document.document_id,
                "title": document.metadata.title,
                "category": document.metadata.category,
                "policy_type": document.metadata.policy_type,
                "department": document.metadata.department,
                "effective_date": document.metadata.effective_date,
                "chunking_strategy": "recursive",
            }
            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    document_id=document.document_id,
                    title=document.metadata.title,
                    section_title=None,
                    section_level=None,
                    text=piece,
                    clean_text=piece,
                    chunk_index=idx,
                    char_count=len(piece),
                    token_count=token_count,
                    metadata=meta,
                )
            )

        return chunks


class MarkdownSectionChunker(BaseChunker):
    """
    Splits markdown documents along header boundaries (# H1, ## H2, ### H3).
    Preserves document structure, section headers, hierarchy, and ensures large sections
    are subdivided if they exceed chunk_size.
    """

    HEADER_REGEX = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

    def split_document(self, document: Document) -> List[Chunk]:
        text = document.raw_content
        if not text.strip():
            return []

        lines = text.split("\n")
        sections: List[Dict[str, Any]] = []

        current_header = document.metadata.title
        current_level = 1
        current_lines: List[str] = []

        for line in lines:
            match = re.match(r"^(#{1,6})\s+(.+)$", line.strip())
            if match:
                # Flush existing accumulated section
                if current_lines:
                    sec_text = "\n".join(current_lines).strip()
                    if sec_text:
                        sections.append({
                            "header": current_header,
                            "level": current_level,
                            "text": sec_text
                        })
                    current_lines = []
                current_level = len(match.group(1))
                current_header = match.group(2).strip()
            else:
                current_lines.append(line)

        # Flush final section
        if current_lines:
            sec_text = "\n".join(current_lines).strip()
            if sec_text:
                sections.append({
                    "header": current_header,
                    "level": current_level,
                    "text": sec_text
                })

        # Now convert sections to chunks, subdividing large sections if needed
        chunks: List[Chunk] = []
        chunk_idx = 0

        for sec in sections:
            header_name = sec["header"]
            level = sec["level"]
            body = sec["text"]

            # If section is small enough, keep as single chunk
            if len(body) <= self.chunk_size:
                full_text = f"## {header_name}\n{body}" if not body.startswith(f"## {header_name}") else body
                chunk_id = f"{document.document_id}_s{chunk_idx:03d}"
                token_count = DocumentPreprocessor.estimate_token_count(full_text)
                meta = {
                    "document_id": document.document_id,
                    "title": document.metadata.title,
                    "section_title": header_name,
                    "section_level": level,
                    "category": document.metadata.category,
                    "policy_type": document.metadata.policy_type,
                    "department": document.metadata.department,
                    "effective_date": document.metadata.effective_date,
                    "chunking_strategy": "markdown_section",
                }
                chunks.append(
                    Chunk(
                        chunk_id=chunk_id,
                        document_id=document.document_id,
                        title=document.metadata.title,
                        section_title=header_name,
                        section_level=level,
                        text=full_text,
                        clean_text=full_text,
                        chunk_index=chunk_idx,
                        char_count=len(full_text),
                        token_count=token_count,
                        metadata=meta,
                    )
                )
                chunk_idx += 1
            else:
                # Subdivide using recursive character chunker
                sub_chunker = RecursiveCharacterChunker(
                    chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
                )
                # Create a pseudo document for this section
                pseudo_doc = Document(
                    document_id=document.document_id,
                    metadata=document.metadata,
                    raw_content=body,
                )
                sub_chunks = sub_chunker.split_document(pseudo_doc)
                for sc in sub_chunks:
                    annotated_text = f"## {header_name}\n{sc.text}"
                    chunk_id = f"{document.document_id}_s{chunk_idx:03d}"
                    token_count = DocumentPreprocessor.estimate_token_count(annotated_text)
                    meta = {
                        "document_id": document.document_id,
                        "title": document.metadata.title,
                        "section_title": header_name,
                        "section_level": level,
                        "category": document.metadata.category,
                        "policy_type": document.metadata.policy_type,
                        "department": document.metadata.department,
                        "effective_date": document.metadata.effective_date,
                        "chunking_strategy": "markdown_section_subdivided",
                    }
                    chunks.append(
                        Chunk(
                            chunk_id=chunk_id,
                            document_id=document.document_id,
                            title=document.metadata.title,
                            section_title=header_name,
                            section_level=level,
                            text=annotated_text,
                            clean_text=annotated_text,
                            chunk_index=chunk_idx,
                            char_count=len(annotated_text),
                            token_count=token_count,
                            metadata=meta,
                        )
                    )
                    chunk_idx += 1

        return chunks


def get_chunker(strategy: str = "markdown_section", chunk_size: int = 500, chunk_overlap: int = 100) -> BaseChunker:
    """Factory method for chunkers."""
    strat = strategy.lower()
    if strat in ["markdown", "markdown_section", "section"]:
        return MarkdownSectionChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    elif strat in ["recursive", "recursive_character"]:
        return RecursiveCharacterChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    elif strat in ["fixed", "fixed_size"]:
        return FixedSizeChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    else:
        raise ValueError(f"Unknown chunking strategy: {strategy}")
