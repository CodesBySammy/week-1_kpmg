"""
Case API Routes

WHY ROUTES ARE THIN:
    Route handlers should do exactly three things:
      1. Receive the HTTP request (FastAPI handles parsing automatically)
      2. Call the service layer
      3. Return the HTTP response

    They should NOT contain business logic, database queries, or validation
    beyond what Pydantic provides. This keeps routes easy to read and test.

HOW FASTAPI ROUTES WORK:
    @router.post("/cases") registers a function to handle POST /cases.
    FastAPI automatically:
      - Parses the JSON request body into the Pydantic schema
      - Validates all fields (returns 422 if invalid)
      - Injects dependencies (like the database session)
      - Serializes the return value to JSON
      - Sets the correct status code

CURRICULUM CONNECTION:
    Week 1 requires: REST endpoints, HTTP methods, request validation,
    status codes, OpenAPI documentation.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.case import CasePriority, CaseStatus
from app.schemas.case import (
    CaseCreate,
    CaseListResponse,
    CaseResponse,
    CaseUpdate,
    UserCreate,
    UserResponse,
)
from app.services.case_service import CaseService

logger = logging.getLogger(__name__)

# ── Router Setup ─────────────────────────────────────────────────
# APIRouter groups related endpoints. The prefix "/cases" means all
# routes here are under /cases (e.g., POST /cases, GET /cases/{id}).
# Tags organize endpoints in OpenAPI documentation.

router = APIRouter()
case_service = CaseService()


# ── Case Endpoints ───────────────────────────────────────────────


@router.post(
    "/cases",
    response_model=CaseResponse,
    status_code=201,  # 201 Created (not 200 OK — resource was created)
    summary="Create a new case",
    description="Create a new case with the provided details. "
    "The creator must be an existing user.",
    tags=["Cases"],
)
def create_case(
    case_data: CaseCreate,
    db: Session = Depends(get_db),
) -> CaseResponse:
    """
    Create a new case.

    - **title**: Brief summary (required, 1–255 chars)
    - **created_by**: ID of the creating user (required, must exist)
    - **priority**: LOW, MEDIUM, HIGH, CRITICAL (default: MEDIUM)
    - **case_type**: BUG, FEATURE_REQUEST, INQUIRY, COMPLAINT (default: INQUIRY)
    """
    logger.info(
        "Received create case request",
        extra={"title": case_data.title, "operation": "api_create_case"},
    )
    case = case_service.create_case(db, case_data)
    return CaseResponse.model_validate(case)


@router.get(
    "/cases/{case_id}",
    response_model=CaseResponse,
    summary="Retrieve a case by ID",
    description="Fetch a single case by its unique identifier.",
    tags=["Cases"],
)
def get_case(
    case_id: int,
    db: Session = Depends(get_db),
) -> CaseResponse:
    """
    Retrieve a case.

    Returns 404 if the case does not exist.
    """
    logger.debug(
        "Received get case request",
        extra={"case_id": case_id, "operation": "api_get_case"},
    )
    case = case_service.get_case(db, case_id)
    return CaseResponse.model_validate(case)


@router.get(
    "/cases",
    response_model=CaseListResponse,
    summary="List all cases",
    description="Retrieve a paginated list of cases with optional filters.",
    tags=["Cases"],
)
def list_cases(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Max records to return"),
    status: Optional[CaseStatus] = Query(None, description="Filter by status"),
    priority: Optional[CasePriority] = Query(None, description="Filter by priority"),
    db: Session = Depends(get_db),
) -> CaseListResponse:
    """
    List cases with pagination and optional filters.
    """
    cases, total = case_service.list_cases(
        db, skip=skip, limit=limit,
        status=status.value if status else None,
        priority=priority.value if priority else None,
    )
    return CaseListResponse(
        cases=[CaseResponse.model_validate(c) for c in cases],
        total=total,
    )


@router.put(
    "/cases/{case_id}",
    response_model=CaseResponse,
    summary="Update a case",
    description="Update one or more fields of an existing case.",
    tags=["Cases"],
)
def update_case(
    case_id: int,
    case_data: CaseUpdate,
    db: Session = Depends(get_db),
) -> CaseResponse:
    """
    Update a case.

    Only send the fields you want to change.
    Returns 404 if the case does not exist.
    Returns 422 if no fields are provided or validation fails.
    """
    logger.info(
        "Received update case request",
        extra={"case_id": case_id, "operation": "api_update_case"},
    )
    case = case_service.update_case(db, case_id, case_data)
    return CaseResponse.model_validate(case)


# ── User Endpoints (supporting resource) ─────────────────────────
# Users are needed so we can create cases with valid created_by IDs.


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=201,
    summary="Create a new user",
    description="Create a user who can create or be assigned cases.",
    tags=["Users"],
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
) -> UserResponse:
    """Create a new user."""
    from app.models.case import User
    from app.repositories.case_repository import UserRepository

    user_repo = UserRepository()
    user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        role=user_data.role,
    )
    created_user = user_repo.create(db, user)
    return UserResponse.model_validate(created_user)


@router.get(
    "/users",
    response_model=list[UserResponse],
    summary="List all users",
    tags=["Users"],
)
def list_users(
    db: Session = Depends(get_db),
) -> list[UserResponse]:
    """List all users."""
    from app.repositories.case_repository import UserRepository

    user_repo = UserRepository()
    users = user_repo.get_all(db)
    return [UserResponse.model_validate(u) for u in users]
