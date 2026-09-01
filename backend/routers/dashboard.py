"""Progress Dashboard aggregating read, per docs/architecture.md §11.4.

Single read-only endpoint, re-fetched fresh every time the dashboard is
opened -- no caching, no writes. `word_review_state`/`activity_log` are
written only by the SRS and activity endpoints (and `exam_attempts` by the
existing Exam submit flow); this module never writes.
"""

from datetime import date, timedelta

from fastapi import APIRouter

from .. import database
from ..schemas import DashboardExamHistoryItem, DashboardLessonItem, DashboardResponse

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
def get_dashboard():
    conn = database.get_connection()
    try:
        lessons = []
        for row in conn.execute("SELECT id, title FROM lessons ORDER BY id").fetchall():
            latest = conn.execute(
                """
                SELECT score, total FROM exam_attempts
                WHERE lesson_id = ?
                ORDER BY taken_at DESC, id DESC LIMIT 1
                """,
                (row["id"],),
            ).fetchone()
            mastery_percent = (
                round(100 * latest["score"] / latest["total"]) if latest else None
            )
            lessons.append(
                DashboardLessonItem(
                    lesson_id=row["id"],
                    title=row["title"],
                    mastery_percent=mastery_percent,
                )
            )

        exam_history = [
            DashboardExamHistoryItem(
                id=r["id"],
                lesson_id=r["lesson_id"],
                lesson_title=r["title"],
                score=r["score"],
                total=r["total"],
                taken_at=r["taken_at"],
            )
            for r in conn.execute(
                """
                SELECT e.id, e.lesson_id, l.title, e.score, e.total, e.taken_at
                FROM exam_attempts e
                JOIN lessons l ON l.id = e.lesson_id
                ORDER BY e.taken_at DESC, e.id DESC
                """
            ).fetchall()
        ]

        streak_days = _compute_streak(conn)

        return DashboardResponse(
            lessons=lessons, exam_history=exam_history, streak_days=streak_days
        )
    finally:
        conn.close()


def _compute_streak(conn) -> int:
    """Consecutive calendar days (activity_log ∪ exam_attempts), per §11.4.

    Walks backward from today, or from the most recent qualifying day if
    today has no activity yet. Calendar days are derived from the same
    `strftime(..., 'now')`-based timestamps already used throughout the
    schema, so "today" is that same clock's notion of the current date.
    """
    dates = {
        r["d"]
        for r in conn.execute(
            "SELECT DISTINCT substr(occurred_at, 1, 10) AS d FROM activity_log"
        ).fetchall()
    }
    dates |= {
        r["d"]
        for r in conn.execute(
            "SELECT DISTINCT substr(taken_at, 1, 10) AS d FROM exam_attempts"
        ).fetchall()
    }
    if not dates:
        return 0

    today_str = conn.execute("SELECT strftime('%Y-%m-%d', 'now')").fetchone()[0]
    cursor_date = (
        date.fromisoformat(today_str)
        if today_str in dates
        else date.fromisoformat(max(dates))
    )

    streak = 0
    while cursor_date.isoformat() in dates:
        streak += 1
        cursor_date -= timedelta(days=1)
    return streak
