-- =============================================================================
-- Transaction Examples — ACID Properties and Isolation
-- =============================================================================
-- Transactions guarantee that a group of operations either ALL succeed
-- or ALL fail (atomicity). This prevents partial updates that leave
-- the database in an inconsistent state.
--
-- ACID PROPERTIES:
--   A — Atomicity:    All or nothing (partial commits impossible)
--   C — Consistency:  Database moves from one valid state to another
--   I — Isolation:    Concurrent transactions don't interfere
--   D — Durability:   Committed changes survive crashes
--
-- NOTE: SQLite auto-commits by default. Use BEGIN/COMMIT/ROLLBACK
-- to group operations into explicit transactions.
-- =============================================================================


-- ═══════════════════════════════════════════════════════════════════
-- EXAMPLE 1: Successful Transaction (Case Assignment)
-- ═══════════════════════════════════════════════════════════════════
-- Scenario: Assign a case AND record the change in history.
-- Both must succeed or both must fail.

BEGIN TRANSACTION;

-- Step 1: Update the case assignment
UPDATE cases
SET assigned_to = 3, updated_at = datetime('now')
WHERE id = 4;

-- Step 2: Record the change in audit history
INSERT INTO case_history (case_id, changed_by, field_changed, old_value, new_value, changed_at)
VALUES (4, 1, 'assigned_to', NULL, '3', datetime('now'));

-- Both operations succeeded → commit
COMMIT;


-- ═══════════════════════════════════════════════════════════════════
-- EXAMPLE 2: Rollback on Error (Status Transition)
-- ═══════════════════════════════════════════════════════════════════
-- Scenario: Change status to RESOLVED and set resolved_at.
-- If either fails, roll back both.
-- This is a "simulated" rollback — in practice, the application
-- code would catch the error and call ROLLBACK.

BEGIN TRANSACTION;

-- Step 1: Update status
UPDATE cases
SET status = 'RESOLVED',
    resolved_at = datetime('now'),
    updated_at = datetime('now')
WHERE id = 1;

-- Step 2: Record history
INSERT INTO case_history (case_id, changed_by, field_changed, old_value, new_value, changed_at)
VALUES (1, 2, 'status', 'OPEN', 'RESOLVED', datetime('now'));

-- If something went wrong, you would ROLLBACK instead:
-- ROLLBACK;

-- Everything is fine → commit
COMMIT;


-- ═══════════════════════════════════════════════════════════════════
-- EXAMPLE 3: Transaction with Validation Check
-- ═══════════════════════════════════════════════════════════════════
-- Scenario: Only update if the case is in a valid state.
-- This mimics what the application code does in the service layer.

BEGIN TRANSACTION;

-- Check: only proceed if case is not CLOSED
-- (In application code, this is an IF statement; in SQL, it's a WHERE clause)
UPDATE cases
SET priority = 'CRITICAL',
    updated_at = datetime('now')
WHERE id = 6
  AND status != 'CLOSED';

-- Record history (only if the update actually changed a row)
-- In practice, the application checks the affected row count
INSERT INTO case_history (case_id, changed_by, field_changed, old_value, new_value, changed_at)
SELECT 6, 2, 'priority', 'MEDIUM', 'CRITICAL', datetime('now')
WHERE changes() > 0;

COMMIT;


-- ═══════════════════════════════════════════════════════════════════
-- EXAMPLE 4: Bulk Update in a Transaction
-- ═══════════════════════════════════════════════════════════════════
-- Scenario: Reassign all cases from one user to another (e.g., user leaves).
-- All reassignments must happen together.

BEGIN TRANSACTION;

-- Record history for each case being reassigned
INSERT INTO case_history (case_id, changed_by, field_changed, old_value, new_value, changed_at)
SELECT id, 1, 'assigned_to', CAST(assigned_to AS TEXT), '4', datetime('now')
FROM cases
WHERE assigned_to = 2
  AND status IN ('OPEN', 'IN_PROGRESS');

-- Perform the reassignment
UPDATE cases
SET assigned_to = 4,
    updated_at = datetime('now')
WHERE assigned_to = 2
  AND status IN ('OPEN', 'IN_PROGRESS');

COMMIT;


-- ═══════════════════════════════════════════════════════════════════
-- EXAMPLE 5: Using SAVEPOINT for Nested Operations
-- ═══════════════════════════════════════════════════════════════════
-- SAVEPOINT is like a checkpoint within a transaction.
-- You can roll back to a savepoint without losing the entire transaction.

BEGIN TRANSACTION;

-- First operation: always succeeds
UPDATE cases SET updated_at = datetime('now') WHERE id = 1;

-- Savepoint before risky operation
SAVEPOINT before_risky_update;

-- Risky operation: try to update a case that might not exist
UPDATE cases SET priority = 'LOW' WHERE id = 999;

-- If the risky operation affected 0 rows, roll back to savepoint
-- (In application code: if affected_rows == 0: rollback to savepoint)
-- ROLLBACK TO SAVEPOINT before_risky_update;

-- Release the savepoint (merge it into the main transaction)
RELEASE SAVEPOINT before_risky_update;

COMMIT;
