-- =============================================================================
-- SQL Queries — Joins, CTEs, and Window Functions Practice
-- =============================================================================
-- These queries demonstrate the SQL concepts required by Week 1:
--   1. JOINs (INNER, LEFT, self-joins)
--   2. CTEs (Common Table Expressions)
--   3. Window functions (ROW_NUMBER, RANK, LAG, aggregate windows)
--
-- Run these against the database after loading schema.sql and seed.sql.
-- =============================================================================


-- ═══════════════════════════════════════════════════════════════════
-- SECTION 1: JOINs
-- ═══════════════════════════════════════════════════════════════════

-- ── 1a. INNER JOIN: Cases with their creators ───────────────────
-- Shows: INNER JOIN returns only rows with matches in BOTH tables.
-- If a case had no creator (impossible due to NOT NULL), it would be excluded.

SELECT
    c.id        AS case_id,
    c.title,
    c.status,
    c.priority,
    u.full_name AS creator_name,
    u.email     AS creator_email
FROM cases c
INNER JOIN users u ON c.created_by = u.id
ORDER BY c.created_at DESC;


-- ── 1b. LEFT JOIN: Cases with assignees (including unassigned) ──
-- Shows: LEFT JOIN keeps ALL rows from the left table (cases), even if
-- there's no matching row in the right table (users). Unassigned cases
-- show NULL for assignee fields.

SELECT
    c.id        AS case_id,
    c.title,
    c.status,
    u.full_name AS assignee_name,
    CASE
        WHEN u.full_name IS NULL THEN 'UNASSIGNED'
        ELSE u.full_name
    END AS assignee_display
FROM cases c
LEFT JOIN users u ON c.assigned_to = u.id
ORDER BY c.priority DESC;


-- ── 1c. Multiple JOINs: Full case details ──────────────────────
-- Shows: You can join the same table multiple times with different aliases.

SELECT
    c.id        AS case_id,
    c.title,
    c.status,
    c.priority,
    c.case_type,
    creator.full_name  AS created_by_name,
    assignee.full_name AS assigned_to_name,
    c.created_at,
    c.updated_at
FROM cases c
INNER JOIN users creator   ON c.created_by  = creator.id
LEFT  JOIN users assignee  ON c.assigned_to = assignee.id
ORDER BY c.created_at DESC;


-- ── 1d. JOIN with aggregation: Cases per user ───────────────────
-- Shows: JOINs combined with GROUP BY for aggregate reporting.

SELECT
    u.full_name,
    u.role,
    COUNT(c.id) AS cases_created,
    SUM(CASE WHEN c.status = 'OPEN' THEN 1 ELSE 0 END) AS open_cases,
    SUM(CASE WHEN c.status = 'RESOLVED' THEN 1 ELSE 0 END) AS resolved_cases
FROM users u
LEFT JOIN cases c ON u.id = c.created_by
GROUP BY u.id, u.full_name, u.role
ORDER BY cases_created DESC;


-- ═══════════════════════════════════════════════════════════════════
-- SECTION 2: CTEs (Common Table Expressions)
-- ═══════════════════════════════════════════════════════════════════

-- ── 2a. Basic CTE: Case summary dashboard ──────────────────────
-- A CTE is like a temporary named query. Think of it as creating
-- a temporary table that only exists for this one query.
-- CTEs make complex queries readable by breaking them into steps.

WITH case_summary AS (
    SELECT
        status,
        priority,
        COUNT(*)              AS total_cases,
        MIN(created_at)       AS earliest_case,
        MAX(created_at)       AS latest_case
    FROM cases
    GROUP BY status, priority
)
SELECT
    status,
    priority,
    total_cases,
    earliest_case,
    latest_case
FROM case_summary
ORDER BY
    CASE status
        WHEN 'OPEN' THEN 1
        WHEN 'IN_PROGRESS' THEN 2
        WHEN 'RESOLVED' THEN 3
        WHEN 'CLOSED' THEN 4
    END,
    CASE priority
        WHEN 'CRITICAL' THEN 1
        WHEN 'HIGH' THEN 2
        WHEN 'MEDIUM' THEN 3
        WHEN 'LOW' THEN 4
    END;


-- ── 2b. Multiple CTEs: Change activity report ──────────────────
-- Shows: You can chain multiple CTEs, each building on previous ones.

WITH change_counts AS (
    SELECT
        case_id,
        COUNT(*) AS total_changes,
        MIN(changed_at) AS first_change,
        MAX(changed_at) AS last_change
    FROM case_history
    GROUP BY case_id
),
case_details AS (
    SELECT
        c.id,
        c.title,
        c.status,
        c.priority,
        creator.full_name AS creator_name
    FROM cases c
    INNER JOIN users creator ON c.created_by = creator.id
)
SELECT
    cd.title,
    cd.status,
    cd.creator_name,
    COALESCE(cc.total_changes, 0) AS total_changes,
    cc.first_change,
    cc.last_change
FROM case_details cd
LEFT JOIN change_counts cc ON cd.id = cc.case_id
ORDER BY total_changes DESC;


-- ── 2c. CTE for workload analysis ──────────────────────────────

WITH user_workload AS (
    SELECT
        u.id AS user_id,
        u.full_name,
        u.role,
        COUNT(DISTINCT c_created.id) AS cases_created,
        COUNT(DISTINCT c_assigned.id) AS cases_assigned
    FROM users u
    LEFT JOIN cases c_created  ON u.id = c_created.created_by
    LEFT JOIN cases c_assigned ON u.id = c_assigned.assigned_to
        AND c_assigned.status IN ('OPEN', 'IN_PROGRESS')
    GROUP BY u.id, u.full_name, u.role
)
SELECT
    full_name,
    role,
    cases_created,
    cases_assigned,
    CASE
        WHEN cases_assigned > 3 THEN 'OVERLOADED'
        WHEN cases_assigned > 1 THEN 'BUSY'
        ELSE 'AVAILABLE'
    END AS workload_status
FROM user_workload
ORDER BY cases_assigned DESC;


-- ═══════════════════════════════════════════════════════════════════
-- SECTION 3: WINDOW FUNCTIONS
-- ═══════════════════════════════════════════════════════════════════

-- ── 3a. ROW_NUMBER: Rank cases by creation date ────────────────
-- Window functions compute a value across a SET of rows related to
-- the current row, WITHOUT collapsing rows (unlike GROUP BY).
--
-- ROW_NUMBER() assigns 1, 2, 3... to each row within a partition.

SELECT
    id,
    title,
    status,
    priority,
    created_at,
    ROW_NUMBER() OVER (
        PARTITION BY status
        ORDER BY created_at ASC
    ) AS row_num_within_status
FROM cases
ORDER BY status, row_num_within_status;


-- ── 3b. RANK: Priority ranking within status ───────────────────
-- RANK() is like ROW_NUMBER() but handles ties differently:
-- If two rows tie, they get the same rank, and the next rank is skipped.

SELECT
    id,
    title,
    status,
    priority,
    RANK() OVER (
        PARTITION BY status
        ORDER BY
            CASE priority
                WHEN 'CRITICAL' THEN 1
                WHEN 'HIGH' THEN 2
                WHEN 'MEDIUM' THEN 3
                WHEN 'LOW' THEN 4
            END
    ) AS priority_rank
FROM cases
ORDER BY status, priority_rank;


-- ── 3c. LAG: Time between consecutive changes ──────────────────
-- LAG() looks at the PREVIOUS row's value. Useful for computing
-- durations, detecting gaps, or comparing consecutive records.

SELECT
    ch.case_id,
    c.title,
    ch.field_changed,
    ch.old_value,
    ch.new_value,
    ch.changed_at,
    LAG(ch.changed_at) OVER (
        PARTITION BY ch.case_id
        ORDER BY ch.changed_at
    ) AS previous_change_at,
    ROUND(
        (JULIANDAY(ch.changed_at) - JULIANDAY(
            LAG(ch.changed_at) OVER (
                PARTITION BY ch.case_id
                ORDER BY ch.changed_at
            )
        )) * 24, 2
    ) AS hours_since_last_change
FROM case_history ch
INNER JOIN cases c ON ch.case_id = c.id
ORDER BY ch.case_id, ch.changed_at;


-- ── 3d. Aggregate Window: Running total of changes ─────────────
-- SUM() OVER(...) gives a running total without collapsing rows.

SELECT
    ch.case_id,
    c.title,
    ch.field_changed,
    ch.changed_at,
    COUNT(*) OVER (
        PARTITION BY ch.case_id
        ORDER BY ch.changed_at
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_change_count,
    COUNT(*) OVER (
        PARTITION BY ch.case_id
    ) AS total_changes_for_case
FROM case_history ch
INNER JOIN cases c ON ch.case_id = c.id
ORDER BY ch.case_id, ch.changed_at;
