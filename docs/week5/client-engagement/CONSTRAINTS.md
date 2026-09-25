# Engineering Constraints & Boundaries

1. **Language & Runtime**: Python 3.14 with strict type annotations (	yping, Pydantic v2).
2. **Framework**: FastAPI (REST) and SQLAlchemy (ORM).
3. **Data Boundary**: SQLite database for local portability, transactional consistency, and self-contained execution.
4. **Deterministic Embedding**: Offline SHA-256 projection vector index for reproducible, dependency-free testing.
5. **No Breaking Changes**: Existing APIs, schemas, and test suites from Weeks 1–4 must continue to function without regression.
6. **No Phantom Tools**: All tools must have complete deterministic implementations, input/output schemas, and test coverage.
