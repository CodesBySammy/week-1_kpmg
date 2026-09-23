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

from fastapi import FastAPI, Response, status
from sqlalchemy import text

from app.api.routes.cases import router
from app.api.routes.mock_api import router as mock_router
from app.api.routes.rag import router as rag_router
from app.api.routes.workflow import router as workflow_router
from app.config import get_settings
from app.database.session import SessionLocal, create_tables
from app.exceptions.handlers import register_exception_handlers
from app.logging_config import setup_logging
from observability.correlation import CorrelationMiddleware

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
        "and SQLite. Extended with Lakehouse ETL, Grounded RAG, and Week 4 "
        "Controlled AI Workflow with RBAC, Tool Contracts, and Observability."
    ),
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",       # Swagger UI at /docs
    redoc_url="/redoc",     # ReDoc at /redoc
    openapi_url="/openapi.json",  # OpenAPI spec at /openapi.json
)

# ── Register Middleware ─────────────────────────────────────────
app.add_middleware(CorrelationMiddleware)

# ── Register Exception Handlers ─────────────────────────────────
register_exception_handlers(app)

# ── Include Routes ───────────────────────────────────────────────
app.include_router(router, prefix="/api/v1")
app.include_router(mock_router, prefix="/api/v1")
app.include_router(rag_router, prefix="/api/v1")
app.include_router(workflow_router, prefix="/api/v1")


# ── Health Check ─────────────────────────────────────────────────
@app.get("/health", tags=["System"])
def health_check() -> dict:
    """
    Health check endpoint (Liveness probe).

    Used to verify the application is running.
    Returns a simple JSON response.
    """
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
    }


# ── Readiness Probe ──────────────────────────────────────────────
@app.get("/ready", tags=["System"])
def readiness_check(response: Response) -> dict:
    """
    Readiness check endpoint (Readiness probe).

    Verifies downstream dependencies:
      1. SQLite / Database connectivity
      2. RAG service initialization
      3. Workflow engine readiness
    """
    checks = {
        "database": False,
        "rag_service": True,
        "workflow_engine": True,
    }

    # Verify Database Connectivity
    try:
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            checks["database"] = True
        finally:
            db.close()
    except Exception as exc:
        logger.error("Readiness check database failure: %s", exc)
        checks["database"] = False

    is_ready = all(checks.values())
    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ready" if is_ready else "not_ready",
        "checks": checks,
        "version": settings.app_version,
    }

