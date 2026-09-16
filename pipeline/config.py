"""
Pipeline Configuration Module

Implements 12-Factor environment-based configuration for the Week 2 Data Pipeline.
Supports local development, automated tests, and Docker container execution.
"""

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class PipelineSettings(BaseSettings):
    """Configuration settings for the enterprise data pipeline."""
    
    # Environment & Naming
    app_env: str = "development"
    pipeline_name: str = "case-management-data-pipeline"
    version: str = "2.0.0"
    log_level: str = "INFO"
    
    # Paths (relative or absolute)
    base_dir: Path = Path(__file__).resolve().parent.parent
    data_dir: Path = base_dir / "data"
    input_dir: Path = data_dir / "input"
    raw_dir: Path = data_dir / "raw"
    standardized_dir: Path = data_dir / "standardized"
    curated_dir: Path = data_dir / "curated"
    rejected_dir: Path = data_dir / "rejected"
    
    reports_dir: Path = base_dir / "reports"
    profiling_dir: Path = reports_dir / "profiling"
    data_quality_dir: Path = reports_dir / "data_quality"
    reconciliation_dir: Path = reports_dir / "reconciliation"
    
    audit_dir: Path = base_dir / "audit"
    watermark_file: Path = audit_dir / "watermark.json"
    
    # Database URL (links directly to Week 1 SQLite OLTP storage)
    database_url: str = "sqlite:///./case_management.db"
    
    # Mock REST API Base URL
    mock_api_url: str = "http://127.0.0.1:8000/api/v1/mock/policies"
    mock_api_timeout_seconds: float = 5.0
    
    # Execution parameters
    run_mode: str = "full"  # "full" or "incremental"
    run_id: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def get_run_id(self) -> str:
        """Returns the configured run_id or generates an ISO-timestamped run ID."""
        if self.run_id:
            return self.run_id
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        return f"RUN_{timestamp}"

    def ensure_directories(self) -> None:
        """Ensures all required operational directories exist."""
        for path in [
            self.data_dir,
            self.input_dir,
            self.raw_dir,
            self.standardized_dir,
            self.curated_dir,
            self.rejected_dir,
            self.reports_dir,
            self.profiling_dir,
            self.data_quality_dir,
            self.reconciliation_dir,
            self.audit_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)


# Global singleton settings instance
settings = PipelineSettings()
