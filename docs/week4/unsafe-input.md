# Unsafe Input & Validation Controls

## 1. Defensive Controls
- **Malformed Inputs:** Rejected at FastAPI Pydantic schema validation with 422 Unprocessable Entity.
- **Negative or Zero IDs:** Enforced via `gt=0` Pydantic field constraints.
- **Path Traversal / Shell Injection:** Prevented by parameterized SQL queries via SQLAlchemy ORM.
