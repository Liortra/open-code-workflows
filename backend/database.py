"""SQLite connection helper, schema creation, and first-run seeding.

Per docs/architecture.md §3/§4: this module owns the SQLite connection and
schema; no router opens its own connection logic. The SQLite file lives at
backend/data/app.db, created on first run if absent (already covered by the
`*.db` entry in .gitignore).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterator

from . import seed_data

DATA_DIR = Path(__file__).resolve().parent / "data"
DB_PATH = DATA_DIR / "app.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS recipes (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT NOT NULL,
    category   TEXT NOT NULL CHECK (category IN ('Breakfast','Main','Side','Dessert')),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS recipe_ingredients (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL REFERENCES recipes(id),
    position  INTEGER NOT NULL,
    quantity  TEXT,
    name      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS recipe_steps (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id   INTEGER NOT NULL REFERENCES recipes(id),
    position    INTEGER NOT NULL,
    instruction TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS meal_plan_entries (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id  INTEGER NOT NULL REFERENCES recipes(id),
    date       TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS shopping_list_checks (
    ingredient_key TEXT PRIMARY KEY,
    checked        INTEGER NOT NULL DEFAULT 0
);
"""


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create the schema if missing and seed the 20 starter recipes on a
    fresh database (i.e. when `recipes` is empty). Called once on app
    startup (backend/main.py)."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
        _seed_if_empty(conn)
    finally:
        conn.close()


def _seed_if_empty(conn: sqlite3.Connection) -> None:
    count = conn.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
    if count > 0:
        return
    for recipe in seed_data.RECIPES:
        cur = conn.execute(
            "INSERT INTO recipes (title, category) VALUES (?, ?)",
            (recipe["title"], recipe["category"]),
        )
        recipe_id = cur.lastrowid
        for position, ingredient in enumerate(recipe["ingredients"]):
            conn.execute(
                "INSERT INTO recipe_ingredients (recipe_id, position, quantity, name) "
                "VALUES (?, ?, ?, ?)",
                (recipe_id, position, ingredient.get("quantity"), ingredient["name"]),
            )
        for position, instruction in enumerate(recipe["steps"]):
            conn.execute(
                "INSERT INTO recipe_steps (recipe_id, position, instruction) VALUES (?, ?, ?)",
                (recipe_id, position, instruction),
            )
    conn.commit()


def get_db() -> Iterator[sqlite3.Connection]:
    """FastAPI dependency: yields a connection for the duration of one
    request, closing it afterward."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
