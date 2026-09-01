# Summary: Backend Engineer (Stage 06)

- **Date:** 2026-08-31
- **Author / Executor:** Claude (agent)
- **Instruction file:** `instructions/build/06-backend.md`
- **Commit:** `stage 06: implement backend per architecture`

## Work Completed

Implemented the full backend under `backend/` exactly per `docs/architecture.md`:
a single FastAPI app with a thin-router layout, a `sqlite3`-based persistence
layer (no ORM), shared quiz/exam question-generation logic, and the complete
API contract from architecture §6 (lessons, study, quiz, exam, admin). The
database is created and seeded (20 lessons × 10 vocabulary items) on
startup if empty. Verified end-to-end against a live `uvicorn` instance:
catalog listing/detail, vocabulary retrieval, quiz question generation +
per-answer check, exam question generation + full-submission scoring +
history, admin add-lesson/add-vocabulary, and the 404/422 error paths all
behave as specified.

## Outputs Produced

- `backend/main.py` — FastAPI app, router registration, static-frontend mount, startup seeding via `lifespan`.
- `backend/database.py` — connection helper, schema (`CREATE TABLE IF NOT EXISTS`), `lesson_exists()`, first-run seeding.
- `backend/seed_data.py` — the 20 lessons × 10 vocabulary items as plain data (backend-authored content, see below).
- `backend/schemas.py` — Pydantic request/response models matching architecture §6 exactly.
- `backend/quiz_logic.py` — single shared `build_questions()` (with same-lesson-first, cross-lesson-fallback distractor selection and shuffling) used by both quiz and exam routers.
- `backend/routers/lessons.py`, `study.py`, `quiz.py`, `exam.py`, `admin.py` — one thin router per architecture's module boundaries.
- `summaries/06-backend.md` (this file).

No changes were made to `run.sh`, `install.sh`, or `requirements.txt` — the
`backend.main:app` import target already matches this layout, and no extra
dependencies were needed beyond `fastapi`/`uvicorn`.

## Key Decisions

- **Timestamp format resolution (minor gap):** `docs/architecture.md` §4's
  literal schema uses `DEFAULT (datetime('now'))`, which SQLite renders as
  `YYYY-MM-DD HH:MM:SS` (space-separated) — but §6's example responses show
  `taken_at` with a `T` separator (`"2026-08-31T12:00:00"`). Resolved by
  using `strftime('%Y-%m-%dT%H:%M:%S', 'now')` as the column default instead,
  so stored/returned timestamps match the documented API contract exactly.
  No API shape changed.
- **Backend-authored seed content:** the architecture specifies the *shape*
  (20 lessons, 10 vocabulary items each) but not the actual words. Authored
  20 themed lessons (Greetings, Numbers, Colors, Family, Food, Animals, Body
  Parts, Days of the Week, Time & Calendar, Weather, Clothing, House & Home,
  Transportation, Occupations, Emotions, Nature, School & Objects,
  Directions & Places, Common Verbs, Common Adjectives) with plausible
  Hebrew/English vocabulary pairs, avoiding duplicate Hebrew headwords across
  lessons where practical. Downstream roles should treat this content as a
  placeholder, not curated/verified translations.
- **Static frontend mount uses `check_dir=False`:** `frontend/` is Stage 7's
  output and doesn't exist yet. The mount is wired per the architecture
  (single-process serving, `/` → `frontend/`), but requests to `/` will 500
  ("StaticFiles directory ... does not exist") until Stage 7 creates
  `frontend/`. This does not affect any `/api/*` route, which are registered
  first and verified working standalone. Flagging so the frontend engineer
  knows the mount is already in place and just needs the directory to exist.
- Auth: not applicable — no contract in the briefs/architecture calls for an
  auth gate (single-user, no-login app), so no auth/token layer was added.

## Open Questions & Concerns

- The frontend engineer should create `frontend/` early in Stage 7 so the
  root `/` route stops 500ing (see above) — this is expected, not a bug.
- Seed vocabulary content (see "Backend-authored seed content" above) is
  original but not linguistically reviewed; flag for a human pass if
  translation accuracy matters beyond a demo/starting dataset.

## Status

- [x] Complete
- [ ] Needs review
