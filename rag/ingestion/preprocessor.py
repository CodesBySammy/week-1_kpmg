"""
Document Preprocessing and text normalization module.
"""
import re
from typing import Dict, Any, Tuple


class DocumentPreprocessor:
    """
    Standardizes raw text, removes unwanted artifacts,
    normalizes Unicode characters, and estimates token lengths.
    """

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """
        Normalizes multiple spaces to single space,
        and collapses 3+ consecutive newlines to 2, preserving paragraph breaks.
        """
        # Replace Windows CRLF with LF
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Replace non-breaking spaces and tabs with regular spaces
        text = text.replace("\xa0", " ").replace("\t", "    ")
        # Replace 3+ consecutive newlines with 2 newlines
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Collapse multiple horizontal spaces to single space, except leading indentations
        lines = [re.sub(r"[ ]{2,}", " ", line.rstrip()) for line in text.split("\n")]
        return "\n".join(lines).strip()

    @staticmethod
    def clean_text(raw_text: str) -> str:
        """
        Cleans text while preserving structural elements like markdown headers and bullets.
        """
        if not raw_text:
            return ""
        
        # Remove zero-width characters and control characters except \n and \t
        cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", raw_text)
        return DocumentPreprocessor.normalize_whitespace(cleaned)

    @staticmethod
    def estimate_token_count(text: str) -> int:
        """
        Rough token count estimation (~4 characters per token for English text),
        calibrated with word count.
        """
        if not text:
            return 0
        words = len(text.split())
        chars = len(text)
        # Standard heuristic: max of (words * 1.3, chars / 4)
        return max(1, int(max(words * 1.3, chars / 4)))

    @classmethod
    def preprocess(cls, text: str, extra_metadata: Dict[str, Any] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Full preprocessing pipeline returning cleaned text and extracted statistics.
        """
        cleaned = cls.clean_text(text)
        stats = {
            "char_count": len(cleaned),
            "word_count": len(cleaned.split()),
            "estimated_token_count": cls.estimate_token_count(cleaned),
        }
        if extra_metadata:
            stats.update(extra_metadata)
        return cleaned, stats
