from fastapi import APIRouter, HTTPException

from .. import database
from ..schemas import Lesson, LessonDetail

router = APIRouter(prefix="/api/lessons", tags=["lessons"])

_LESSON_WITH_COUNT_SQL = """
SELECT l.id, l.title, COUNT(v.id) AS vocabulary_count
FROM lessons l
LEFT JOIN vocabulary v ON v.lesson_id = l.id
{where}
GROUP BY l.id
ORDER BY l.id
"""


@router.get("", response_model=list[Lesson])
def list_lessons():
    conn = database.get_connection()
    try:
        rows = conn.execute(_LESSON_WITH_COUNT_SQL.format(where="")).fetchall()
        return [
            Lesson(id=r["id"], title=r["title"], vocabulary_count=r["vocabulary_count"])
            for r in rows
        ]
    finally:
        conn.close()


@router.get("/{lesson_id}", response_model=LessonDetail)
def get_lesson(lesson_id: int):
    conn = database.get_connection()
    try:
        row = conn.execute(
            _LESSON_WITH_COUNT_SQL.format(where="WHERE l.id = ?"), (lesson_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Lesson not found")
        has_exam_history = (
            conn.execute(
                "SELECT 1 FROM exam_attempts WHERE lesson_id = ? LIMIT 1", (lesson_id,)
            ).fetchone()
            is not None
        )
        return LessonDetail(
            id=row["id"],
            title=row["title"],
            vocabulary_count=row["vocabulary_count"],
            has_exam_history=has_exam_history,
        )
    finally:
        conn.close()
