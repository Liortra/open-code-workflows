from fastapi import APIRouter, HTTPException

from .. import database
from ..schemas import (
    CreateLessonRequest,
    CreateVocabularyRequest,
    Lesson,
    VocabularyCreated,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/lessons", response_model=Lesson, status_code=201)
def create_lesson(payload: CreateLessonRequest):
    conn = database.get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO lessons (title) VALUES (?)", (payload.title,)
        )
        conn.commit()
        return Lesson(id=cursor.lastrowid, title=payload.title, vocabulary_count=0)
    finally:
        conn.close()


@router.post("/vocabulary", response_model=VocabularyCreated, status_code=201)
def create_vocabulary(payload: CreateVocabularyRequest):
    conn = database.get_connection()
    try:
        if not database.lesson_exists(conn, payload.lesson_id):
            raise HTTPException(status_code=404, detail="Lesson not found")
        cursor = conn.execute(
            "INSERT INTO vocabulary (lesson_id, hebrew, meaning) VALUES (?, ?, ?)",
            (payload.lesson_id, payload.hebrew, payload.meaning),
        )
        conn.commit()
        return VocabularyCreated(
            id=cursor.lastrowid,
            lesson_id=payload.lesson_id,
            hebrew=payload.hebrew,
            meaning=payload.meaning,
        )
    finally:
        conn.close()
