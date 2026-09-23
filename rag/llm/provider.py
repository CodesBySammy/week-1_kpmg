"""
LLM provider interfaces and implementations.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import os
import re


class BaseLLMProvider(ABC):
    """Abstract base class for LLM generation."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.0) -> str:
        """Generate response given user prompt and optional system prompt."""
        pass


class MockLLMProvider(BaseLLMProvider):
    """
    Deterministic LLM emulator for testing, labs, and evaluation.
    Synthesizes grounded answers strictly from the provided context blocks.
    Emits formal refusals when the context is insufficient or ungrounded.
    """

    def __init__(self, model_name: str = "mock-gpt-4o"):
        self.model_name = model_name

    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.0) -> str:
        # Extract context block and question from standard RAG prompt format
        context_match = re.search(r"CONTEXT:\s*(.*?)\s*QUESTION:", prompt, re.DOTALL | re.IGNORECASE)
        question_match = re.search(r"QUESTION:\s*(.*?)(?:\n\n|\Z)", prompt, re.DOTALL | re.IGNORECASE)

        context_text = context_match.group(1).strip() if context_match else prompt
        question_text = question_match.group(1).strip() if question_match else prompt

        if not context_text or context_text.strip() == "":
            return "I am unable to find any relevant information in the official policy documentation to answer your question."

        q_terms = [t.lower() for t in re.findall(r"[a-zA-Z0-9_\-]+", question_text) if len(t) > 2]
        # Ignore common filler question words and prepositions
        filler = {
            "what", "when", "where", "which", "who", "whom", "whose", "why", "how",
            "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
            "do", "does", "did", "can", "could", "should", "would", "may", "might", "must",
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "with", "from", "by", "about", "into", "through", "during", "before", "after",
            "above", "below", "under", "between"
        }
        meaningful_terms = [t for t in q_terms if t not in filler and len(t) > 2]

        # Check if any meaningful term appears in context
        has_overlap = any(term in context_text.lower() for term in meaningful_terms)

        if not has_overlap and len(meaningful_terms) > 0:
            return "I am unable to answer this question because the provided policy documents do not contain information regarding this topic."

        # Extract source headers present in context, e.g. [Source 1: IT-SECURITY-005 — ... | Section: ...]
        sources = re.findall(r"\[(Source \d+: ([^—\]]+)[^\]]*)\]", context_text)

        # Find best matching paragraph in context
        paragraphs = [p.strip() for p in context_text.split("\n\n") if p.strip()]
        matched_sentences = []

        for p in paragraphs:
            # Skip pure headers
            if p.startswith("[Source") and len(p.split("\n")) == 1:
                continue
            for line in p.split("\n"):
                clean_l = line.strip().lstrip("-*# ")
                if not clean_l:
                    continue
                match_count = sum(1 for term in meaningful_terms if term in clean_l.lower())
                if match_count > 0:
                    matched_sentences.append((match_count, clean_l))

        # Sort sentences by keyword relevance
        matched_sentences.sort(key=lambda x: x[0], reverse=True)

        if not matched_sentences:
            return "Based on the provided policy documents, there are no specific provisions that address your inquiry."

        top_sentences = [s[1] for s in matched_sentences[:3]]
        body_answer = " ".join(top_sentences)

        # Format citation tag from sources
        if sources:
            primary_src = sources[0][0]
            primary_doc = sources[0][1].strip()
            answer = f"According to official policy [{primary_doc}], {body_answer} (Reference: [{primary_src}])."
        else:
            answer = f"Based on company policy documentation: {body_answer}"

        return answer


class OpenAILLMProvider(BaseLLMProvider):
    """
    OpenAI-compatible LLM provider with API key detection and fallback.
    """

    def __init__(self, model_name: str = "gpt-4o-mini", api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self._fallback = MockLLMProvider()

    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.0) -> str:
        if not self.api_key:
            return self._fallback.generate(prompt=prompt, system_prompt=system_prompt, temperature=temperature)

        try:
            import requests
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature,
            }
            resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            else:
                return self._fallback.generate(prompt=prompt, system_prompt=system_prompt, temperature=temperature)
        except Exception:
            return self._fallback.generate(prompt=prompt, system_prompt=system_prompt, temperature=temperature)


def get_llm_provider(provider_type: str = "mock", model_name: Optional[str] = None) -> BaseLLMProvider:
    """Factory method for LLM providers."""
    pt = provider_type.lower()
    if pt in ["mock", "test", "emulator"]:
        return MockLLMProvider(model_name=model_name or "mock-gpt-4o")
    elif pt in ["openai", "gpt"]:
        return OpenAILLMProvider(model_name=model_name or "gpt-4o-mini")
    else:
        raise ValueError(f"Unknown LLM provider: {provider_type}")
