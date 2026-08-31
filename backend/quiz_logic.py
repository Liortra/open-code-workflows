"""Shared multiple-choice question generation, per docs/architecture.md §5.

The single place that builds a question (prompt + 4 choices + which is
correct) for a vocabulary item. Both `routers/quiz.py` and `routers/exam.py`
call into this module so the two modes can never diverge in how questions
are built.
"""

import random
import sqlite3

from .schemas import Question

DISTRACTOR_COUNT = 3


def build_questions(conn: sqlite3.Connection, lesson_id: int) -> list[Question]:
    items = conn.execute(
        "SELECT id, hebrew, meaning FROM vocabulary WHERE lesson_id = ?",
        (lesson_id,),
    ).fetchall()

    questions = []
    for item in items:
        choices = [item["meaning"], *_distractors_for(conn, lesson_id, item)]
        random.shuffle(choices)
        questions.append(
            Question(vocabulary_id=item["id"], prompt=item["hebrew"], choices=choices)
        )
    random.shuffle(questions)
    return questions


def _distractors_for(
    conn: sqlite3.Connection, lesson_id: int, item: sqlite3.Row
) -> list[str]:
    same_lesson = conn.execute(
        """
        SELECT meaning FROM vocabulary
        WHERE lesson_id = ? AND id != ?
        ORDER BY RANDOM() LIMIT ?
        """,
        (lesson_id, item["id"], DISTRACTOR_COUNT),
    ).fetchall()
    distractors = [row["meaning"] for row in same_lesson]

    missing = DISTRACTOR_COUNT - len(distractors)
    if missing > 0:
        exclude = [item["meaning"], *distractors]
        placeholders = ",".join("?" for _ in exclude)
        other_lessons = conn.execute(
            f"""
            SELECT meaning FROM vocabulary
            WHERE lesson_id != ? AND meaning NOT IN ({placeholders})
            ORDER BY RANDOM() LIMIT ?
            """,
            (lesson_id, *exclude, missing),
        ).fetchall()
        distractors.extend(row["meaning"] for row in other_lessons)

    return distractors
