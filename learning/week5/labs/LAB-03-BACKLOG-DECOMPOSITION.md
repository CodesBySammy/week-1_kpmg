# LAB-03: Backlog Decomposition into Vertical Slices

## 1. Objective
Decompose an ambiguous enterprise feature epic into independently testable vertical slices.

## 2. Prerequisites
Understanding of vertical slicing and Agile requirements decomposition.

## 3. Practical Task
Deconstruct the 'Case Escalation & Department Isolation' epic into 3 vertical slices.

## 4. Step-by-Step Instructions
1. Define slice boundaries: Slice 1 (Schema & DB), Slice 2 (RBAC & Service), Slice 3 (Tool & E2E API).
2. Write GIVEN/WHEN/THEN acceptance criteria for each slice.
3. Map slices to automated tests in `tests/e2e/`.

## 5. Expected Result
Decomposed technical backlog in `docs/week5/backlog/TECHNICAL_BACKLOG.md`.

## 6. Verification & Automated Validation
Execute `pytest tests/e2e/test_scope_change_escalation.py`.

## 7. Challenge Questions
Why is a vertical slice that includes audit logging better than adding audit logging at the end of the project?
