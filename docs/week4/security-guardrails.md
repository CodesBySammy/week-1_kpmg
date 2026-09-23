# Security Guardrails & Input Sanitization

## 1. Input Validation
Every raw prompt is inspected by `security.guardrails.InputGuardrail`:
- **Length Bounds:** Rejects prompts under 2 characters or over 4,000 characters.
- **Control Characters:** Strips null bytes, non-printable control characters, and dangerous terminal escapes.

## 2. Prompt Delimiters
User inputs and retrieved evidence are placed inside explicit XML/tag boundaries (`<user_input>`, `<retrieved_evidence>`) preventing the LLM from confusing untrusted text with system directives.
