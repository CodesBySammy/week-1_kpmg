# Secrets Management & Configuration Separation

## 1. Twelve-Factor Configuration
All configurable parameters are separated from code and loaded via environment variables or `.env` files using Pydantic `BaseSettings`:
- `JWT_SECRET`: Secret key for HMAC token signing.
- `WORKFLOW_TIMEOUT_MS`: Millisecond timeout for orchestrator tasks.
- `ENVIRONMENT`: Runtime environment (`development`, `staging`, `production`).

## 2. Sensitive Data Handling
- Secrets are NEVER logged in application logs.
- Sensitive credentials, API keys, and internal connection strings are filtered through log masking helpers.
