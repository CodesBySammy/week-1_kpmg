# Containerized Deployment & Sandbox Architecture

## 1. Dockerfile Configuration
The containerized deployment packages:
- Python 3.14 slim base image.
- Non-root application user for container security.
- FastAPI backend running on Uvicorn.
- Mounted persistent volumes for SQLite and vector index data.
- Standardized health check probes via `GET /health`.
