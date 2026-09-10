-- =============================================================================
-- Seed Data — Realistic test data for the case management system
-- =============================================================================
-- Run this AFTER schema.sql to populate the database with sample data.
-- This data is used for:
--   1. Manual API testing
--   2. SQL query practice (joins, CTEs, window functions)
--   3. Demonstrating the system works
-- =============================================================================

-- ── Users ───────────────────────────────────────────────────────
INSERT INTO users (username, email, full_name, role) VALUES
    ('asingh',   'asingh@example.com',   'Aarav Singh',    'manager'),
    ('pgupta',   'pgupta@example.com',   'Priya Gupta',    'analyst'),
    ('rkumar',   'rkumar@example.com',   'Raj Kumar',      'analyst'),
    ('nreddy',   'nreddy@example.com',   'Neha Reddy',     'senior_analyst'),
    ('vpatel',   'vpatel@example.com',   'Vikram Patel',   'admin');


-- ── Cases ───────────────────────────────────────────────────────
INSERT INTO cases (title, description, status, priority, case_type, created_by, assigned_to, created_at, updated_at) VALUES
    ('Login page returns 500 error',
     'Users clicking the login button on Chrome v120 see a 500 Internal Server Error page. Affects approximately 30% of login attempts.',
     'OPEN', 'CRITICAL', 'BUG', 1, 2,
     datetime('now', '-7 days'), datetime('now', '-7 days')),

    ('Add dark mode to dashboard',
     'Multiple clients have requested dark mode support for the analytics dashboard. This would improve usability during evening work hours.',
     'IN_PROGRESS', 'MEDIUM', 'FEATURE_REQUEST', 2, 3,
     datetime('now', '-5 days'), datetime('now', '-2 days')),

    ('How to export report as PDF?',
     'Client asked how to export their monthly compliance report as a PDF document from the reports section.',
     'RESOLVED', 'LOW', 'INQUIRY', 3, 4,
     datetime('now', '-10 days'), datetime('now', '-8 days')),

    ('Data mismatch in quarterly report',
     'The Q3 revenue figures in the dashboard do not match the source data. Discrepancy of approximately $15,000.',
     'OPEN', 'HIGH', 'BUG', 1, NULL,
     datetime('now', '-3 days'), datetime('now', '-3 days')),

    ('Slow response time on search API',
     'The /api/search endpoint takes over 5 seconds to return results when the dataset exceeds 10,000 records.',
     'IN_PROGRESS', 'HIGH', 'BUG', 4, 2,
     datetime('now', '-6 days'), datetime('now', '-1 day')),

    ('Request for bulk import feature',
     'Need ability to import cases from a CSV file for quarterly migration from legacy system.',
     'OPEN', 'MEDIUM', 'FEATURE_REQUEST', 2, NULL,
     datetime('now', '-1 day'), datetime('now', '-1 day')),

    ('Incorrect date format in notifications',
     'Email notifications show dates in MM/DD/YYYY format instead of the configured DD/MM/YYYY for non-US clients.',
     'CLOSED', 'LOW', 'BUG', 3, 3,
     datetime('now', '-15 days'), datetime('now', '-12 days')),

    ('Compliance audit preparation',
     'Need to prepare documentation and evidence for the upcoming SOC 2 compliance audit scheduled for next month.',
     'OPEN', 'CRITICAL', 'COMPLAINT', 1, 4,
     datetime('now', '-2 days'), datetime('now', '-2 days'));


-- ── Case History (audit trail) ──────────────────────────────────
-- Simulates realistic changes over time for CTE and window function exercises

INSERT INTO case_history (case_id, changed_by, field_changed, old_value, new_value, changed_at) VALUES
    -- Case 1: login bug lifecycle
    (1, 1, 'priority', 'HIGH', 'CRITICAL', datetime('now', '-6 days')),
    (1, 2, 'assigned_to', NULL, '2', datetime('now', '-6 days')),

    -- Case 2: dark mode feature progress
    (2, 3, 'status', 'OPEN', 'IN_PROGRESS', datetime('now', '-4 days')),
    (2, 3, 'assigned_to', NULL, '3', datetime('now', '-4 days')),
    (2, 1, 'priority', 'LOW', 'MEDIUM', datetime('now', '-3 days')),

    -- Case 3: inquiry resolved
    (3, 4, 'status', 'OPEN', 'IN_PROGRESS', datetime('now', '-9 days')),
    (3, 4, 'status', 'IN_PROGRESS', 'RESOLVED', datetime('now', '-8 days')),
    (3, 4, 'resolved_at', NULL, datetime('now', '-8 days'), datetime('now', '-8 days')),

    -- Case 5: search performance
    (5, 2, 'status', 'OPEN', 'IN_PROGRESS', datetime('now', '-4 days')),
    (5, 2, 'priority', 'MEDIUM', 'HIGH', datetime('now', '-2 days')),

    -- Case 7: date format bug fully resolved and closed
    (7, 3, 'status', 'OPEN', 'IN_PROGRESS', datetime('now', '-14 days')),
    (7, 3, 'status', 'IN_PROGRESS', 'RESOLVED', datetime('now', '-13 days')),
    (7, 1, 'status', 'RESOLVED', 'CLOSED', datetime('now', '-12 days'));
