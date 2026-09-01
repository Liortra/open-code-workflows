# Summary: Backend Engineer (Stage 06)

- **Date:** 2026-09-01
- **Author / Executor:** Claude (Backend Engineer role)
- **Instruction file:** `instructions/enhancements/06-backend.md`
- **Scope reference:** `enhancements/scope.md`
- **Commit:** `stage 06: implement backend per architecture`

## Work Completed

Implemented the backend surface for all Sprint 01 features specified in
`docs/architecture.md` §11: Spaced Repetition (SRS) and the Progress
Dashboard's activity/streak tracking. English Text-to-Speech and the Nikud
toggle require no backend changes (both are 100% client-side per §11.4/§11.7)
and were left untouched.

Read `features/briefs/01–04-*.md`, `docs/architecture.md` (including §11),
the full existing backend (`main.py`, `database.py`, `quiz_logic.py`,
`schemas.py`, all four routers), and the environment definition
(`requirements.txt`, `install.sh`, `run.sh`, `environment-notes.md`) before
making changes.

Added two new tables (`word_review_state`, `activity_log`) to
`database.py`'s schema, a new `srs_logic.py` implementing the day-ladder
scheduling algorithm exactly as specified (including the correct/incorrect
transition rule that prevents a correct answer from ever landing on the
0-day rung), and three new routers (`srs.py`, `activity.py`,
`dashboard.py`) implementing the four new endpoints. De-privatized
`quiz_logic.py`'s distractor helper (`_distractors_for` → `distractors_for`)
so `srs_logic.py` reuses the exact same distractor strategy as Quiz/Exam,
per §11.5.

All new and existing endpoints were exercised end-to-end against a running
dev server (fresh seeded DB): `GET /api/srs/due` (200 seed words all due
when unreviewed), `POST /api/srs/{id}/answer` walked through the worked
example in §11.3 (correct → 1 day, correct → 3 days, incorrect → due now,
correct → 1 day again, confirming the streak-reset behaves exactly as
specified), `POST /api/activity` (accepts `study`/`quiz`, rejects
`exam`/`bogus` with 422), and `GET /api/dashboard` (correct mastery
percentage, `null` for unattempted lessons, cross-lesson exam history,
streak count). Existing v0.1 endpoints (`/api/lessons`, `/vocabulary`,
`/quiz`, `/quiz/check`, `/exam/history`, `/admin/lessons`) were re-verified
to still return `200`/`201` with unchanged behavior. The dev `app.db` used
for testing was deleted afterward (it is gitignored and not committed).

## Outputs Produced / Modified

- `backend/database.py` — added `word_review_state` and `activity_log`
  table definitions to `SCHEMA` (both `CREATE TABLE IF NOT EXISTS`,
  applied automatically by the existing `init_db()`). `lessons`,
  `vocabulary`, `exam_attempts` unchanged.
- `backend/quiz_logic.py` — renamed `_distractors_for` to `distractors_for`
  (de-privatized) and updated its one call site in `build_questions`; no
  behavior change to Quiz/Exam.
- `backend/schemas.py` — added `SrsDueItem`, `SrsAnswerRequest`,
  `SrsAnswerResponse`, `ActivityRequest`, `ActivityResponse`,
  `DashboardLessonItem`, `DashboardExamHistoryItem`, `DashboardResponse`.
  `ActivityRequest`/`ActivityResponse.mode` use `Literal["study", "quiz"]`
  so FastAPI/Pydantic rejects any other value with `422` automatically.
- `backend/srs_logic.py` (new) — `build_due_questions()` (due-item query +
  question building via `quiz_logic.distractors_for`) and `score_answer()`
  (the day-ladder upsert rule from §11.3). Mirrors `quiz_logic.py`'s role
  as the single owner of its domain's logic, reused by the router.
- `backend/routers/srs.py` (new) — `GET /api/srs/due`,
  `POST /api/srs/{vocabulary_id}/answer` (404 on unknown id; single
  transaction upserting `word_review_state` and inserting an
  `activity_log{mode:'srs'}` row).
- `backend/routers/activity.py` (new) — `POST /api/activity`.
- `backend/routers/dashboard.py` (new) — `GET /api/dashboard` (per-lesson
  mastery from most recent exam attempt, full cross-lesson exam history,
  streak computed from `activity_log ∪ exam_attempts` distinct calendar
  days).
- `backend/main.py` — registered the three new routers
  (`srs`, `activity`, `dashboard`) alongside the existing ones.
- `instructions/enhancements/summaries/06-backend.md` (this file, new).

## Key Decisions

Both were flagged as open (non-blocking) implementation judgment calls in
my Stage 6 pre-work review; resolved here as follows, per the "Undefined
seed / sample content" and general gap-filling guidance in
`06-backend.md`:

1. **Streak "calendar day" boundary.** §11.4 doesn't pin the streak's
   day-boundary to a timezone. Resolved by deriving calendar dates from
   the same `strftime(..., 'now')`-based clock already used for every
   timestamp column in the schema (`substr(occurred_at, 1, 10)` /
   `substr(taken_at, 1, 10)`), so "today" in the streak calculation is
   consistent with how `next_due_at`, `occurred_at`, and `taken_at` are
   all already computed. No new dependency; `date`/`timedelta` from the
   stdlib are used only for the backward-walk loop in
   `dashboard.py::_compute_streak`.
2. **De-privatizing the distractor helper.** §11.5 left the mechanism (
   rename in place vs. extract to a shared module) to Stage 6. Chose the
   simpler rename-in-place (`_distractors_for` → `distractors_for`) since
   `quiz_logic.py` already owns this logic per §5/§7 and SRS is just
   another caller of the same lesson-scoped strategy — no behavioral
   difference, `quiz.py`/`exam.py` are unaffected.

No contract deviations from `docs/architecture.md` §11.4: all four new
endpoints, their request/response shapes, and status codes match the
specification exactly, verified against a running server (see Work
Completed).

## Open Questions & Concerns

- None blocking. Frontend Engineer (Stage 7) should note: `GET
  /api/srs/due` and `GET /api/dashboard` are pure reads with no caching,
  matching the "reflects current data every time it's viewed" requirement
  in the Dashboard brief — no client-side cache-busting is needed, but
  none should be added either (a stale client cache would violate the
  "no separate refresh step" acceptance expectation).
- `word_review_state` and `activity_log` start empty on a fresh DB (no
  seed rows) — every vocabulary item is due on first run, consistent with
  the SRS brief's "a word with no review history yet is treated as due."
  This means Stage 8 (Verification) will see all 200 seed words in `GET
  /api/srs/due` on a clean checkout, which is expected, not a bug.
- Per Stage 5's summary, the seed Hebrew text contains no nikud
  characters, so nikud show/hide will be a visual no-op against seed
  content until Admin-entered nikud-bearing vocabulary exists. This is a
  frontend/verification concern only — no backend action was needed or
  taken (nikud remains entirely client-side, unchanged from `docs/architecture.md` §11.4/§11.7).

## Status

- [x] Complete
- [ ] Needs review
