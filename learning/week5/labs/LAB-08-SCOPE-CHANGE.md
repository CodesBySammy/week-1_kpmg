# LAB-08: Controlled Scope Change Implementation & Verification

## 1. Objective
Execute an end-to-end scope change: update database models, update schemas, enforce RBAC, and verify zero regressions.

## 2. Prerequisites
SQLAlchemy ORM, Pydantic, Alembic migrations.

## 3. Practical Task
Add a new field and role restriction to the case management system with backward compatibility.

## 4. Step-by-Step Instructions
1. Review `docs/week5/scope-change/SCOPE_CHANGE_REQUEST.md`.
2. Inspect `app/models/case.py` for `escalation_tier` column.
3. Inspect `security/rbac.py` for supervisor role enforcement.
4. Run full regression suite to verify no legacy features broke.

## 5. Expected Result
New scope verified without breaking any Week 1–4 tests.

## 6. Verification & Automated Validation
Run `pytest tests/e2e/test_scope_change_escalation.py tests/regression/`.

## 7. Challenge Questions
What is the risk of performing schema migrations in a live production environment?
