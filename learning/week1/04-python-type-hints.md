# Module 04: Python Type Hints & Static Typing in Backend Systems

## 1. What It Is
**Type Hints** (introduced formally in PEP 484 and modernized in Python 3.9+ / 3.10+) allow developers to annotate variables, function parameters, and return values with expected data types. While Python remains dynamically typed at runtime, type hints enable static analysis, IDE autocomplete, and schema generation.

## 2. Why It Exists
In untyped Python, a function signature like:
```python
def process_case(c, u, flag):
    ...
```
is a black box. What is `c`? A dictionary? An ORM model? An integer ID? What is `flag`? If a developer passes a string instead of an integer ID, Python won't raise an error until runtime when deep code crashes with an `AttributeError` or `TypeError`.

With type hints:
```python
def process_case(case: Case, user_id: int, is_urgent: bool = False) -> CaseResponse:
    ...
```
The contract is completely self-documenting, and errors are caught by static analysis before deployment.

## 3. Why Backend Engineers Use It
1. **Pydantic & FastAPI Runtime Enforcement**: FastAPI reads standard Python type hints to automatically validate incoming JSON bodies, coerce types, return HTTP 422 on invalid data, and build OpenAPI documentation.
2. **Refactoring Safety**: When renaming or altering attributes in a large codebase, typecheckers (like `mypy` or `pyright`) flag every broken call site across 500 files in seconds.
3. **Eliminates Null Pointer / NoneType Bugs**: Using `Optional[T]` forces the developer to explicitly handle cases where a value might be `None`.

## 4. How It Works: Python Typing Syntax

### Basic Types & Modern Collections (Python 3.10+)
```python
# Primitives
case_id: int = 101
title: str = "Database connection pool exhausted"
sla_hours: float = 4.5
is_resolved: bool = False

# Collections (no need to import List, Dict in modern Python!)
tags: list[str] = ["database", "infrastructure", "p1"]
metadata: dict[str, str] = {"env": "prod", "region": "us-east-1"}
coordinates: tuple[int, int] = (10, 20)
unique_user_ids: set[int] = {1, 2, 3}
```

### Optional, Union, and None Handling
In modern Python 3.10+, the pipe operator `|` replaces `Union` and `Optional`:
```python
# Old syntax: Optional[str] or Union[str, None]
# Modern syntax:
assignee_id: int | None = None
search_query: str | None = None
result: int | str  # Can be int OR str
```

### Function Signatures & Generators
```python
from collections.abc import Generator
from sqlalchemy.orm import Session

# Database session dependency generator
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## 5. How Type Hints Power FastAPI and Pydantic
In [app/schemas/case.py](file:///d:/week1_kpmg/case-management-backend/app/schemas/case.py):
```python
class CaseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    priority: CasePriority = CasePriority.MEDIUM
    created_by: int = Field(..., gt=0)
    assigned_to: int | None = None
```
FastAPI parses these type annotations at startup. If a client sends:
```json
{"title": 12345, "created_by": "not-an-integer"}
```
FastAPI detects that `created_by` violates `int` and responds with:
```json
{
  "error": {
    "code": "REQUEST_VALIDATION_ERROR",
    "details": [{"field": "body -> created_by", "message": "Input should be a valid integer", "type": "int_type"}]
  }
}
```
**No custom validation code had to be written** — type hints alone enforced the boundary!

## 6. Common Mistakes & Anti-Patterns
- **Overusing `Any`**:
  ```python
  # BAD: def handle(data: Any) -> Any:
  # Using Any disables all type-checking benefits.
  ```
- **Mutable Default Arguments**:
  ```python
  # DANGEROUS:
  def add_case(title: str, tags: list[str] = []):  # The same list is shared across all calls!
      tags.append("new")
      return tags

  # SAFE:
  def add_case(title: str, tags: list[str] | None = None) -> list[str]:
      current_tags = tags if tags is not None else []
      current_tags.append("new")
      return current_tags
  ```
- **Forgetting return type annotations**:
  Always annotate return types (`-> Case:`, `-> None:`, `-> dict[str, Any]:`).

## 7. Practical Exercises
1. Inspect [app/repositories/case_repository.py](file:///d:/week1_kpmg/case-management-backend/app/repositories/case_repository.py). Find the return type hint for `get_all()`. What does `tuple[list[Case], int]` represent?
*(Answer: A tuple containing a list of `Case` ORM models and an integer representing the total count for pagination).*
2. Convert a function that returns either a `User` or `None` to use modern Python 3.10+ typing syntax.

## 8. Interview Questions & Model Answers
**Q: Does adding type hints to Python code degrade its runtime performance?**
*Answer:* No. Python type annotations are stored in the `__annotations__` dictionary of functions or classes at module load time and are completely ignored by the Python runtime evaluation loop. They have zero overhead during function execution, except for when libraries like Pydantic explicitly evaluate them once at startup to generate serialization and validation bytecode.

## 9. Short Self-Test
1. What is the modern Python 3.10+ equivalent of `Union[int, None]`? *(Answer: `int | None`)*
2. What happens if a client passes a float `3.14` to a route expecting `user_id: int`? *(Answer: FastAPI / Pydantic rejects or coerces the value based on strictness; with strict typing, it returns HTTP 422).*
