# Architecture Decision Records (ADRs)

This document records the critical architectural choices, alternatives evaluated, rationale, and engineering trade-offs made during the development of the Case Management Backend.

---

## ADR-001: Selection of SQLite over PostgreSQL for Primary Week 1 Delivery

### Status: ACCEPTED

### Context
Week 1 curriculum allows choosing between PostgreSQL and SQLite. The service requires normalized schema design, foreign keys, multi-table joins, CTEs, window functions, and ACID transactions. The target user is a fresher needing zero-friction local setup and reproducible testing.

### Decision
Implement **SQLite** as the primary relational database engine for the Week 1 implementation.

### Alternatives Considered
- **PostgreSQL via Local Install**: Requires installing PostgreSQL service, creating users, granting roles, and configuring network listener on port 5432. High friction on Windows developer machines; prone to setup failure.
- **PostgreSQL via Docker**: Requires Docker Desktop, WSL2 on Windows, and container lifecycle management. Introduces significant overhead unrelated to Python/SQL core concepts.

### Rationale
- SQLite is built into Python's standard library (`sqlite3`), requiring zero external daemons or container runtimes.
- SQLite fully supports all required SQL concepts: ANSI SQL joins, CTEs, Window Functions (`ROW_NUMBER`, `RANK`, `LAG`), and ACID transactions.
- By using SQLAlchemy ORM, the data access layer remains database-agnostic. Upgrading to PostgreSQL in a later phase requires changing only the `DATABASE_URL` connection string in `.env`.

### Trade-offs & Consequences
- **Positive**: Instant setup; completely hermetic, sub-second test execution; zero setup friction for freshers.
- **Negative**: SQLite does not support high-concurrency multi-process writes (file lock limit). Not suitable for high-throughput multi-node production deployments without migrating to PostgreSQL.

---

## ADR-002: Adoption of the Repository Pattern for Data Access

### Status: ACCEPTED

### Context
In fast prototypes, developers often place SQLAlchemy queries directly inside FastAPI route functions. We needed an architectural pattern that supports unit testing without running a database and prevents tight coupling between HTTP routes and SQL queries.

### Decision
Enforce a dedicated **Repository Layer** (`app/repositories/case_repository.py`) between the Service layer and the database.

### Alternatives Considered
- **Active Record Pattern**: Placing query and save methods directly on ORM models (`case.save()`). Rebuffed because it couples business models directly to active database sessions.
- **Inline Queries in Route Controllers**: Writing `db.query(Case).filter(...)` directly inside FastAPI routes. Rebuffed because it makes unit testing without an active database impossible and violates Single Responsibility Principle.

### Rationale
- The Repository pattern isolates all database query logic, transaction rollbacks, and ORM operations in one place.
- Allows unit tests (`tests/unit/test_case_service.py`) to mock the repository using `MagicMock` and test pure domain rules in milliseconds.
- Isolates audit trail logging (`case_history`) inside repository methods, ensuring history is recorded consistently regardless of which service calls the update.

### Trade-offs & Consequences
- **Positive**: Clean separation of concerns, testability with mocks, swappable persistence layer.
- **Negative**: Introduces additional classes and method delegation layers.

---

## ADR-003: Externalized Configuration via Pydantic Settings

### Status: ACCEPTED

### Context
Application configuration (database URLs, log levels, server ports) must not be hardcoded in source code or committed to Git (12-Factor App Factor III).

### Decision
Implement `app/config.py` using **Pydantic Settings** (`pydantic-settings`), backed by a committed `.env.example` template and an uncommitted `.env` file, cached via `@lru_cache()`.

### Alternatives Considered
- **Direct `os.getenv()` Calls**: Calling `os.getenv("DATABASE_URL")` throughout multiple files. Rejected because it lacks type validation and default values are scattered across 20 files.
- **Static Configuration Dictionaries / Python Config Files**: Defining settings in a `config.py` dictionary. Rejected because secrets could be accidentally committed and environment variable overrides are clumsy.

### Rationale
- Pydantic Settings automatically validates types at startup (e.g. ensuring `APP_PORT` is an integer).
- Supports `.env` loading for local development and system environment variables for production containers.
- Centralizes all system configuration in a single self-documenting class.

### Trade-offs & Consequences
- **Positive**: Zero secrets in Git; fail-fast startup on invalid config; full IDE autocomplete.
- **Negative**: Requires adding `pydantic-settings` to project dependencies.

---

## ADR-004: Standardized Universal JSON Error Contract

### Status: ACCEPTED

### Context
APIs that return varying error payloads (sometimes plain strings, sometimes lists, sometimes raw HTML stack traces) create extreme complexity for client and frontend developers.

### Decision
Enforce a single, immutable JSON error envelope across all 4xx and 5xx responses:
`{ "error": { "code": "...", "message": "...", "details": ... } }`.

### Alternatives Considered
- **FastAPI Default Error Format**: FastAPI natively returns `{"detail": "..."}` or `{"detail": [...]}`. Rejected because it lacks stable, machine-readable error codes and the payload shape varies between string and list.
- **Plain Text Responses**: Returning plain status text. Rejected because programmatic clients need structured details.

### Rationale
- Predictable contract: Clients write a single global error handler.
- Machine-readable codes: Allows client UIs to switch on `CASE_NOT_FOUND` rather than parsing fragile English strings.
- Security masking: Global handlers catch unexpected 500 exceptions and mask internal stack traces from clients while preserving full traces in server logs.

### Trade-offs & Consequences
- **Positive**: Enterprise-grade client developer experience; zero stack trace leakage.
- **Negative**: Requires writing custom global exception handlers in `app/exceptions/handlers.py`.

---

## ADR-005: Structured JSON Logging for Enterprise Observability

### Status: ACCEPTED

### Context
Traditional `print()` statements or plain text logs are difficult to parse, search, and alert on when ingested into cloud log aggregators.

### Decision
Implement **Structured JSON Logging** using `python-json-logger` emitting to `sys.stdout`.

### Alternatives Considered
- **Standard Library Plain Text Logging**: Using `logging.basicConfig(format="%(asctime)s - %(message)s")`. Rejected because extracting fields (like `case_id`) in log aggregators requires writing slow, fragile regular expressions.
- **Raw `print()` Statements**: Rejected because it lacks severity levels, timestamps, module origins, and structured metadata.

### Rationale
- Every log line is emitted as a single-line JSON object containing standard keys (`timestamp`, `level`, `logger`, `message`) plus contextual metadata passed via `extra={...}` (`case_id`, `operation`).
- Cloud log ingestion pipelines (CloudWatch, Datadog, Elasticsearch) parse JSON natively, enabling instant querying without custom regex grok patterns.

### Trade-offs & Consequences
- **Positive**: Machine-parseable logs, rapid incident troubleshooting, searchability.
- **Negative**: JSON log lines are slightly more verbose to read in local raw terminals without a log viewer tool.
