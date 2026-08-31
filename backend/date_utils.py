"""Rolling 7-day window computation.

Per docs/architecture.md §6: this is the single place that computes "today
through 6 days from now" and validates whether a given date falls inside
that window. Both routers/meal_plan.py and routers/shopping_list.py call
into this module so the two features can never disagree about what "the
coming week" means. Uses the server's local date with no timezone handling,
consistent with the single-user, local-development-only scope in
environment-notes.md.
"""

from __future__ import annotations

from datetime import date, timedelta

_WEEKDAY_NAMES = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

WINDOW_DAYS = 7


def get_window(today: date | None = None) -> list[tuple[str, str]]:
    """Return exactly 7 (ISO date string, weekday name) pairs: today through
    today + 6 days."""
    if today is None:
        today = date.today()
    result = []
    for offset in range(WINDOW_DAYS):
        d = today + timedelta(days=offset)
        result.append((d.isoformat(), _WEEKDAY_NAMES[d.weekday()]))
    return result


def in_window(iso_date: str, today: date | None = None) -> bool:
    """Return True if `iso_date` (an ISO 'YYYY-MM-DD' string) falls within
    the current rolling 7-day window (today through today + 6 days)."""
    if today is None:
        today = date.today()
    try:
        parsed = date.fromisoformat(iso_date)
    except (ValueError, TypeError):
        return False
    return today <= parsed <= today + timedelta(days=WINDOW_DAYS - 1)
