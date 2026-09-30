# Production Environment Configuration Reference

| Variable Name | Required | Default (Dev) | Production Recommendation | Description |
|---|---|---|---|---|
| `DATABASE_URL` | **Yes** | `sqlite:///./test.db` | `postgresql://...` | Connection URI for transactional database |
| `JWT_SECRET_KEY` | **Yes** | `dev-secret-key-12345` | High-entropy 64-char string | HMAC secret for signing access tokens |
| `APPROVAL_SECRET_KEY` | **Yes** | `dev-approval-key-67890` | High-entropy 64-char string | Secret for cryptographic approval tokens |
| `EMBEDDING_PROVIDER` | No | `dense_hash` | `openai` / `huggingface` | Embedding model provider for RAG |
| `LLM_PROVIDER` | No | `mock` | `openai` / `azure_openai` | Model provider for conversational RAG |
| `ENVIRONMENT` | No | `development` | `production` | Enables strict CORS and secure cookies |
| `LOG_LEVEL` | No | `INFO` | `INFO` / `WARN` | Structlog emission verbosity |
