from fastapi import APIRouter, HTTPException

from .. import database, quiz_logic
from ..schemas import Question, QuizCheckRequest, QuizCheckResponse

router = APIRouter(prefix="/api/lessons", tags=["quiz"])


@router.get("/{lesson_id}/quiz", response_model=list[Question])
def get_quiz(lesson_id: int):
    conn = database.get_connection()
    try:
        if not database.lesson_exists(conn, lesson_id):
            raise HTTPException(status_code=404, detail="Lesson not found")
        return quiz_logic.build_questions(conn, lesson_id)
    finally:
        conn.close()


@router.post("/{lesson_id}/quiz/check", response_model=QuizCheckResponse)
def check_quiz_answer(lesson_id: int, payload: QuizCheckRequest):
    conn = database.get_connection()
    try:
        if not database.lesson_exists(conn, lesson_id):
            raise HTTPException(status_code=404, detail="Lesson not found")
        row = conn.execute(
            "SELECT meaning FROM vocabulary WHERE id = ? AND lesson_id = ?",
            (payload.vocabulary_id, lesson_id),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Vocabulary item not found")
        correct_answer = row["meaning"]
        return QuizCheckResponse(
            is_correct=payload.selected == correct_answer,
            correct_answer=correct_answer,
        )
    finally:
        conn.close()
