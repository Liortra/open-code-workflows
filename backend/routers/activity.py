"""Generic activity-completion logging, per docs/architecture.md §11.4.

Called by Study (once vocabulary finishes loading) and Quiz (once the
end-of-quiz summary is reached) -- the two modes with no other durable
completion signal. Exam and SRS do not call this endpoint; they get their
completion signal for free from `exam_attempts` and the SRS answer endpoint
respectively.
"""

from fastapi import APIRouter

from .. import database
from ..schemas import ActivityRequest, ActivityResponse

router = APIRouter(prefix="/api/activity", tags=["activity"])


@router.post("", response_model=ActivityResponse, status_code=201)
def log_activity(payload: ActivityRequest):
    conn = database.get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO activity_log (mode) VALUES (?)", (payload.mode,)
        )
        conn.commit()
        occurred_at = conn.execute(
            "SELECT occurred_at FROM activity_log WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()["occurred_at"]
        return ActivityResponse(mode=payload.mode, occurred_at=occurred_at)
    finally:
        conn.close()
