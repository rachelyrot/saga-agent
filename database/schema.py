"""
database/schema.py
All CREATE TABLE statements and init_db() for Saga's SQLite database.
"""

import sqlite3
import os

# Resolve the DB path relative to this file's location so it always lands
# at the project root regardless of the working directory at runtime.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(_PROJECT_ROOT, "saga.db")


def get_connection() -> sqlite3.Connection:
    """Return a connection with foreign keys enabled and Row factory set."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ---------------------------------------------------------------------------
# Table DDL
# ---------------------------------------------------------------------------

_CREATE_DAILY_PLANS = """
CREATE TABLE IF NOT EXISTS daily_plans (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TEXT    NOT NULL UNIQUE,   -- ISO-8601: YYYY-MM-DD
    raw_input       TEXT    NOT NULL,          -- user's brain-dump text
    plan_output     TEXT    NOT NULL,          -- full markdown plan from Morning Agent
    priorities      TEXT    NOT NULL DEFAULT '[]',  -- JSON array of priority strings
    energy_level    INTEGER NOT NULL DEFAULT 3,     -- 1-5
    mood_morning    TEXT    NOT NULL DEFAULT '',     -- emoji or label
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);
"""

_CREATE_REFLECTIONS = """
CREATE TABLE IF NOT EXISTS reflections (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TEXT    NOT NULL UNIQUE,   -- ISO-8601: YYYY-MM-DD
    plan_id         INTEGER REFERENCES daily_plans(id) ON DELETE SET NULL,
    questions       TEXT    NOT NULL DEFAULT '[]',  -- JSON array of 3 question strings
    answers         TEXT    NOT NULL DEFAULT '[]',  -- JSON array of 3 answer strings
    completion_pct  INTEGER NOT NULL DEFAULT 0,     -- 0-100
    mood_evening    TEXT    NOT NULL DEFAULT '',     -- emoji or label
    wins            TEXT    NOT NULL DEFAULT '[]',  -- JSON array of win strings
    blockers        TEXT    NOT NULL DEFAULT '[]',  -- JSON array of blocker strings
    insight_summary TEXT    NOT NULL DEFAULT '',    -- short paragraph from Phase 2
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);
"""

_CREATE_TASKS = """
CREATE TABLE IF NOT EXISTS tasks (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id       INTEGER REFERENCES daily_plans(id) ON DELETE CASCADE,
    date          TEXT    NOT NULL,   -- ISO-8601: YYYY-MM-DD (denormalized for fast queries)
    task_text     TEXT    NOT NULL,
    priority_rank INTEGER NOT NULL DEFAULT 0,  -- 1 = highest priority
    category      TEXT    NOT NULL DEFAULT 'Work',  -- Work | Personal | Health | Creative | Admin
    completed     INTEGER NOT NULL DEFAULT 0   -- 0 = false, 1 = true
);
"""

_CREATE_WEEKLY_NARRATIVES = """
CREATE TABLE IF NOT EXISTS weekly_narratives (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    week_start TEXT    NOT NULL UNIQUE,  -- ISO-8601: Monday of the week
    week_end   TEXT    NOT NULL,         -- Sunday of the week
    narrative  TEXT    NOT NULL DEFAULT '',  -- long markdown from Weekly Narrator
    stats      TEXT    NOT NULL DEFAULT '{}',  -- JSON: avg_completion, avg_mood, total_tasks, etc.
    theme      TEXT    NOT NULL DEFAULT '',    -- short theme string from the agent
    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);
"""

_ALL_TABLES = [
    _CREATE_DAILY_PLANS,
    _CREATE_REFLECTIONS,
    _CREATE_TASKS,
    _CREATE_WEEKLY_NARRATIVES,
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def init_db() -> None:
    """
    Create all tables (if they don't already exist) and apply any lightweight
    schema migrations needed on existing databases.

    Safe to call on every app start — it is idempotent.
    """
    with get_connection() as conn:
        for ddl in _ALL_TABLES:
            conn.execute(ddl)
        conn.commit()
    print(f"[saga] DB initialised at: {DB_PATH}")


if __name__ == "__main__":
    init_db()
