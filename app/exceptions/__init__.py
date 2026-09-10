"""
Custom Exceptions

WHY THIS EXISTS:
    Instead of raising generic Python exceptions, we define application-specific
    exceptions that:
      1. Carry semantic meaning (CaseNotFoundError vs generic ValueError)
      2. Map cleanly to HTTP status codes
      3. Produce consistent API error responses
      4. Make error handling predictable for both developers and API consumers

ANTI-PATTERN (DO NOT DO THIS):
    except Exception:
        pass  # Silently swallows ALL errors — bugs become invisible

CORRECT PATTERN:
    except CaseNotFoundError as e:
        # Handle specifically, log it, return proper 404
        logger.warning("Case not found", extra={"case_id": e.case_id})
        raise HTTPException(status_code=404, detail=str(e))

CURRICULUM CONNECTION:
    Week 1 requires: exception handling, custom exceptions, consistent errors,
    no silent error swallowing.
"""


class AppError(Exception):
    """
    Base exception for all application errors.

    All custom exceptions inherit from this so you can catch any
    application error with `except AppError`.
    """

    def __init__(self, message: str = "An application error occurred"):
        self.message = message
        super().__init__(self.message)


class CaseNotFoundError(AppError):
    """
    Raised when a requested case does not exist.

    Maps to HTTP 404 Not Found.
    """

    def __init__(self, case_id: int):
        self.case_id = case_id
        super().__init__(f"Case with id {case_id} not found")


class UserNotFoundError(AppError):
    """
    Raised when a referenced user does not exist.

    Maps to HTTP 404 Not Found (or 422 if user ID is in request body).
    """

    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"User with id {user_id} not found")


class ValidationError(AppError):
    """
    Raised for business-rule validation failures that go beyond
    Pydantic's schema validation.

    Example: trying to assign a case to a user who doesn't exist,
    or setting status to RESOLVED without a resolved_at timestamp.

    Maps to HTTP 422 Unprocessable Entity.
    """

    def __init__(self, message: str):
        super().__init__(message)


class DatabaseError(AppError):
    """
    Raised when a database operation fails unexpectedly.

    Maps to HTTP 500 Internal Server Error.
    This wraps SQLAlchemy or database-driver exceptions so that
    database implementation details don't leak into the API layer.
    """

    def __init__(self, message: str = "A database error occurred"):
        super().__init__(message)
