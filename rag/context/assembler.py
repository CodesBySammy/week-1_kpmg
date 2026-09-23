"""
Token-budget-aware context assembly for RAG pipelines.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from rag.schemas import RetrievedChunk, Citation
from rag.ingestion.preprocessor import DocumentPreprocessor


class AssembledContext(BaseModel):
    formatted_context: str
    total_tokens: int
    included_chunks: List[RetrievedChunk]
    dropped_chunk_count: int
    citation_index: Dict[str, Citation]


class ContextAssembler:
    """
    Assembles retrieved chunks into structured prompt context blocks,
    enforcing maximum token limits and formatting citations.
    """

    def __init__(self, max_context_tokens: int = 2000, include_metadata_header: bool = True):
        self.max_context_tokens = max_context_tokens
        self.include_metadata_header = include_metadata_header

    def assemble(self, retrieved_chunks: List[RetrievedChunk]) -> AssembledContext:
        if not retrieved_chunks:
            return AssembledContext(
                formatted_context="",
                total_tokens=0,
                included_chunks=[],
                dropped_chunk_count=0,
                citation_index={},
            )

        context_blocks: List[str] = []
        included_chunks: List[RetrievedChunk] = []
        dropped_count = 0
        current_token_count = 0
        citation_index: Dict[str, Citation] = {}

        # Track seen text hashes to prevent duplicates
        seen_texts = set()

        for idx, item in enumerate(retrieved_chunks, start=1):
            ch = item.chunk
            text_snippet = ch.clean_text.strip()

            # Pass-through deduplication of identical or near-identical text
            text_hash = hash(text_snippet[:100])
            if text_hash in seen_texts:
                continue
            seen_texts.add(text_hash)

            # Build block header with clear citation keys
            sec_info = f" | Section: {ch.section_title}" if ch.section_title else ""
            header = f"[Source {idx}: {ch.document_id} — {ch.title}{sec_info}]"
            block = f"{header}\n{text_snippet}\n"

            block_tokens = DocumentPreprocessor.estimate_token_count(block)

            if current_token_count + block_tokens > self.max_context_tokens:
                # If even the first block exceeds limit, truncate it; otherwise break
                if not context_blocks:
                    # Truncate first chunk to fit
                    truncated_text = text_snippet[: self.max_context_tokens * 3]
                    block = f"{header}\n{truncated_text}...\n"
                    context_blocks.append(block)
                    included_chunks.append(item)
                    current_token_count += DocumentPreprocessor.estimate_token_count(block)
                else:
                    dropped_count += 1
                    continue
            else:
                context_blocks.append(block)
                included_chunks.append(item)
                current_token_count += block_tokens

            # Create citation object
            citation = Citation(
                document_id=ch.document_id,
                title=ch.title,
                section_title=ch.section_title,
                chunk_id=ch.chunk_id,
                snippet=text_snippet[:200] + "..." if len(text_snippet) > 200 else text_snippet,
                relevance_score=item.score,
            )
            citation_index[ch.document_id] = citation
            citation_index[f"Source {idx}"] = citation

        full_context_str = "\n---\n".join(context_blocks)

        return AssembledContext(
            formatted_context=full_context_str,
            total_tokens=current_token_count,
            included_chunks=included_chunks,
            dropped_chunk_count=dropped_count,
            citation_index=citation_index,
        )
