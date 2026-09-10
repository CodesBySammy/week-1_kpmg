"""
Global Exception Handlers

WHY THIS EXISTS:
    FastAPI needs to know how to convert Python exceptions into HTTP responses.
    Without these handlers, an unhandled exception would return a generic 500
    with a stack trace — leaking internal implementation details to API consumers.

    These handlers ensure:
      1. Every error produces a consistent JSON error body
      2. Internal details (stack traces, file paths) are never exposed
      3. Errors are logged with context for debugging
      4. HTTP status codes match the error semantics

ERROR CONTRACT:
    All error responses follow this structure:
    {
        "error": {
            "code": "CASE_NOT_FOUND",
            "message": "Case with id 42 not found",
            "details": null
        }
    }

    See docs/api-specification.md for the full error contract.

CURRICULUM CONNECTION:
    Week 1 requires: consistent errors, error contracts, HTTP status codes,
    no exposed stack traces.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions import (
    AppError,
    CaseNotFoundError,
    DatabaseError,
    UserNotFoundError,
    ValidationError,
)

logger = logging.getLogger(__name__)


def _error_response(
    status_code: int, code: str, message: str, details: object = None
) -> JSONResponse:
    """Build a consistent error response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details,
            }
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI app."""

    @app.exception_handler(CaseNotFoundError)
    async def case_not_found_handler(
        request: Request, exc: CaseNotFoundError
    ) -> JSONResponse:
        logger.warning(
            "Case not found",
            extra={"case_id": exc.case_id, "path": str(request.url)},
        )
        return _error_response(404, "CASE_NOT_FOUND", exc.message)

    @app.exception_handler(UserNotFoundError)
    async def user_not_found_handler(
        request: Request, exc: UserNotFoundError
    ) -> JSONResponse:
        logger.warning(
            "User not found",
            extra={"user_id": exc.user_id, "path": str(request.url)},
        )
        return _error_response(404, "USER_NOT_FOUND", exc.message)

    @app.exception_handler(ValidationError)
    async def validation_error_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        logger.warning(
            "Validation error",
            extra={"detail": exc.message, "path": str(request.url)},
        )
        return _error_response(422, "VALIDATION_ERROR", exc.message)

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """
        Handle Pydantic/FastAPI request validation errors.

        FastAPI raises this when the request body/params don't match
        the Pydantic schema (wrong types, missing required fields, etc.)
        """
        # Extract user-friendly error details
        errors = []
        for err in exc.errors():
            field = " -> ".join(str(loc) for loc in err["loc"])
            errors.append({
                "field": field,
                "message": err["msg"],
                "type": err["type"],
            })

        logger.warning(
            "Request validation failed",
            extra={"errors": errors, "path": str(request.url)},
        )
        return _error_response(
            422, "REQUEST_VALIDATION_ERROR",
            "Request validation failed",
            details=errors,
        )

    @app.exception_handler(DatabaseError)
    async def database_error_handler(
        request: Request, exc: DatabaseError
    ) -> JSONResponse:
        logger.error(
            "Database error",
            extra={"detail": exc.message, "path": str(request.url)},
        )
        # Do NOT expose database details to the client
        return _error_response(
            500, "INTERNAL_ERROR", "An internal error occurred"
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        Catch-all for unexpected errors.

        This is the safety net. If we reach here, it means there's a bug
        we didn't anticipate. Log the full exception for debugging, but
        return a generic message to the client.
        """
        logger.exception(
            "Unhandled exception",
            extra={"path": str(request.url), "error_type": type(exc).__name__},
        )
        return _error_response(
            500, "INTERNAL_ERROR", "An unexpected error occurred"
        )
