# Grounded Generation & Citation Verification

## 1. Grounding Invariants
1. **Strict Context Adherence:** The generator is constrained to answer strictly from the provided source passages.
2. **Citation Attribution:** Every factual assertion must be attributed to an explicit document tag `[DOC-ID, Section X]`.
3. **Citation Cross-Validation:** The engine verifies that every citation in the generated text corresponds to an actual chunk in the retrieved context.
4. **Deterministic Refusal:** When retrieved evidence does not contain the answer, the system outputs a formal refusal:
   *"I am unable to answer this question based on the provided policy documents."*
