"""
Input Safety and Prompt-Injection Guardrail Protections.
Treats all user inputs and retrieved documents as UNTRUSTED DATA,
enforces strict instruction/data delimiters, and detects injection attacks.
"""
from typing import Tuple, List, Optional
import re
from pydantic import BaseModel, Field
from fastapi import HTTPException, status


class GuardrailViolation(HTTPException):
    def __init__(self, reason: str, pattern_matched: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "GUARDRAIL_VIOLATION",
                "reason": reason,
                "pattern": pattern_matched,
            },
        )


class SanitizedInput(BaseModel):
    original_text: str
    cleaned_text: str
    is_safe: bool
    warnings: List[str] = Field(default_factory=list)


class InputGuardrail:
    """
    Enforces perimeter safety checks against malicious inputs,
    prompt injection attacks, and command bypass attempts.
    """

    MAX_INPUT_LENGTH = 4000

    # Common injection and jailbreak signatures
    INJECTION_PATTERNS = [
        r"ignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions",
        r"disregard\s+(?:all\s+)?(?:previous|prior|above)\s+instructions",
        r"you\s+are\s+now\s+(?:unconstrained|in\s+dan\s+mode|freed)",
        r"bypass\s+(?:all\s+)?(?:security|approval|checks|guardrails)",
        r"system\s*:\s*override",
        r"print\s+(?:all\s+)?system\s+prompts",
        r"reveal\s+(?:your\s+)?hidden\s+instructions",
        r"execute\s+(?:without|bypassing)\s+approval",
    ]

    @classmethod
    def check_prompt_injection(cls, text: str) -> Tuple[bool, Optional[str]]:
        """Scans input text for known injection and instruction override attempts."""
        lowered = text.lower()
        for pat in cls.INJECTION_PATTERNS:
            if re.search(pat, lowered):
                return True, pat
        return False, None

    @classmethod
    def sanitize(cls, raw_text: str, strict: bool = True) -> SanitizedInput:
        """
        Validates input length, removes control characters, and blocks prompt injection.
        """
        if not raw_text:
            return SanitizedInput(original_text="", cleaned_text="", is_safe=True)

        # 1. Enforce length limits
        if len(raw_text) > cls.MAX_INPUT_LENGTH:
            raise GuardrailViolation(
                reason=f"Input length {len(raw_text)} exceeds maximum allowed limit of {cls.MAX_INPUT_LENGTH} characters."
            )

        # 2. Check for prompt injection
        has_injection, matched_pat = cls.check_prompt_injection(raw_text)
        if has_injection and strict:
            raise GuardrailViolation(
                reason="Potential prompt injection or instruction override attempt detected.",
                pattern_matched=matched_pat,
            )

        # 3. Strip non-printable control characters
        cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", raw_text).strip()

        warnings = []
        if has_injection and not strict:
            warnings.append(f"Suspicious pattern detected: {matched_pat}")

        return SanitizedInput(
            original_text=raw_text,
            cleaned_text=cleaned,
            is_safe=not has_injection,
            warnings=warnings,
        )

    @classmethod
    def wrap_data_boundary(cls, text: str, data_type: str = "user_input") -> str:
        """
        Wraps content inside XML-style structural data boundaries
        to ensure the LLM treats it strictly as passive data rather than instructions.
        """
        sanitized = cls.sanitize(text, strict=False).cleaned_text
        return f"<{data_type}>\n{sanitized}\n</{data_type}>"
