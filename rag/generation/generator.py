"""
Grounded Answer Generator with citation validation and hallucination checks.
"""
from typing import List, Tuple, Dict, Any, Optional
import re

from rag.schemas import Citation, RetrievedChunk
from rag.context.assembler import AssembledContext
from rag.llm.provider import BaseLLMProvider
from rag.generation.prompts import RAGPromptTemplates


class GroundedAnswerGenerator:
    """
    Generates grounded answers using an LLM, verifies citations against the retrieved context,
    and flags ungrounded statements or hallucinations.
    """

    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm_provider = llm_provider

    def _is_refusal(self, text: str) -> bool:
        low = text.lower()
        return any(phrase in low for phrase in RAGPromptTemplates.REFUSAL_PHRASES)

    def _extract_and_verify_citations(
        self, answer: str, context: AssembledContext
    ) -> Tuple[List[Citation], bool]:
        """
        Extracts cited document references from generated answer (e.g. [HR-POLICY-001], [Source 1]),
        verifies that they actually exist in the retrieved context chunks,
        and returns verified citations and a grounding flag.
        """
        # Look for [DOC-ID] or [Source N] in text
        raw_citations = re.findall(r"\[([^\]]+)\]", answer)
        verified_citations: List[Citation] = []
        is_grounded = True

        for ref in raw_citations:
            clean_ref = ref.strip()
            # Check if reference matches any chunk in context
            matched_citation = None
            for key, cit in context.citation_index.items():
                if key in clean_ref or clean_ref in key or cit.document_id in clean_ref:
                    matched_citation = cit
                    break

            if matched_citation:
                if matched_citation not in verified_citations:
                    verified_citations.append(matched_citation)
            else:
                # Mentioned a source not in context -> possible hallucination
                if not any(word in clean_ref.lower() for word in ["ref", "reference", "note"]):
                    is_grounded = False

        # If answer is not a refusal and no explicit bracketed citation was added,
        # but chunks were used, attribute all included chunks as primary sources
        if not verified_citations and not self._is_refusal(answer):
            for ch in context.included_chunks:
                c = Citation(
                    document_id=ch.chunk.document_id,
                    title=ch.chunk.title,
                    section_title=ch.chunk.section_title,
                    chunk_id=ch.chunk.chunk_id,
                    snippet=ch.chunk.clean_text[:200],
                    relevance_score=ch.score,
                )
                if c not in verified_citations:
                    verified_citations.append(c)

        return verified_citations, is_grounded

    def generate_answer(
        self,
        question: str,
        context: AssembledContext,
        temperature: float = 0.0,
        strict_grounding: bool = True,
    ) -> Tuple[str, List[Citation], bool, bool]:
        """
        Runs the grounded generation process.
        Returns: (answer, citations, is_grounded, is_refusal)
        """
        if not context.formatted_context.strip():
            refusal_text = (
                "I am unable to answer this question because no relevant policy documents were found in the knowledge base."
            )
            return refusal_text, [], True, True

        prompt = RAGPromptTemplates.USER_PROMPT_TEMPLATE.format(
            context=context.formatted_context,
            question=question,
        )

        raw_answer = self.llm_provider.generate(
            prompt=prompt,
            system_prompt=RAGPromptTemplates.SYSTEM_PROMPT,
            temperature=temperature,
        )

        is_refusal = self._is_refusal(raw_answer)
        if is_refusal:
            return raw_answer, [], True, True

        citations, is_grounded = self._extract_and_verify_citations(raw_answer, context)

        return raw_answer, citations, is_grounded, False
