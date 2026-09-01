"""Spaced Repetition ("Due for Review") endpoints, per docs/architecture.md §11.4."""

from fastapi import APIRouter, HTTPException

from .. import database, srs_logic
from ..schemas import SrsAnswerRequest, SrsAnswerResponse, SrsDueItem

router = APIRouter(prefix="/api/srs", tags=["srs"])


@router.get("/due", response_model=list[SrsDueItem])
def get_due():
    conn = database.get_connection()
    try:
        return srs_logic.build_due_questions(conn)
    finally:
        conn.close()


@router.post("/{vocabulary_id}/answer", response_model=SrsAnswerResponse)
def answer_srs_item(vocabulary_id: int, payload: SrsAnswerRequest):
    conn = database.get_connection()
    try:
        row = conn.execute(
            "SELECT meaning FROM vocabulary WHERE id = ?", (vocabulary_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Vocabulary item not found")

        correct_answer = row["meaning"]
        is_correct = payload.selected == correct_answer

        # Single transaction: upsert word_review_state and log the SRS
        # completion signal together (§11.4).
        next_due_at = srs_logic.score_answer(conn, vocabulary_id, is_correct)
        conn.execute("INSERT INTO activity_log (mode) VALUES ('srs')")
        conn.commit()

        return SrsAnswerResponse(
            is_correct=is_correct,
            correct_answer=correct_answer,
            next_due_at=next_due_at,
        )
    finally:
        conn.close()
