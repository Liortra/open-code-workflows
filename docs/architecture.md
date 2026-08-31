# Architecture — Hebrew Language Tutor

Technical specification for implementation. Backend and frontend engineers
should be able to build independently from this document without guessing at
contracts.

## 1. Overview

A single-process FastAPI app serves both a JSON API and a static, multi-page
Bootstrap frontend (no SPA framework, no build step, per
`environment-notes.md`). Persistence is SQLite via the stdlib `sqlite3`
module (no ORM). Text-to-speech is entirely client-side via the browser's
`SpeechSynthesis` API and has no backend surface.

```
Browser (static HTML/CSS/JS + Bootstrap CDN)
   │  fetch() → JSON
   ▼
FastAPI app (single process, uvicorn)
   │  sqlite3
   ▼
backend/data/app.db
```

## 2. Project / File Structure

```
backend/
├── main.py                 # FastAPI() instance ("app"), mounts routers + static frontend
├── database.py              # connection helper, schema creation, seeding on startup
├── seed_data.py              # the 20 starting lessons × 10 vocab items, as plain data
├── schemas.py                # Pydantic request/response models
├── quiz_logic.py              # shared question/distractor generation (used by quiz + exam routers)
├── routers/
│   ├── lessons.py             # GET /api/lessons, GET /api/lessons/{id}
│   ├── study.py                # GET /api/lessons/{id}/vocabulary
│   ├── quiz.py                 # GET /api/lessons/{id}/quiz, POST /api/lessons/{id}/quiz/check
│   ├── exam.py                  # GET/POST /api/lessons/{id}/exam..., GET .../exam/history
│   └── admin.py                  # POST /api/admin/lessons, POST /api/admin/vocabulary
└── data/
    └── app.db                    # SQLite file, created on first run (gitignored)

frontend/
├── index.html                 # Lesson Catalog
├── lesson.html                 # Lesson screen: choose Study / Quiz / Exam, shows exam history
├── study.html
├── quiz.html
├── exam.html
├── admin.html
└── static/
    ├── css/
    │   └── app.css               # small overrides on top of Bootstrap
    └── js/
        ├── api.js                  # fetch() wrappers for every endpoint below
        ├── tts.js                   # SpeechSynthesis wrapper (speak/cancel-on-new-request)
        ├── catalog.js
        ├── lesson.js
        ├── study.js
        ├── quiz.js
        ├── exam.js
        └── admin.js
```

`backend/main.py` mounts `frontend/` as static files (`StaticFiles`) at `/`,
and the API routers under `/api`. This satisfies `run.sh`'s
`backend.main:app` import target and the single-process serving model from
`environment-notes.md`.

## 3. Module Boundaries

- **`database.py`** owns the SQLite connection, schema creation
  (`CREATE TABLE IF NOT EXISTS ...`), and first-run seeding. No router opens
  its own connection logic — all go through this module.
- **`seed_data.py`** is pure data (20 lessons, 10 vocab items each). It has
  no behavior; `database.py` reads it once, on first run, when `lessons` is
  empty.
- **`quiz_logic.py`** is the single place that builds a multiple-choice
  question (prompt + 4 choices + which choice is correct) for a vocabulary
  item, including distractor selection. Both `quiz.py` and `exam.py` call
  into it so the two modes can never diverge in how questions are built.
- **Routers** are thin: parse/validate the request, call `database.py` /
  `quiz_logic.py`, return a `schemas.py` model. No SQL or question-building
  logic lives in a router body directly beyond simple `SELECT`s.
- **Frontend JS modules** are one per screen (`catalog.js`, `study.js`,
  etc.), each responsible only for its own page's DOM and API calls.
  `api.js` is the sole place that knows endpoint URLs/payload shapes;
  `tts.js` is the sole place that touches `SpeechSynthesis`.

## 4. Data Model / SQLite Schema

```sql
CREATE TABLE lessons (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE vocabulary (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_id  INTEGER NOT NULL REFERENCES lessons(id),
    hebrew     TEXT NOT NULL,
    meaning    TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE exam_attempts (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_id  INTEGER NOT NULL REFERENCES lessons(id),
    score      INTEGER NOT NULL,
    total      INTEGER NOT NULL,
    taken_at   TEXT NOT NULL DEFAULT (datetime('now'))
);
```

Notes:

- No `quiz_attempts` table: Quiz mode is explicitly not persisted (brief
  `03-quiz-mode.md`, constraint: "Quiz results are not persisted/saved
  anywhere"). Quiz state lives only in the browser for the duration of one
  attempt.
- `exam_attempts` stores only `(lesson_id, score, total, taken_at)`. The
  per-question right/wrong review required by `04-exam-mode.md` step 5 is
  computed and returned once, in the submission response — it is not
  persisted, because the brief only requires past *scores* to remain
  viewable ("view past exam results ... e.g. most recent score, or a
  history of attempts"), not a replayable review of a past attempt.
- A vocabulary item belongs to exactly one lesson (`lesson_id NOT NULL`,
  single FK) per `05-admin-content-management.md`'s constraint that "a
  vocabulary item must belong to exactly one lesson."
- No `users`/auth tables — the app is single-user/no-login per the concept
  and `environment-notes.md`.
- SQLite file lives at `backend/data/app.db`, created by `database.py` on
  first run if absent. Already covered by the `*.db` entry in `.gitignore`.

## 5. Question Generation (shared by Quiz and Exam)

Decision: every question prompts with the **Hebrew word** and asks the user
to pick the correct **meaning** from 4 choices (1 correct + 3 distractors).
This direction is fixed and consistent across Quiz and Exam (the briefs
leave the exact direction open; this is the architecture's resolution of
that open point).

Distractor selection, per question, for vocabulary item `v` in lesson `L`:

1. Pull up to 3 other vocabulary items from `L` (excluding `v`) and use
   their `meaning` values as distractors.
2. If `L` has fewer than 4 total items (only reachable for a lesson created
   via Admin that hasn't yet had 3+ more items added), fill the remaining
   distractor slots with `meaning` values drawn at random from vocabulary in
   *other* lessons.
3. Shuffle the 4 choices (1 correct meaning + distractors) before returning
   them, so the correct answer isn't always in the same position.

This logic lives once in `quiz_logic.py` and is reused by both `quiz.py` and
`exam.py`, so both modes always cover all of the lesson's vocabulary and
never expose the correct answer ahead of time in the payload for a
not-yet-answered question.

## 6. API Contracts

All endpoints are under `/api`, return JSON, and use standard HTTP status
codes (`404` for an unknown `lesson_id`/`vocabulary_id`, `422` for
validation failures via FastAPI/Pydantic).

### Lessons / Catalog

**`GET /api/lessons`**
Response `200`:
```json
[
  { "id": 1, "title": "Greetings", "vocabulary_count": 10 }
]
```

**`GET /api/lessons/{lesson_id}`**
Response `200`:
```json
{
  "id": 1,
  "title": "Greetings",
  "vocabulary_count": 10,
  "has_exam_history": true
}
```
`has_exam_history` lets the lesson screen show "an exam result exists"
(`04-exam-mode.md` step 8) without a second round trip.

### Study

**`GET /api/lessons/{lesson_id}/vocabulary`**
Response `200`:
```json
[
  { "id": 11, "hebrew": "שלום", "meaning": "hello" }
]
```
Word and meaning are returned together, per `02-study-mode.md` ("no
guessing or answering is required").

### Quiz (stateless — nothing persisted)

**`GET /api/lessons/{lesson_id}/quiz`**
Response `200`: one question per vocabulary item in the lesson, in random
order. Correct answer is **not** included.
```json
[
  {
    "vocabulary_id": 11,
    "prompt": "שלום",
    "choices": ["hello", "goodbye", "please", "thank you"]
  }
]
```

**`POST /api/lessons/{lesson_id}/quiz/check`**
Request:
```json
{ "vocabulary_id": 11, "selected": "goodbye" }
```
Response `200`:
```json
{ "is_correct": false, "correct_answer": "hello" }
```
Immediate per-question feedback (`03-quiz-mode.md` step 3). The frontend
tallies the end-of-quiz score itself from the `check` responses it already
received — no separate summary endpoint or server-side quiz state is
needed, consistent with Quiz results not being persisted.

### Exam (feedback withheld until submit; result persisted)

**`GET /api/lessons/{lesson_id}/exam`**
Same shape as the quiz question list — one question per vocabulary item,
correct answer not included.

**`POST /api/lessons/{lesson_id}/exam/submit`**
Request — all of the lesson's vocabulary items must be present, or `422`:
```json
{
  "answers": [
    { "vocabulary_id": 11, "selected": "hello" }
  ]
}
```
Response `200`:
```json
{
  "score": 8,
  "total": 10,
  "taken_at": "2026-08-31T12:00:00",
  "review": [
    {
      "vocabulary_id": 11,
      "prompt": "שלום",
      "selected": "hello",
      "correct_answer": "hello",
      "is_correct": true
    }
  ]
}
```
Persists one row to `exam_attempts`. `review` is computed for this response
only and is not stored (see §4).

**`GET /api/lessons/{lesson_id}/exam/history`**
Response `200`, most recent first:
```json
[
  { "id": 5, "score": 8, "total": 10, "taken_at": "2026-08-31T12:00:00" }
]
```

### Admin (add-only, per `05-admin-content-management.md`)

**`POST /api/admin/lessons`**
Request: `{ "title": "Food" }`
Response `201`: `{ "id": 21, "title": "Food", "vocabulary_count": 0 }`

**`POST /api/admin/vocabulary`**
Request: `{ "lesson_id": 21, "hebrew": "לחם", "meaning": "bread" }`
Response `201`: `{ "id": 211, "lesson_id": 21, "hebrew": "לחם", "meaning": "bread" }`
`404` if `lesson_id` doesn't exist.

No update/delete endpoints exist anywhere in this API — Admin is strictly
additive, matching the brief's constraint.

## 7. Backend Responsibilities

- Own all persistence (SQLite) and be the sole source of truth for lesson
  and vocabulary content.
- Build multiple-choice questions (prompt, choices, distractor selection)
  — the frontend never invents choices or shuffles them itself.
- Enforce that an exam submission covers all of a lesson's vocabulary
  (reject incomplete submissions) and persist every exam attempt.
- Seed the 20 starting lessons / 10 vocab items each on first run
  (`seed_data.py`, applied by `database.py` when `lessons` is empty), so a
  fresh checkout is immediately usable without a manual data-loading step.
- Serve the static frontend files (single process, per
  `environment-notes.md`).
- Never touch text-to-speech — that is 100% client-side.

## 8. Frontend Responsibilities

- Render the Lesson Catalog, lesson screen, and each mode (Study/Quiz/Exam)
  as separate static pages, navigating via normal links/`fetch` calls — no
  SPA router, no build step.
- Study mode: fetch and display all vocabulary for a lesson with word +
  meaning shown together; never hide/quiz.
- Quiz mode: fetch questions, submit each answer to `/quiz/check` as the
  user answers, show immediate feedback, tally and display the final score
  itself from the responses it collected. Allow re-entering Quiz mode
  freely (no state to reset server-side).
- Exam mode: fetch questions, collect all answers client-side, block
  submission until every question is answered, `POST` once to
  `/exam/submit`, then render the returned score + review. Fetch
  `/exam/history` on the lesson screen to show past results.
- Admin: forms for "add lesson" and "add vocabulary" (with a lesson
  picker sourced from `GET /api/lessons`), posting to the two admin
  endpoints; no edit/delete UI.
- Text-to-speech (`tts.js`): wrap `window.speechSynthesis`, cancel any
  in-flight utterance before starting a new one (per
  `06-text-to-speech.md`'s "does not stack or overlap audio"), and
  disable/hide the control gracefully if `speechSynthesis` is unavailable
  without blocking any other feature.

## 9. Component Interaction / State Flow

```
Catalog (GET /api/lessons)
   │ select lesson
   ▼
Lesson screen (GET /api/lessons/{id})
   │
   ├─ Study  → GET .../vocabulary                (no state produced)
   ├─ Quiz   → GET .../quiz  → per-answer POST .../quiz/check   (ephemeral, client-tallied)
   └─ Exam   → GET .../exam  → POST .../exam/submit  → persisted exam_attempts row
                  lesson screen also: GET .../exam/history
Admin → POST /api/admin/lessons | POST /api/admin/vocabulary
   → next GET /api/lessons / GET .../vocabulary calls see the new data immediately
     (no cache, no separate publish step — satisfies 05-admin-content-management.md)
```

All application state that must outlive a single page view (lesson
catalog, vocabulary, exam history) lives in SQLite and is re-fetched by the
frontend; the frontend holds no state beyond the current page/in-progress
quiz or exam answers in memory.

## 10. Deviations From the Approved Environment

None. `requirements.txt` (`fastapi`, `uvicorn[standard]`) is sufficient —
no ORM, no additional packages required by this architecture.
