# Verification Report — Hebrew Language Tutor

- **Date:** 2026-08-31
- **Method:** Backend checked live via `curl` against the app started with
  `./install.sh` (already provisioned) + `./run.sh` (`uvicorn` on
  `localhost:8000`). Frontend checked via static review of
  `frontend/**/*.html` and `frontend/static/js/*.js` against the approved
  briefs and architecture — no headless/browser automation was used, so
  frontend JS execution and rendered layout were not exercised, only read.
- **Checklist derivation:** one checklist item per observable behavior stated
  in `concept.md`, `features/briefs/*.md`, and API/data contracts in
  `docs/architecture.md`.

## Summary

| Area | Checks | Pass | Fail |
|---|---|---|---|
| Lesson Catalog | 5 | 5 | 0 |
| Study Mode | 3 | 3 | 0 |
| Quiz Mode | 5 | 5 | 0 |
| Exam Mode | 7 | 7 | 0 |
| Admin | 6 | 6 | 0 |
| Text-to-Speech | 3 | 3 | 0 |
| Cross-cutting (static frontend serving, add-only API surface) | 3 | 3 | 0 |

**32/32 checks passed. No failures.**

## 1. Lesson Catalog (`01-lesson-catalog.md`)

| # | Check | Result | Evidence |
|---|---|---|---|
| 1.1 | Catalog returns all lessons on load | PASS | `GET /api/lessons` → 200, 20 items |
| 1.2 | Exactly the 20 starting lessons, 10 vocab each | PASS | Catalog response: 20 entries, `vocabulary_count: 10` on `id:1` ("Greetings") through `id:20` ("Common Adjectives") |
| 1.3 | Each lesson has an identifying title | PASS | Every catalog entry has a non-empty `title` |
| 1.4 | Selecting a lesson opens a lesson-level screen offering Study/Quiz/Exam | PASS (static) | `lesson.html` + `lesson.js` render `study-link`/`quiz-link`/`exam-link` from `GET /api/lessons/{id}` |
| 1.5 | A lesson added via Admin appears in the catalog without extra action | PASS | After `POST /api/admin/lessons {"title":"Food"}` → 201, next `GET /api/lessons` returned 21 items including the new lesson, no separate publish step |

## 2. Study Mode (`02-study-mode.md`)

| # | Check | Result | Evidence |
|---|---|---|---|
| 2.1 | Word + meaning shown together (never hidden/quizzed) | PASS | `GET /api/lessons/1/vocabulary` → each item has both `hebrew` and `meaning`; `study.js` renders both directly, no answer-hiding logic |
| 2.2 | All of a lesson's vocabulary is reachable, revisitable in any order | PASS (static) | `study.js` renders every returned vocabulary item as a card simultaneously (no pagination/locking) |
| 2.3 | Study mode produces no score/grade/history | PASS | `GET /api/lessons/{id}/vocabulary` is a plain read; no related mutation endpoint exists |

## 3. Quiz Mode (`03-quiz-mode.md`)

| # | Check | Result | Evidence |
|---|---|---|---|
| 3.1 | Quiz presents multiple-choice questions covering the lesson's vocabulary | PASS | `GET /api/lessons/1/quiz` → 10 questions, each with `prompt` + 4 `choices`, one per vocabulary item |
| 3.2 | Correct answer is not exposed before answering | PASS | Quiz question payload keys are only `vocabulary_id`, `prompt`, `choices` — no correct-answer field |
| 3.3 | Immediate per-question feedback (correct) | PASS | `POST /api/lessons/1/quiz/check {"vocabulary_id":1,"selected":"hello"}` → `{"is_correct":true,"correct_answer":"hello"}` |
| 3.4 | Immediate per-question feedback (incorrect, reveals correct answer) | PASS | Same endpoint with `"selected":"goodbye"` → `{"is_correct":false,"correct_answer":"hello"}` |
| 3.5 | End-of-quiz score shown; quiz retakeable; nothing persisted | PASS (static) | `quiz.js` tallies `correctCount` client-side from `/quiz/check` responses and shows it in `#summary-score`; `#retake-btn` re-invokes `startQuiz()`; no quiz-attempt table/endpoint exists anywhere in the API |

## 4. Exam Mode (`04-exam-mode.md`)

| # | Check | Result | Evidence |
|---|---|---|---|
| 4.1 | Exam covers all 10 vocabulary items of the lesson | PASS | `GET /api/lessons/1/exam` → 10 questions |
| 4.2 | No per-question feedback while answering | PASS (static) | `exam.js` only records selections into `selectedAnswers`; no per-question check call exists client- or server-side for exam |
| 4.3 | Submission blocked until all questions answered | PASS | `POST /api/lessons/1/exam/submit` with only 1 of 10 answers → `422`; `exam.js` also disables `#submit-btn` until `selectedAnswers.size === questions.length` |
| 4.4 | Full submission returns score + per-question review | PASS | Full 10-answer submission → `{"score":10,"total":10,"taken_at":"2026-08-31T15:24:37","review":[...10 items with is_correct...]}` |
| 4.5 | Result is persisted and remains viewable | PASS | `GET /api/lessons/1/exam/history` after submit → returns the saved attempt `{"id":1,"score":10,"total":10,"taken_at":...}` |
| 4.6 | Lesson screen reflects that an exam result exists | PASS | `GET /api/lessons/1` before any submit → `"has_exam_history":false`; after submit → `"has_exam_history":true` |
| 4.7 | Retaking produces a new saved result, most-recent-first, old result kept | PASS | Second submission (score 9/10) → history now `[{"id":2,"score":9,...}, {"id":1,"score":10,...}]`, ordered newest first, both retained |

## 5. Admin Content Management (`05-admin-content-management.md`)

| # | Check | Result | Evidence |
|---|---|---|---|
| 5.1 | New lesson can be created with a title | PASS | `POST /api/admin/lessons {"title":"Food"}` → `201 {"id":21,"title":"Food","vocabulary_count":0}` |
| 5.2 | New vocabulary can be added to a lesson | PASS | `POST /api/admin/vocabulary {"lesson_id":21,"hebrew":"לחם","meaning":"bread"}` → `201 {"id":201,...}` |
| 5.3 | New vocabulary immediately available in Study/Quiz/Exam | PASS | `GET /api/lessons/21/vocabulary` returns the new item; `GET /api/lessons/21/quiz` builds a question for it (distractors auto-filled from other lessons since the lesson has <4 items, per architecture §5 step 2) |
| 5.4 | Vocabulary add against a nonexistent lesson is rejected | PASS | `POST /api/admin/vocabulary {"lesson_id":9999,...}` → `404` |
| 5.5 | Admin is add-only: no edit/delete surface | PASS | `PUT /api/lessons/1` → `405`; `DELETE /api/lessons/1` → `405`; `PUT /api/admin/lessons/21` → `405`; `DELETE /api/admin/vocabulary/201` → `405`; `admin.html`/`admin.js` expose only "add lesson" and "add vocabulary" forms |
| 5.6 | Admin input is validated | PASS | `POST /api/admin/lessons {}` → `422`; `POST /api/admin/vocabulary {"lesson_id":21}` → `422` |

## 6. Text-to-Speech (`06-text-to-speech.md`)

| # | Check | Result | Evidence |
|---|---|---|---|
| 6.1 | A pronunciation control accompanies every Hebrew word shown (Study, Quiz, Exam prompts) | PASS (static) | `study.js` appends `tts.createSpeakerButton(item.hebrew)` per vocab card; `quiz.js` and `exam.js` each append one per question prompt |
| 6.2 | Playback is client-side only (browser `SpeechSynthesis`, no backend/API involvement) | PASS (static) | `tts.js` calls only `window.speechSynthesis` / `SpeechSynthesisUtterance`; no network request; no backend route related to audio exists |
| 6.3 | No overlapping/stacked audio; graceful degradation if unsupported | PASS (static) | `tts.speak()` calls `window.speechSynthesis.cancel()` before each new utterance; `createSpeakerButton()` disables the button with a tooltip (not hidden) when `isAvailable()` is false, without touching any other feature |

## 7. Cross-cutting

| # | Check | Result | Evidence |
|---|---|---|---|
| 7.1 | Single process serves both API and static frontend | PASS | All of `/`, `/index.html`, `/lesson.html`, `/study.html`, `/quiz.html`, `/exam.html`, `/admin.html`, `/static/js/api.js`, `/static/js/tts.js` → `200` from the same `uvicorn` process that serves `/api/*` |
| 7.2 | Every HTML page's JS-referenced element IDs exist in that page's markup | PASS | Cross-checked `id="..."` attributes in each `frontend/*.html` against the DOM lookups (`document.getElementById(...)`) in its paired `static/js/*.js` — no mismatches found |
| 7.3 | XSS-safe rendering of user/content-sourced text | PASS (static) | All frontend JS interpolates lesson titles, vocabulary, and admin-entered text through a shared `escapeHtml()` helper before insertion into `innerHTML` |

## Failures

None.

## Limitations

- Frontend interaction (clicking through Study/Quiz/Exam/Admin in an actual
  browser, verifying rendered layout, and hearing TTS audio) was **not**
  exercised by an automation tool in this environment — only statically
  reviewed by reading the HTML/JS against the briefs and cross-checking
  element IDs. No browser-interaction claims are made beyond this static
  review.
- Backend behavior was verified live via `curl` against the running
  application (`install.sh` + `run.sh`), covering every documented endpoint
  in `docs/architecture.md` §6, including edge cases (404s, 422s, 405s, and
  the low-vocab-count distractor fallback for a freshly Admin-created
  lesson).
