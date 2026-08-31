"""SQLite connection helper, schema creation, and first-run seeding.

All persistence access goes through this module; routers never open their
own connections or embed schema-creation logic.
"""

import sqlite3
from pathlib import Path

from .seed_data import LESSONS

DB_PATH = Path(__file__).resolve().parent / "data" / "app.db"

# `strftime(..., 'now')` (rather than `datetime('now')`) so stored timestamps
# are already ISO-8601 with a 'T' separator, matching the API contracts in
# docs/architecture.md section 6 (e.g. "taken_at": "2026-08-31T12:00:00").
SCHEMA = """
CREATE TABLE IF NOT EXISTS lessons (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now'))
);

CREATE TABLE IF NOT EXISTS vocabulary (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_id  INTEGER NOT NULL REFERENCES lessons(id),
    hebrew     TEXT NOT NULL,
    meaning    TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now'))
);

CREATE TABLE IF NOT EXISTS exam_attempts (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_id  INTEGER NOT NULL REFERENCES lessons(id),
    score      INTEGER NOT NULL,
    total      INTEGER NOT NULL,
    taken_at   TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now'))
);
"""


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
        _seed_if_empty(conn)
    finally:
        conn.close()


def lesson_exists(conn: sqlite3.Connection, lesson_id: int) -> bool:
    return (
        conn.execute("SELECT 1 FROM lessons WHERE id = ?", (lesson_id,)).fetchone()
        is not None
    )


def _seed_if_empty(conn: sqlite3.Connection) -> None:
    count = conn.execute("SELECT COUNT(*) FROM lessons").fetchone()[0]
    if count > 0:
        return
    for lesson in LESSONS:
        cursor = conn.execute(
            "INSERT INTO lessons (title) VALUES (?)", (lesson["title"],)
        )
        lesson_id = cursor.lastrowid
        conn.executemany(
            "INSERT INTO vocabulary (lesson_id, hebrew, meaning) VALUES (?, ?, ?)",
            [(lesson_id, v["hebrew"], v["meaning"]) for v in lesson["vocabulary"]],
        )
    conn.commit()
