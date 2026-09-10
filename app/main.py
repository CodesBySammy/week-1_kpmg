"""
FastAPI Application Entry Point

WHY THIS IS main.py:
    This is the single point where the FastAPI application is assembled.
    It wires together:
      - Logging configuration
      - Database initialization
      - Exception handlers
      - API routes
      - OpenAPI metadata

    Think of it as the "startup script" that connects all the modular pieces.

HOW TO RUN:
    uvicorn app.main:app --reload

    This tells uvicorn to import the `app` variable from `app.main` module.

CURRICULUM CONNECTION:
    Week 1 requires: FastAPI service, OpenAPI specification, modular structure.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.cases import router
from app.config import get_settings
from app.database.session import create_tables
from app.exceptions.handlers import register_exception_handlers
from app.logging_config import setup_logging

# ── Initialize Logging First ─────────────────────────────────────
# Logging must be configured before anything else so all startup
# messages are properly formatted.
setup_logging()
logger = logging.getLogger(__name__)


# ── Lifespan: Startup & Shutdown ─────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.

    Code before `yield` runs at startup.
    Code after `yield` runs at shutdown.
    """
    settings = get_settings()
    logger.info(
        "Application starting",
        extra={
            "app_name": settings.app_name,
            "app_version": settings.app_version,
            "environment": settings.app_env,
        },
    )

    # Create database tables if they don't exist
    create_tables()
    logger.info("Database tables initialized")

    yield  # Application is running

    logger.info("Application shutting down")


# ── Create FastAPI App ───────────────────────────────────────────
settings = get_settings()

app = FastAPI(
    title="Case Management API",
    description=(
        "A modular, testable case management backend built with FastAPI "
        "and SQLite. Week 1 hands-on project for the FDE Fresher Readiness "
        "Program."
    ),
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",       # Swagger UI at /docs
    redoc_url="/redoc",     # ReDoc at /redoc
    openapi_url="/openapi.json",  # OpenAPI spec at /openapi.json
)

# ── Register Exception Handlers ─────────────────────────────────
register_exception_handlers(app)

# ── Include Routes ───────────────────────────────────────────────
app.include_router(router, prefix="/api/v1")


# ── Health Check ─────────────────────────────────────────────────
@app.get("/health", tags=["System"])
def health_check() -> dict:
    """
    Health check endpoint.

    Used to verify the application is running.
    Returns a simple JSON response.
    """
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
    }
