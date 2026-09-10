-- =============================================================================
-- Case Management Backend — Database Schema
-- =============================================================================
-- This is the reference SQL schema. The actual tables are created by
-- SQLAlchemy ORM (app/models/case.py), but this file documents the schema
-- in pure SQL for learning and reference purposes.
--
-- DATABASE: SQLite (compatible with PostgreSQL with minor type changes)
--
-- DESIGN PRINCIPLES:
--   1. Normalized to 3NF (Third Normal Form) — no redundant data
--   2. Foreign keys enforce referential integrity
--   3. Enums enforced via CHECK constraints (SQLite) or ENUM types (PostgreSQL)
--   4. UTC timestamps — always store in UTC, convert for display
--   5. Audit trail via case_history table
--
-- ER DIAGRAM (Mermaid):
--   See docs/database-design.md for the full ER diagram.
-- =============================================================================

-- ── Users Table ─────────────────────────────────────────────────
-- WHY: Stores case creators and assignees separately from cases.
-- Without this, user info (name, email) would be duplicated in every case row.
-- That's denormalized and causes "update anomalies" — change a user's email
-- and you must update every case row they created.

CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    VARCHAR(50)  NOT NULL UNIQUE,
    email       VARCHAR(255) NOT NULL UNIQUE,
    full_name   VARCHAR(255) NOT NULL,
    role        VARCHAR(50)  NOT NULL DEFAULT 'analyst',
    created_at  DATETIME     NOT NULL DEFAULT (datetime('now'))
);

-- Index on username for fast lookups
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);


-- ── Cases Table ─────────────────────────────────────────────────
-- WHY: Core business entity. Each row is one case in the system.
-- Foreign keys to users table for created_by and assigned_to.

CREATE TABLE IF NOT EXISTS cases (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       VARCHAR(255) NOT NULL,
    description TEXT,
    status      VARCHAR(20)  NOT NULL DEFAULT 'OPEN'
                CHECK (status IN ('OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED')),
    priority    VARCHAR(20)  NOT NULL DEFAULT 'MEDIUM'
                CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    case_type   VARCHAR(20)  NOT NULL DEFAULT 'INQUIRY'
                CHECK (case_type IN ('BUG', 'FEATURE_REQUEST', 'INQUIRY', 'COMPLAINT')),
    created_by  INTEGER      NOT NULL,
    assigned_to INTEGER,
    created_at  DATETIME     NOT NULL DEFAULT (datetime('now')),
    updated_at  DATETIME     NOT NULL DEFAULT (datetime('now')),
    resolved_at DATETIME,

    FOREIGN KEY (created_by)  REFERENCES users(id),
    FOREIGN KEY (assigned_to) REFERENCES users(id)
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_cases_status   ON cases(status);
CREATE INDEX IF NOT EXISTS idx_cases_priority ON cases(priority);
CREATE INDEX IF NOT EXISTS idx_cases_created_by ON cases(created_by);


-- ── Case History Table ──────────────────────────────────────────
-- WHY: Audit trail. Records every field change for every case.
-- Enables:
--   - CTE queries to build change timelines
--   - Window functions to rank changes or compute time-between-changes
--   - Compliance and debugging ("who changed what, when?")

CREATE TABLE IF NOT EXISTS case_history (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id        INTEGER      NOT NULL,
    changed_by     INTEGER      NOT NULL,
    field_changed  VARCHAR(100) NOT NULL,
    old_value      TEXT,
    new_value      TEXT         NOT NULL,
    changed_at     DATETIME     NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY (case_id)    REFERENCES cases(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_case_history_case_id ON case_history(case_id);
