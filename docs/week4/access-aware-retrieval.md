# Access-Aware Retrieval in RAG

## 1. Concept
Passive RAG systems retrieve documents based purely on cosine similarity, risking exposure of confidential HR, executive, or compliance policies to unauthorized users.

## 2. Implementation
1. **Policy Metadata:** Policies are tagged with `allowed_roles` in metadata (e.g. `['manager', 'admin']`).
2. **Pre-Filtering:** During retrieval, `AccessAwarePolicyFilter.filter_documents(...)` excludes documents the authenticated user's role cannot access.
3. **Citation Scrubbing:** Even if an authorized document is retrieved, citations are verified against the user principal before output rendering.
