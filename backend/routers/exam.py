from fastapi import APIRouter, HTTPException

from .. import database, quiz_logic
from ..schemas import (
    ExamHistoryItem,
    ExamReviewItem,
    ExamSubmitRequest,
    ExamSubmitResponse,
    Question,
)

router = APIRouter(prefix="/api/lessons", tags=["exam"])


@router.get("/{lesson_id}/exam", response_model=list[Question])
def get_exam(lesson_id: int):
    conn = database.get_connection()
    try:
        if not database.lesson_exists(conn, lesson_id):
            raise HTTPException(status_code=404, detail="Lesson not found")
        return quiz_logic.build_questions(conn, lesson_id)
    finally:
        conn.close()


@router.post("/{lesson_id}/exam/submit", response_model=ExamSubmitResponse)
def submit_exam(lesson_id: int, payload: ExamSubmitRequest):
    conn = database.get_connection()
    try:
        if not database.lesson_exists(conn, lesson_id):
            raise HTTPException(status_code=404, detail="Lesson not found")

        vocab_by_id = {
            row["id"]: row
            for row in conn.execute(
                "SELECT id, hebrew, meaning FROM vocabulary WHERE lesson_id = ?",
                (lesson_id,),
            ).fetchall()
        }
        answers_by_id = {a.vocabulary_id: a.selected for a in payload.answers}
        if set(answers_by_id) != set(vocab_by_id):
            raise HTTPException(
                status_code=422,
                detail=(
                    "Exam submission must include exactly one answer for every "
                    "vocabulary item in the lesson"
                ),
            )

        review = []
        score = 0
        for vocab_id, vocab in vocab_by_id.items():
            selected = answers_by_id[vocab_id]
            is_correct = selected == vocab["meaning"]
            score += is_correct
            review.append(
                ExamReviewItem(
                    vocabulary_id=vocab_id,
                    prompt=vocab["hebrew"],
                    selected=selected,
                    correct_answer=vocab["meaning"],
                    is_correct=is_correct,
                )
            )

        cursor = conn.execute(
            "INSERT INTO exam_attempts (lesson_id, score, total) VALUES (?, ?, ?)",
            (lesson_id, score, len(vocab_by_id)),
        )
        conn.commit()
        taken_at = conn.execute(
            "SELECT taken_at FROM exam_attempts WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()["taken_at"]

        return ExamSubmitResponse(
            score=score, total=len(vocab_by_id), taken_at=taken_at, review=review
        )
    finally:
        conn.close()


@router.get("/{lesson_id}/exam/history", response_model=list[ExamHistoryItem])
def get_exam_history(lesson_id: int):
    conn = database.get_connection()
    try:
        if not database.lesson_exists(conn, lesson_id):
            raise HTTPException(status_code=404, detail="Lesson not found")
        rows = conn.execute(
            """
            SELECT id, score, total, taken_at FROM exam_attempts
            WHERE lesson_id = ?
            ORDER BY taken_at DESC, id DESC
            """,
            (lesson_id,),
        ).fetchall()
        return [
            ExamHistoryItem(
                id=r["id"], score=r["score"], total=r["total"], taken_at=r["taken_at"]
            )
            for r in rows
        ]
    finally:
        conn.close()
