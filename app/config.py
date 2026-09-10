"""
Configuration Module

WHY THIS EXISTS:
    Configuration should NEVER be hardcoded in application code.
    This module reads settings from environment variables (loaded from a .env file
    in development). This separation means:
      - Different environments (dev, staging, production) use different configs
      - Secrets never appear in source code or version control
      - Configuration changes don't require code changes

HOW IT WORKS:
    Pydantic Settings reads values from environment variables automatically.
    If a .env file exists, python-dotenv loads it first. Each field in the
    Settings class maps to an environment variable (case-insensitive).

CURRICULUM CONNECTION:
    Week 1 requires: configuration, environment variables, no hardcoded secrets.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Each attribute maps to an environment variable.
    Example: APP_NAME env var -> app_name attribute.
    """

    # ── Application ──────────────────────────────────────────────
    app_name: str = "case-management-backend"
    app_version: str = "1.0.0"
    app_env: str = "development"
    app_debug: bool = True
    app_host: str = "127.0.0.1"
    app_port: int = 8000

    # ── Database ─────────────────────────────────────────────────
    database_url: str = "sqlite:///./case_management.db"

    # ── Logging ──────────────────────────────────────────────────
    log_level: str = "DEBUG"
    log_format: str = "json"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache()
def get_settings() -> Settings:
    """
    Return a cached Settings instance.

    WHY CACHED:
        Settings are read from disk/environment. We only need to do this once.
        lru_cache ensures the same Settings object is reused everywhere,
        avoiding repeated file I/O.
    """
    return Settings()
