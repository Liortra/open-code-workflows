# Hebrew Language Tutor

A simple Hebrew vocabulary learning web app. Browse a catalog of lessons,
review vocabulary in Study mode, practice with low-stakes Quizzes, take a
scored and recorded Exam per lesson, hear any word pronounced via
text-to-speech, and add new lessons/vocabulary through an Admin section.

Built as a single FastAPI process serving both a JSON API and a static,
multi-page Bootstrap frontend (no separate frontend server, no build step).

## Features

- **Lesson Catalog** — browse all lessons (starts with 20 lessons, 10
  vocabulary items each) and jump into any of them.
- **Study Mode** — review a lesson's vocabulary (Hebrew word + meaning shown
  together) at your own pace, with no grading.
- **Quiz Mode** — multiple-choice practice with immediate per-question
  feedback and an end-of-quiz score. Retakeable without limit; attempts are
  never saved.
- **Exam Mode** — multiple-choice assessment covering all 10 vocabulary items
  of a lesson. Feedback is withheld until you submit; the score (and a
  review of right/wrong answers) is shown afterward, and the score is saved
  permanently per lesson, viewable again later.
- **Admin** — add new lessons and new vocabulary items directly in the app
  (no code change needed); additions appear immediately in the catalog and
  in Study/Quiz/Exam. Adding is supported; editing/deleting existing content
  is not.
- **Text-to-Speech** — hear any Hebrew vocabulary word spoken aloud via the
  browser's built-in speech synthesis. No external API, no pre-recorded
  audio files.

There is no login — the app is single-user, and Admin is an unrestricted
section of the app rather than a separate authenticated role.

## Stack

- **Backend:** Python 3.13, FastAPI, served by Uvicorn.
- **Persistence:** SQLite via the standard-library `sqlite3` module (no ORM).
- **Frontend:** Static HTML/CSS/JS, styled with Bootstrap 5.3.3 loaded from a
  CDN (no npm/Node.js, no build step).

See `docs/architecture.md` for the full technical specification (file
layout, database schema, and API contract).

## Setup

Requires Python 3.13 on `PATH` as `python3.13` (override with the
`PYTHON_BIN` env var), and internet access at runtime for the Bootstrap CDN.

```bash
./install.sh
```

This creates a `.venv` virtual environment and installs the dependencies in
`requirements.txt`.

## Running

```bash
./run.sh
```

Starts the app with `uvicorn backend.main:app --reload` on `0.0.0.0:8000`
(override with `HOST`/`PORT` env vars). Open `http://localhost:8000` in a
browser. The SQLite database (`backend/data/app.db`) is created and seeded
with the starting 20 lessons × 10 vocabulary items automatically on first
run if empty.

## Implementation Summary

The app was built through a staged pipeline (concept → features → briefs →
environment → architecture → backend → frontend), documented stage-by-stage
in `summaries/`.

- **Backend** (`backend/`): a single FastAPI app with one thin router per
  feature area (`lessons`, `study`, `quiz`, `exam`, `admin`), a `sqlite3`
  persistence layer with three tables (`lessons`, `vocabulary`,
  `exam_attempts`), and a shared question-generation module
  (`quiz_logic.py`) used by both Quiz and Exam. Quiz questions ask for a
  vocabulary item's meaning given its Hebrew word, with distractors drawn
  from the same lesson (falling back to other lessons if a lesson has fewer
  than 4 items). Quiz is stateless server-side (a `check` endpoint gives
  per-question feedback; the frontend tallies the final score). Exam scores
  are persisted to `exam_attempts`; the per-question review is computed and
  returned once at submission time, not stored.
- **Frontend** (`frontend/`): six static Bootstrap pages (catalog, lesson,
  study, quiz, exam, admin), each with its own JS module, plus `api.js` as
  the sole owner of endpoint URLs/payload shapes and `tts.js` as the sole
  wrapper around the browser's `SpeechSynthesis` API. Admin-authored
  free-text content is HTML-escaped before being rendered elsewhere in the
  app.
- **Seed content**: the 20 starting lessons and 200 vocabulary items
  (`backend/seed_data.py`) are original, backend-authored Hebrew/English
  pairs across 20 themes (Greetings, Numbers, Colors, Family, Food, Animals,
  etc.), not linguistically reviewed — see "Known Issues" below.

## Project Status

All 9 stages of the build pipeline are complete and committed: concept,
feature decomposition, feature briefs, environment setup, architecture,
backend, frontend, verification, and this documentation pass.

## Verification Results

Stage 8 (`docs/verification-report.md`) derived a 32-item checklist from
`concept.md`, `features/briefs/*.md`, and `docs/architecture.md`, covering
Lesson Catalog, Study, Quiz, Exam, Admin, Text-to-Speech, and cross-cutting
concerns (single-process static serving, HTML/JS element-ID consistency,
XSS-safe rendering of user/admin-entered text).

**32/32 checks passed. No failures.**

- Backend behavior was verified live via `curl` against the app started with
  `install.sh` + `run.sh`, exercising every documented endpoint including
  edge cases: 404s on unknown lesson/vocabulary ids, 422s on incomplete exam
  submission and invalid admin payloads, 405s confirming no edit/delete
  surface exists, and the low-vocabulary-count distractor fallback for a
  freshly Admin-created lesson.
- Frontend behavior was verified by **static review** of every HTML page and
  its paired JS module against the briefs (including a cross-check that
  every `document.getElementById` lookup resolves to an actual element ID),
  not by browser automation — see "Known Issues" below.

## Known Issues

- **Frontend was not exercised in an actual browser during Stage 8.**
  Stage 7 (frontend engineering) did run headless-Chrome interaction tests
  as part of building the frontend, but Stage 8's independent verification
  pass covered the frontend by static code review only (reading HTML/JS
  against the briefs), not by clicking through the app or hearing TTS audio
  itself. No rendered-layout or live-interaction claim is made by Stage 8
  beyond that static review.
- **Seed vocabulary is unreviewed.** The 200 starting Hebrew/English word
  pairs are original content authored by the backend engineering stage as a
  plausible starting dataset, not verified for linguistic accuracy. Treat as
  a placeholder if translation correctness matters.
- **No favicon.** Requesting `/favicon.ico` returns an unstyled 404 in the
  browser console; cosmetic only, not part of any brief or the architecture.
- **No pass/fail threshold on Exam mode** — by design, per
  `features/briefs/04-exam-mode.md`: only the score is shown and saved, not
  judged against a threshold.
- **Working-tree state predating this pipeline run**: at the start of Stage
  4, `LICENSE`, the prior `README.md`, and `concept-examples/*` were already
  deleted in the working tree (unstaged), and were left untouched by every
  subsequent stage as out of scope (see `summaries/04-system-engineering.md`).
  That state is unrelated to the app itself but is flagged here in case it
  needs separate attention.

## Next Actions

- Exercise the frontend with real browser/interaction testing (clicking
  through Study/Quiz/Exam/Admin, confirming rendered layout, hearing TTS
  audio) to close the gap left by Stage 8's static-only frontend review.
- Have a human review the seed vocabulary (`backend/seed_data.py`) for
  translation accuracy if the app will be used for real learning rather than
  as a demo.
- Resolve the pre-existing working-tree deletions noted above
  (`LICENSE`, prior `README.md`, `concept-examples/*`) — decide whether they
  should be restored, committed as intentional removals, or are unrelated
  cleanup from before this pipeline run.
- Consider whether Admin should eventually support editing/deleting content,
  and whether pass/fail thresholds or Quiz-attempt history are wanted — both
  were explicitly scoped out by the feature briefs (Stage 3) and would need
  a new pass through the pipeline (starting at feature decomposition) rather
  than an ad hoc change.
