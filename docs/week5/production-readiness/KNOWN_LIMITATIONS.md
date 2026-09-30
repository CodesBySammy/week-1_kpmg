# Enterprise Platform Known Limitations Register

In accordance with Section 26 of the Week 5 curriculum, this register explicitly documents technical debt, architectural assumptions, and boundary limitations:

1. **Local Hash Embedding Provider**:
   - *Limitation*: The default embedding provider in the test suite uses a deterministic dense hash embedding (`DenseHashEmbeddingProvider`) rather than an external vector model API (like OpenAI `text-embedding-3-small`).
   - *Production Impact*: Semantic similarity matches syntactic density; production deployments should enable remote OpenAI/HuggingFace embeddings via `EMBEDDING_PROVIDER=openai` in `.env`.

2. **SQLite vs PostgreSQL Concurrency**:
   - *Limitation*: Local development and testing utilizes SQLite with WAL mode enabled.
   - *Production Impact*: While suitable for moderate concurrency, production multi-pod Kubernetes deployments require PostgreSQL (`DATABASE_URL=postgresql://user:pass@host/db`).

3. **Approval Token Expiration**:
   - *Limitation*: Cryptographic HMAC approval tokens have a fixed 30-minute time-to-live (TTL).
   - *Production Impact*: If a supervisor does not approve a high-priority escalation within 30 minutes, a new approval request must be submitted.

4. **In-Memory Workflow State**:
   - *Limitation*: Intermediate multi-step agentic state transitions are held in memory during the execution lifecycle.
   - *Production Impact*: Node failover during an in-flight request will return a gateway error, requiring client retry.
