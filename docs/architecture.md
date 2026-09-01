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

---

## 11. Enhancement: Sprint 01 — Study Aids & Progress Tracking

**Added by Stage 5 (Architect) of the enhancement pipeline.** This section
extends, and does not replace, sections 1–10 above. It covers the four
features agreed in `enhancements/scope.md` and detailed in
`features/briefs/01-english-text-to-speech.md`,
`features/briefs/02-spaced-repetition.md`,
`features/briefs/03-progress-dashboard.md`, and
`features/briefs/04-nikud-toggle.md`. Stage 4 confirmed no environment
changes are needed for any of the four (`instructions/enhancements/summaries/04-system-engineering.md`):
everything below stays within the existing stack (FastAPI + stdlib
`sqlite3`, static HTML/JS + Bootstrap, client-side `SpeechSynthesis`).

Five cross-cutting design decisions were confirmed with the coordinator
before this section was written; each is called out inline below where it
applies.

### 11.1 Feature → surface summary

| Feature | New backend surface | New frontend surface | New persistence |
|---|---|---|---|
| a. English TTS | none (client-only) | `tts.js` generalized to speak either language; Study mode + Exam review get a second speaker control | none |
| b. Spaced Repetition | `routers/srs.py` (2 endpoints) | `srs.html` / `srs.js` ("Due for Review", nav entry point) | `word_review_state` table |
| c. Progress Dashboard | `routers/dashboard.py`, `routers/activity.py` | `dashboard.html` / `dashboard.js` (new home-adjacent view) | `activity_log` table |
| d. Nikud Toggle | none (client-only) | `nikud.js` + a toggle control added to every page's navbar | none (browser `localStorage` only — **Decision 4**) |

### 11.2 Data Model / Schema Changes

Two new tables. `lessons`, `vocabulary`, and `exam_attempts` (§4) are
**unchanged** — no columns added, no existing rows touched.

```sql
CREATE TABLE IF NOT EXISTS word_review_state (
    vocabulary_id    INTEGER PRIMARY KEY REFERENCES vocabulary(id),
    interval_index   INTEGER NOT NULL,   -- 0-5, index into the day-ladder (see 11.3)
    last_result      TEXT NOT NULL,      -- 'correct' | 'incorrect'
    last_reviewed_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now')),
    next_due_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS activity_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    mode        TEXT NOT NULL,           -- 'study' | 'quiz' | 'srs'
    occurred_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now'))
);
```

Notes:

- A vocabulary item with **no** `word_review_state` row has never been
  reviewed and is therefore due (per SRS brief constraint: "a word with no
  review history yet ... is treated as due"). A row is created on that
  word's first SRS answer, never proactively for unseen words.
- `activity_log` never stores `mode = 'exam'`. Exam completions are
  already durably recorded in `exam_attempts.taken_at`; the streak
  calculation (§11.3) reads both tables rather than duplicating Exam data
  into `activity_log` — this is **Decision 1**'s "completion-timestamp
  only, no scores/answers" reading applied consistently: Exam already has
  its own completion timestamp, so nothing new is needed for it.
- Timestamp columns follow the existing convention in `database.py`
  (`strftime('%Y-%m-%dT%H:%M:%S', 'now')`, not `datetime('now')`), so all
  stored timestamps stay ISO-8601 with a `T` separator, comparable
  lexicographically and consistent with `exam_attempts.taken_at`.

### 11.3 SRS scheduling algorithm (Decision 2, precise transition rule)

Coordinator-approved day-ladder: `DAY_LADDER = [0, 1, 3, 7, 14, 30]`
(indices 0–5), "advance a step on correct recall, reset to 0 on
incorrect."

To satisfy the SRS brief's acceptance requirement that "a word marked as
recalled correctly does not immediately reappear in the same or next
review session," index 0 (0 days — i.e. due again immediately) must only
ever be reached via an **incorrect** answer, never as the result of a
correct one. The precise upsert rule for `POST /api/srs/{vocabulary_id}/answer`
(§11.4) is:

- **Incorrect answer:** `interval_index = 0`, `last_result = 'incorrect'`,
  `next_due_at = strftime('%Y-%m-%dT%H:%M:%S', 'now')` (due immediately).
- **Correct answer:**
  - If no row exists yet (word's first-ever answer) or the answer follows
    a prior incorrect result: `interval_index = 1` (first correct answer
    always lands on the 1-day rung, never on 0).
  - If the prior answer for this word was also correct: `interval_index =
    min(previous_interval_index + 1, 5)`.
  - `last_result = 'correct'`,
    `next_due_at = strftime('%Y-%m-%dT%H:%M:%S', 'now', '+{DAY_LADDER[interval_index]} days')`.

Worked example for one word: never seen → due now. Answered correctly →
due in 1 day (index 1). Answered correctly again → due in 3 days (index
2). Answered incorrectly → due immediately again (index 0). Answered
correctly → due in 1 day (index 1, not 3 — the incorrect answer reset the
streak).

This logic lives in a new `backend/srs_logic.py`, mirroring how
`quiz_logic.py` is the single owner of question-building logic (§3).

### 11.4 API Contract Changes

All new endpoints are under `/api`, JSON in/out, same status-code
conventions as §6 (`404` for an unknown id, `422` for validation
failures).

#### English Text-to-Speech (a)

No new backend surface — entirely a `tts.js` change (§11.6). No new
endpoints, no schema changes.

#### Spaced Repetition (b)

**`GET /api/srs/due`**
Returns every currently-due item across all lessons (no pagination — the
brief allows "as many due items as are available in a session"; the
frontend steps through them one at a time client-side, the same pattern
`quiz.js` already uses for `GET /api/lessons/{id}/quiz`). Uses the same
question/distractor shape as Quiz/Exam (§5), built by reusing
`quiz_logic.py`'s per-item distractor selection (that helper is exposed —
renamed without its leading underscore, or extracted into a small shared
function both `quiz_logic.py` and `srs_logic.py` call — so SRS questions
are never built with a different distractor strategy than Quiz/Exam;
see §11.6 backend responsibilities).
```json
[
  {
    "vocabulary_id": 11,
    "lesson_id": 1,
    "prompt": "שלום",
    "choices": ["hello", "goodbye", "please", "thank you"]
  }
]
```
Empty array `[]` when nothing is due — the frontend renders the "nothing
to review right now" state (brief's basic acceptance expectation) on an
empty response rather than a special status code.

**`POST /api/srs/{vocabulary_id}/answer`**
Request:
```json
{ "selected": "goodbye" }
```
`404` if `vocabulary_id` doesn't exist. Response `200`:
```json
{ "is_correct": false, "correct_answer": "hello", "next_due_at": "2026-09-02T10:00:00" }
```
Side effects (single request, single transaction): upserts
`word_review_state` per §11.3, **and** inserts one `activity_log` row
(`mode = 'srs'`) — per **Decision 1**, this endpoint is the SRS
completion signal; the frontend does not call the generic activity
endpoint separately for SRS.

#### Progress Dashboard (c) + shared activity log

**`POST /api/activity`**
Called by Study (once, when a lesson's vocabulary finishes loading) and
Quiz (once, when the end-of-quiz summary is reached) — the two modes that
have no other durable completion signal, per **Decision 1**. Exam and SRS
do **not** call this endpoint (they get their completion signal for free
from `exam_attempts` and the SRS answer endpoint above, respectively).
Request:
```json
{ "mode": "study" }
```
`mode` must be `"study"` or `"quiz"` (`422` otherwise — `"exam"` and
`"srs"` are valid *stored* values but are never accepted from this
endpoint, since those two modes log through their own existing/new
endpoints instead). Response `201`:
```json
{ "mode": "study", "occurred_at": "2026-09-01T10:00:00" }
```

**`GET /api/dashboard`**
Single aggregating read, re-fetched fresh every time the dashboard is
opened (no caching — same "no separate refresh step" pattern already used
for Admin's additions, §9).
```json
{
  "lessons": [
    { "lesson_id": 1, "title": "Greetings", "mastery_percent": 80 },
    { "lesson_id": 2, "title": "Numbers 1-10", "mastery_percent": null }
  ],
  "exam_history": [
    { "id": 5, "lesson_id": 1, "lesson_title": "Greetings", "score": 8, "total": 10, "taken_at": "2026-08-31T12:00:00" }
  ],
  "streak_days": 3
}
```
- `lessons`: every lesson in the catalog (including ones added later via
  Admin). `mastery_percent` = `round(100 * score / total)` from that
  lesson's most recent `exam_attempts` row (`ORDER BY taken_at DESC LIMIT
  1`); `null` when the lesson has no exam attempt yet — the frontend
  renders `null` as the brief's "not yet attempted" state, never a
  fabricated `0`.
- `exam_history`: **all** `exam_attempts` rows across all lessons
  (joined to `lessons.title`), most recent first — not just each lesson's
  latest, per the brief's "exam results across all lessons ... in one
  place."
- `streak_days`: computed from the distinct calendar dates present in
  `activity_log.occurred_at` (any mode) unioned with
  `exam_attempts.taken_at`, counting consecutive calendar days walking
  backward from today (or from the most recent qualifying day, if today
  has no activity yet), per the brief's day-streak definition already
  decided in `03-progress-dashboard.md`. Viewing the dashboard itself
  never writes to either table, so opening it cannot inflate the streak.

#### Nikud Toggle (d)

No new backend surface — entirely a `localStorage` + `nikud.js` change
(§11.6), per **Decision 4**. No new endpoints, no schema changes, no
change to how Hebrew text is stored or returned by any existing endpoint
(`vocabulary.hebrew` continues to be returned exactly as stored, fully
vocalized, by every existing endpoint — stripping is a display-time-only
transform applied in the browser).

### 11.5 Backend/Frontend Responsibility Changes

**Backend, in addition to §7:**
- Owns `word_review_state` and `activity_log` persistence and is the sole
  place that computes "is this word due" and "what is the current streak"
  — the frontend never computes due-ness or streak length itself, it only
  renders what `/api/srs/due` and `/api/dashboard` return (same
  server-owns-logic pattern as question generation in §7).
- Exposes (de-privatizes) `quiz_logic.py`'s distractor-selection helper so
  `srs_logic.py` can reuse it without duplicating the strategy.
- Still never touches text-to-speech and still never touches nikud
  display — both remain 100% client-side, now including English speech
  and nikud stripping, not just Hebrew speech.

**Frontend, in addition to §8:**
- `tts.js`: generalize the existing `speak(hebrewText)` /
  `createSpeakerButton(hebrewText)` into a `speak(text, lang)` /
  `createSpeakerButton(text, lang, labelPrefix)` pair (`lang` = `"he-IL"`
  or `"en-US"`), with the existing Hebrew call sites updated to pass
  `"he-IL"` explicitly and unchanged in every other respect. Because the
  existing `speak()` already calls `window.speechSynthesis.cancel()`
  before every utterance regardless of language, "only one utterance plays
  at a time across both languages" (English TTS brief, point 5) falls out
  of the existing implementation for free — no new interruption logic is
  needed.
  - `study.js`: adds a second (English) speaker button next to each
    item's meaning text, alongside the existing Hebrew one.
  - `exam.js`: adds a second (English) speaker button next to each
    review row's meaning (`correct_answer` — the item's actual meaning,
    not necessarily what the learner selected), on the post-submit
    results screen.
  - Per **Decision 3**, `quiz.js`'s four answer-choice buttons and
    `exam.js`'s four pre-submit answer-choice radios do **not** get a
    per-choice English control — only Study mode and the Exam review list
    do.
- `srs.js` / `srs.html` (new): fetches `GET /api/srs/due`, steps through
  items one at a time client-side (same UX shape as `quiz.js`), posts each
  answer to `POST /api/srs/{vocabulary_id}/answer`, shows immediate
  correct/incorrect feedback (mirroring Quiz's per-question feedback per
  the brief), and shows a clear "nothing due right now" state when the due
  list is empty. Reachable from a new "Review" nav-bar link added to every
  existing page's navbar (§11.6), independent of any lesson screen.
- `dashboard.js` / `dashboard.html` (new): fetches `GET /api/dashboard` on
  load and renders per-lesson mastery, cross-lesson exam history, and the
  streak count. Reachable from a new "Dashboard" nav-bar link added to
  every existing page's navbar. Per the brief's "alongside ... the
  existing Lesson Catalog entry point" option, `index.html` (Catalog)
  keeps serving as today's `/` default (`StaticFiles(html=True)` in
  `backend/main.py` is unchanged) — Dashboard is an added, separately
  reachable view, not a replacement for `/`.
- `study.js`: after vocabulary loads successfully, fire-and-forget
  `POST /api/activity {mode: "study"}` once per page load.
- `quiz.js`: when `showSummary()` runs (all questions answered), fire-and-
  forget `POST /api/activity {mode: "quiz"}` once per completed quiz.
- `nikud.js` (new): owns `localStorage["nikud_hidden"]` (**Decision 4**),
  exposes a strip function for the documented Unicode range (Hebrew points
  /  accents, `U+0591`–`U+05C7`, per `instructions/enhancements/summaries/04-system-engineering.md`'s
  reasoning), and wires a toggle control added to every page's navbar.
  Every place Hebrew text is rendered into the DOM (`study.js`, `quiz.js`
  prompt, `exam.js` prompt and review rows, `admin.js`'s lesson-picker if
  it ever shows Hebrew, any future Hebrew display in `catalog.js`/
  `lesson.js`) sets the element's original, fully-vocalized text on a
  `data-hebrew` attribute and lets `nikud.js` set the element's visible
  `textContent` from that attribute according to the current toggle
  state. On toggle change, `nikud.js` re-applies itself to every
  `[data-hebrew]` element currently in the DOM, satisfying "takes effect
  ... for Hebrew text currently on screen ... without requiring a reload."
  Per **Decision 5**, the Admin "Add Vocabulary" Hebrew `<input>` is
  **not** wrapped this way and is always unaffected by the toggle — it
  shows exactly what the admin types, at all times. (Admin has no
  read-only Hebrew listing today; when one is added, it would follow the
  `data-hebrew` convention like every other display.)

### 11.6 Component Interaction / State-Flow Changes

```
Home (/ → index.html, unchanged Catalog)          "Dashboard" nav-link        "Review" nav-link
   │                                                       │                          │
   ▼                                                       ▼                          ▼
Lesson screen (unchanged) ──▶ Study/Quiz/Exam      dashboard.html            srs.html
   │  Study  → GET vocabulary                      GET /api/dashboard       GET /api/srs/due
   │            + POST /api/activity {study}          │                        │ per item:
   │  Quiz   → existing flow                          │                        ▼
   │            + POST /api/activity {quiz}            (reads exam_attempts   POST /api/srs/{id}/answer
   │              (fired once, at summary)              + activity_log,        → upserts word_review_state
   └─ Exam   → existing flow, unchanged                 no writes)             → inserts activity_log{srs}
                (exam_attempts row is the
                 completion signal — no
                 activity_log write)

Every page's navbar (all *.html): existing "Admin" link, plus new
"Dashboard" and "Review" links, plus a nikud show/hide toggle
(localStorage-backed, no server round trip).
```

`word_review_state` and `activity_log` are written only by the two new
endpoints described above (`/api/srs/{id}/answer` and `/api/activity`)
plus Exam's existing submit flow (which continues to write only
`exam_attempts`, unchanged). `GET /api/dashboard` and `GET /api/srs/due`
are pure reads; opening either view produces no write.

### 11.7 Explicitly Unchanged / Out of Scope

- The v0.1 data model (`lessons`, `vocabulary`, `exam_attempts`) is
  unchanged — no columns added, no rows migrated.
- Lesson Catalog, Study mode's vocabulary listing, Quiz mode's
  stateless per-question flow, Exam mode's question generation /
  submission / persisted history, and all Admin add-only endpoints are
  unchanged in behavior and contract (§6–§9 remain accurate as written).
- Quiz mode remains fully unpersisted with respect to **results**: no
  score, answer, or per-question data is ever written anywhere for Quiz.
  The one addition (`activity_log {mode: "quiz"}`) is a bare
  completion timestamp with no result data, per **Decision 1**'s reading
  of the existing "Quiz results are not persisted" constraint.
  Existing Exam behavior (`exam_attempts`, `/exam/history`) is untouched;
  SRS reads/writes only its own `word_review_state` table, never Exam or
  Quiz data, per `02-spaced-repetition.md`'s constraint.
- Hebrew pronunciation (`tts.js`'s existing Hebrew path) is functionally
  identical; only its internals are generalized to also support English.
- No new dependency, package, service, or environment change — everything
  above is stdlib `sqlite3` + existing FastAPI/Bootstrap/`SpeechSynthesis`,
  consistent with Stage 4's confirmation
  (`instructions/enhancements/summaries/04-system-engineering.md`).
- No authentication/login is introduced; the app remains single-user.
- Nikud stripping never touches stored data — `vocabulary.hebrew` is
  never rewritten, and every existing endpoint keeps returning the
  fully-vocalized text exactly as stored; hiding nikud is a client-side
  render-time transform only.
