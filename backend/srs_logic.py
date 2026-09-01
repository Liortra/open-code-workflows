"""Spaced-repetition scheduling logic, per docs/architecture.md §11.3.

Owns the "which words are due" query and the day-ladder scheduling
transition rule applied by `POST /api/srs/{vocabulary_id}/answer`. Question
building reuses `quiz_logic.distractors_for` so SRS review items are never
built with a different distractor strategy than Quiz/Exam (§11.4/§11.5).
"""

import random
import sqlite3

from .quiz_logic import distractors_for
from .schemas import SrsDueItem

# Coordinator-approved day-ladder (§11.3), indices 0-5. Index 0 (due
# immediately) is reachable only via an incorrect answer, never as the
# result of a correct one -- see `score_answer` below.
DAY_LADDER = [0, 1, 3, 7, 14, 30]


def build_due_questions(conn: sqlite3.Connection) -> list[SrsDueItem]:
    """Every vocabulary item currently due across all lessons.

    A word with no `word_review_state` row has never been reviewed and is
    therefore due (§11.2 note). A word whose `next_due_at` has elapsed is
    also due.
    """
    rows = conn.execute(
        """
        SELECT v.id, v.lesson_id, v.hebrew, v.meaning
        FROM vocabulary v
        LEFT JOIN word_review_state w ON w.vocabulary_id = v.id
        WHERE w.vocabulary_id IS NULL
           OR w.next_due_at <= strftime('%Y-%m-%dT%H:%M:%S', 'now')
        """
    ).fetchall()

    items = []
    for row in rows:
        choices = [row["meaning"], *distractors_for(conn, row["lesson_id"], row)]
        random.shuffle(choices)
        items.append(
            SrsDueItem(
                vocabulary_id=row["id"],
                lesson_id=row["lesson_id"],
                prompt=row["hebrew"],
                choices=choices,
            )
        )
    random.shuffle(items)
    return items


def score_answer(conn: sqlite3.Connection, vocabulary_id: int, is_correct: bool) -> str:
    """Upsert `word_review_state` per the day-ladder transition rule (§11.3).

    Returns the new `next_due_at` timestamp. Does not commit -- the caller
    controls the transaction so this can be combined with the
    `activity_log` insert in a single commit, per §11.4's "single request,
    single transaction" side-effect note.
    """
    prior = conn.execute(
        "SELECT interval_index, last_result FROM word_review_state WHERE vocabulary_id = ?",
        (vocabulary_id,),
    ).fetchone()

    if is_correct:
        # First-ever answer, or the prior answer was incorrect: always land
        # on the 1-day rung, never on 0 -- a correct answer must never make
        # the word due again immediately (brief's acceptance test).
        if prior is None or prior["last_result"] == "incorrect":
            interval_index = 1
        else:
            interval_index = min(prior["interval_index"] + 1, len(DAY_LADDER) - 1)
        last_result = "correct"
        days = DAY_LADDER[interval_index]
        next_due_at = conn.execute(
            "SELECT strftime('%Y-%m-%dT%H:%M:%S', 'now', ?)", (f"+{days} days",)
        ).fetchone()[0]
    else:
        interval_index = 0
        last_result = "incorrect"
        next_due_at = conn.execute(
            "SELECT strftime('%Y-%m-%dT%H:%M:%S', 'now')"
        ).fetchone()[0]

    conn.execute(
        """
        INSERT INTO word_review_state
            (vocabulary_id, interval_index, last_result, last_reviewed_at, next_due_at)
        VALUES (?, ?, ?, strftime('%Y-%m-%dT%H:%M:%S', 'now'), ?)
        ON CONFLICT(vocabulary_id) DO UPDATE SET
            interval_index = excluded.interval_index,
            last_result = excluded.last_result,
            last_reviewed_at = excluded.last_reviewed_at,
            next_due_at = excluded.next_due_at
        """,
        (vocabulary_id, interval_index, last_result, next_due_at),
    )
    return next_due_at
