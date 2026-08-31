from fastapi import APIRouter, HTTPException

from .. import database
from ..schemas import VocabularyItem

router = APIRouter(prefix="/api/lessons", tags=["study"])


@router.get("/{lesson_id}/vocabulary", response_model=list[VocabularyItem])
def get_vocabulary(lesson_id: int):
    conn = database.get_connection()
    try:
        if not database.lesson_exists(conn, lesson_id):
            raise HTTPException(status_code=404, detail="Lesson not found")
        rows = conn.execute(
            "SELECT id, hebrew, meaning FROM vocabulary WHERE lesson_id = ? ORDER BY id",
            (lesson_id,),
        ).fetchall()
        return [
            VocabularyItem(id=r["id"], hebrew=r["hebrew"], meaning=r["meaning"])
            for r in rows
        ]
    finally:
        conn.close()
