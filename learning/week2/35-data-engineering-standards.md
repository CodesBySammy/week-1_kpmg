# Enterprise Data Engineering Standards: 12-Factor Data Apps and Clean Code

Enterprise data pipelines are not throwaway scripts—they are critical production software systems. Applying modern software engineering rigor guarantees longevity, maintainability, and security.

---

## 1. The 12-Factor Methodology for Data Pipelines

Adapted from Heroku's 12-Factor App methodology for data engineering:

1. **One Codebase, Multiple Deploys**: A single Git repository tracked with version control, deployed across local dev, staging CI, and cloud production.
2. **Explicit Dependencies**: Fully declared in `pyproject.toml` with pinned semantic versions.
3. **Config in the Environment**: Store database credentials, API endpoints, and storage paths in environment variables (`.env` or OS environment via `pydantic-settings`), never hardcoded in code.
4. **Treat Backing Services as Attached Resources**: Databases, REST APIs, and object storage buckets are accessed via configurable connection strings.
5. **Strict Separation of Build, Release, and Run**: Build multi-stage Docker images once, tag them with Git SHAs, and promote them across environments without rebuilding.
6. **Stateless Processes**: The pipeline process executes as a stateless batch job. State (watermarks, data) is persisted strictly in external storage (database, Parquet, JSON files).
7. **Concurrency via Horizontal Scaling**: Partition datasets and distribute processing across worker threads or Spark nodes.
8. **Fast Startup & Graceful Shutdown**: Handle `SIGTERM` and `SIGINT` cleanly, flushing open file buffers and committing manifest records.
9. **Dev/Prod Parity**: Run the same Docker container locally that runs in production.
10. **Logs as Event Streams**: Emit structured JSON logs to `stdout` rather than writing unformatted text to static local log files.

---

## 2. Configuration Management in Our Pipeline

In `pipeline/config.py`, all settings derive from `pydantic_settings.BaseSettings`:

```python
from pathlib import Path
from pydantic_settings import BaseSettings

class PipelineSettings(BaseSettings):
    app_env: str = "development"
    base_dir: Path = Path(__file__).resolve().parent.parent
    data_dir: Path = base_dir / "data"
    input_dir: Path = data_dir / "input"
    raw_dir: Path = data_dir / "raw"
    standardized_dir: Path = data_dir / "standardized"
    curated_dir: Path = data_dir / "curated"
    rejected_dir: Path = data_dir / "rejected"
    database_url: str = "sqlite:///data/cases.db"
    mock_api_url: str = "http://127.0.0.1:8000/api/v1/mock/policies"
    run_mode: str = "full"

    class Config:
        env_file = ".env"
        extra = "allow"
```

This design allows overriding any parameter dynamically via environment variables (e.g. `DATABASE_URL=postgresql://...`).
