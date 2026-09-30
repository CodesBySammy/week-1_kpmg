# Demo Troubleshooting & Emergency Recovery

- **Issue**: Port 8000 already in use.
  - *Fix*: `kill -9 $(lsof -t -i:8000)` or change port to 8001.
- **Issue**: JWT token expired during demo.
  - *Fix*: Run `python scripts/mint_demo_tokens.py` to regenerate 24-hour demo tokens.
- **Issue**: RAG index empty.
  - *Fix*: Run `python -m rag.ingestion.pipeline` to reload knowledge docs.
