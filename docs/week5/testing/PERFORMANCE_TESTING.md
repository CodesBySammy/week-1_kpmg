# Performance Testing Methodology & Environment

## 1. Test Environment Specifications
- **Operating System**: Microsoft Windows 11 Pro
- **Platform**: Python 3.14.7 (win32)
- **Database**: SQLite in-memory / file-based WAL mode
- **Test Framework**: Pytest with high-resolution `time.perf_counter()` benchmarking fixtures
- **Concurrency Model**: Asyncio / AnyIO event loop with FastAPI TestClient

## 2. Benchmark Categories & Targets
1. **API Endpoints**: p95 latency < 50ms for standard read/list queries.
2. **RAG Pipeline**:
   - Chunking & Ingestion: < 10ms per document.
   - Hybrid Search & Reranking: < 15ms for 50-chunk index.
   - Context Assembly: < 5ms for 2000-token budget.
3. **Agentic Workflow Execution**: End-to-end intent-to-response < 100ms.
4. **Tool Execution**: < 20ms per database read/write tool operation.
