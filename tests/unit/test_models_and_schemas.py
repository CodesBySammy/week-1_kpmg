"""
Unit Tests for Models and Schemas

Validates:
  - String representations (__repr__)
  - Model field defaults
  - Pydantic schema validation errors for boundary values
"""

import pytest
from pydantic import ValidationError as PydanticValidationError
from app.models.case import Case, CaseHistory, CasePriority, CaseStatus, CaseType, User
from app.schemas.case import CaseCreate, CaseUpdate, UserCreate


def test_model_repr():
    user = User(id=1, username="alex")
    assert "<User(id=1, username='alex')>" == repr(user)

    case = Case(id=42, title="Bug Title", status=CaseStatus.OPEN)
    assert "<Case(id=42, title='Bug Title', status='CaseStatus.OPEN')>" in repr(case)

    history = CaseHistory(case_id=42, field_changed="status")
    assert "<CaseHistory(case_id=42, field='status')>" == repr(history)


def test_schema_title_too_long():
    with pytest.raises(PydanticValidationError):
        CaseCreate(
            title="A" * 256,  # max_length is 255
            created_by=1,
        )


def test_schema_user_create_invalid_username():
    with pytest.raises(PydanticValidationError):
        UserCreate(
            username="a",  # min_length is 2
            email="invalid",
            full_name="Alex",
        )
