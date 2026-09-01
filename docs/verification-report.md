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

---

# Verification Report Addendum — Sprint 01 Enhancement (Study Aids & Progress Tracking)

- **Date:** 2026-09-01
- **Scope:** the four Sprint 01 features (`enhancements/scope.md`): English
  Text-to-Speech, Spaced Repetition (SRS), Progress Dashboard, Nikud Toggle —
  as specified in `docs/architecture.md` §11 and
  `features/briefs/01–04-*.md`.
- **Method:**
  - Backend: live via `curl` (and one small Python/urllib helper script for
    multi-request sequences) against the app started with `./install.sh` +
    `./run.sh` (`uvicorn` on `localhost:8000`), using a **freshly reseeded**
    `backend/data/app.db` (deleted before starting the server, so results
    reflect a clean checkout).
  - Frontend: static review of `frontend/**/*.html` and
    `frontend/static/js/*.js` against the briefs/architecture, plus
    `node --check` on every JS file for syntax validity and a manual
    cross-check of every `document.getElementById(...)` call against its
    page's markup — no headless/browser automation was used, consistent
    with the v0.1 methodology above.
  - **Multi-day streak / gap-handling** (coordinator-approved approach):
    since real time cannot be advanced within this session, the day-streak
    walk-back logic was exercised by directly inserting/removing rows in
    `activity_log` via the `sqlite3` CLI (bypassing the API), then reading
    the result back via `GET /api/dashboard` over `curl`. These results are
    labeled "direct SQLite verification" below and kept distinct from the
    curl-only evidence.
  - **Nikud toggle** (coordinator-approved approach): the shipped seed data
    (`backend/seed_data.py`) contains zero nikud characters, so one
    nikud-bearing vocabulary item (`שָׁלוֹם`) was added through the live
    Admin API to produce real evidence for the strip round-trip, rather than
    relying on seed content.
  - **Regression depth** (coordinator-approved): a representative spot-check
    across each v0.1 area (not a verbatim re-run of the prior 32-check
    matrix), on the theory that Sprint 01 only adds new tables/routers and
    does not modify any existing table, router, or endpoint contract.
- **Checklist derivation:** one item per observable behavior stated in
  `docs/architecture.md` §11 (API/data contracts) and
  `features/briefs/01–04-*.md` (acceptance expectations), plus regression
  items carried over from the v0.1 checklist derivation method above.
- Evidence artifacts (JSON responses, logs) are under `./tmp/stage08/`
  (gitignored scratch space, not committed).

## Summary

| Area | Checks | Pass | Fail |
|---|---|---|---|
| 8. English Text-to-Speech | 8 | 8 | 0 |
| 9. Spaced Repetition | 11 | 11 | 0 |
| 10. Progress Dashboard | 11 | 11 | 0 |
| 11. Nikud Toggle | 9 | 9 | 0 |
| 12. Regression (v0.1 spot-check) | 7 | 7 | 0 |
| 13. Cross-cutting (enhancement) | 4 | 4 | 0 |

**50/50 checks passed. No failures.**

## 8. English Text-to-Speech (`features/briefs/01-english-text-to-speech.md`)

| # | Check | Result | Evidence |
|---|---|---|---|
| 8.1 | Study mode shows a second (English) speaker control alongside the existing Hebrew one | PASS (static) | `study.js`: `controls.appendChild(tts.createSpeakerButton(item.hebrew, "he-IL", "Hebrew"))` and `...createSpeakerButton(item.meaning, "en-US", "English")` per vocab card |
| 8.2 | English control is independent of the Hebrew control (either can be used without the other) | PASS (static) | Each button has its own click handler calling `tts.speak(text, lang)` directly; no ordering/gating between them |
| 8.3 | Client-side only — browser `SpeechSynthesis`, no backend/network involvement, no new endpoint | PASS (static) | `tts.js` calls only `window.speechSynthesis`/`SpeechSynthesisUtterance`; `backend/main.py`'s router list has no TTS-related route |
| 8.4 | Only one utterance plays at a time across both languages (no overlap) | PASS (static) | `tts.speak()` calls `window.speechSynthesis.cancel()` unconditionally before every utterance, regardless of `lang` |
| 8.5 | Graceful degradation if speech synthesis is unavailable, without blocking other features | PASS (static) | `createSpeakerButton()` disables the button with a tooltip (not hidden) when `!isAvailable()`; nothing else in the click path is touched |
| 8.6 | English control can be used repeatedly without errors | PASS (static) | Stateless handler (`speak()` has no accumulating state); repeated clicks just cancel-and-restart |
| 8.7 | Exam's post-submit review rows get an English control for the meaning (extension beyond Study mode, per brief point 1 "anywhere else a meaning is displayed") | PASS (static) | `exam.js::showResults` appends both `createSpeakerButton(item.prompt, "he-IL", "Hebrew")` and `createSpeakerButton(item.correct_answer, "en-US", "English")` per review row |
| 8.8 | Existing Hebrew-only pronunciation elsewhere (Quiz, Exam pre-submit prompts) is unchanged — no per-choice English control added (Decision 3) | PASS (static) | `quiz.js`/`exam.js` pre-submit prompt speakers still call only `createSpeakerButton(prompt, "he-IL", "Hebrew")`; answer-choice buttons/radios have no speaker control |

## 9. Spaced Repetition (`features/briefs/02-spaced-repetition.md`)

| # | Check | Result | Evidence |
|---|---|---|---|
| 9.1 | `GET /api/srs/due` returns items spanning every lesson on a fresh DB | PASS | Fresh seeded DB → 200 items, `lesson_id` values across 1–20 (`tmp/stage08/01_srs_due_fresh.json`) |
| 9.2 | A word with no review history is treated as due | PASS | Same response: all 200 words due with zero prior `word_review_state` rows |
| 9.3 | A word answered correctly updates its history and does not immediately reappear in the due list | PASS | `vocabulary_id=1` answered correctly → next `GET /api/srs/due` returned 199 items, id 1 absent (`tmp/stage08/02_srs_due_after_item1.json`) |
| 9.4 | Day-ladder worked example (architecture §11.3) matches exactly: correct→+1d, correct→+3d, incorrect→due now, correct→+1d again (never lands on the 0-day rung from a correct answer) | PASS | `POST /api/srs/1/answer` sequence: `next_due_at` 2026-09-02 (+1d) → 2026-09-04 (+3d) → 2026-09-01 (now, incorrect) → 2026-09-02 (+1d, streak reset) — server clock read as 2026-09-01T15:49:18 |
| 9.5 | `404` for an unknown `vocabulary_id` on the answer endpoint | PASS | `POST /api/srs/999999/answer` → `404` |
| 9.6 | Review queue is reachable independently of any lesson (cross-lesson entry point) | PASS (static) | `srs.html` reachable via a top-level "Review" navbar link on every page, not nested under `lesson.html` |
| 9.7 | Nothing-due state is reachable and distinguishable from a broken/empty screen | PASS | After correctly answering all 201 vocabulary items (200 seed + 1 Admin-added) via `POST /api/srs/{id}/answer`, `GET /api/srs/due` returned `[]`; `srs.js` renders `#empty-state` on an empty response |
| 9.8 | Immediate correct/incorrect feedback per reviewed item | PASS (static) | `srs.js::selectAnswer()` renders `#feedback` from the answer response immediately, mirroring `quiz.js`'s pattern |
| 9.9 | Vocabulary added later via Admin is included in the queue without a separate setup step | PASS | The Admin-added item (`vocabulary_id 201`, lesson 21) appeared as due and was answerable through the same endpoint with no extra step |
| 9.10 | SRS reads/writes only its own tables — no interaction with Quiz or Exam data | PASS (static) | `srs_logic.py`/`routers/srs.py` reference only `vocabulary`, `word_review_state`, `activity_log`; no reference to `exam_attempts` or quiz endpoints |
| 9.11 | Quiz mode remains fully unpersisted (no new coupling to SRS) | PASS | `POST /api/lessons/1/quiz/check` still returns only `{is_correct, correct_answer}`; no quiz-attempt table exists; schema diff confirms `lessons`/`vocabulary`/`exam_attempts` unchanged |

## 10. Progress Dashboard (`features/briefs/03-progress-dashboard.md`)

| # | Check | Result | Evidence |
|---|---|---|---|
| 10.1 | Mastery % from most recent Exam attempt only; `null` when a lesson has no attempt | PASS | Fresh DB: all 20 lessons `mastery_percent: null` (`tmp/stage08/00_dashboard_fresh.json`); after a 10/10 submit on lesson 1 → `mastery_percent: 100` |
| 10.2 | Exam history spans all lessons, most recent first | PASS (static + live) | `dashboard.py`'s query `ORDER BY e.taken_at DESC, e.id DESC` joined across all `exam_attempts`; live: history entry appeared immediately after the lesson-1 submission |
| 10.3 | Streak is `0` with no activity anywhere | PASS | Live `curl`, fresh DB: `streak_days: 0` |
| 10.4 | One qualifying session today produces `streak_days: 1` | PASS | Live `curl`, after `POST /api/activity {"mode":"study"}`: `streak_days: 1` |
| 10.5 | N consecutive calendar days produce a streak of N | PASS (direct SQLite) | Inserted `activity_log` rows for yesterday and the day before → `streak_days: 3` |
| 10.6 | A gap (non-contiguous day) breaks the streak | PASS (direct SQLite) | Removed the "yesterday" row, kept today + a non-contiguous earlier day → `streak_days: 1`, not 2 |
| 10.7 | With no activity today, the streak falls back to the most recent qualifying day (not 0) | PASS (direct SQLite) | Removed all of today's `activity_log`/`exam_attempts` rows, left one qualifying day 2 days prior → `streak_days: 1` |
| 10.8 | Viewing the dashboard never writes / never inflates the streak | PASS (static) | `get_dashboard()` issues only `SELECT` statements; repeated `GET /api/dashboard` calls during this session never changed prior results |
| 10.9 | A lesson added via Admin appears on the dashboard immediately | PASS (static + live) | `dashboard.py` selects `SELECT id, title FROM lessons` with no filter; the Admin-added lesson (id 21, "Verification Nikud Test") is included on the same basis as every seed lesson |
| 10.10 | `POST /api/activity` accepts only `study`/`quiz`; rejects `exam`/`srs`/other with `422` | PASS | Live: `study`→201, `quiz`→201, `exam`→422, `srs`→422, `bogus`→422 |
| 10.11 | Existing Lesson Catalog / Study / Quiz / Exam / Admin remain unaffected by the dashboard's addition | PASS | See §12 regression checks |

## 11. Nikud Toggle (`features/briefs/04-nikud-toggle.md`)

| # | Check | Result | Evidence |
|---|---|---|---|
| 11.1 | A toggle control is present and discoverable on every page | PASS | `#nikud-toggle-slot` present in all 8 pages (`index`, `lesson`, `study`, `quiz`, `exam`, `admin`, `dashboard`, `srs`.html), confirmed by grep |
| 11.2 | Setting persists across sessions via `localStorage`, no backend involvement | PASS (static) | `nikud.js`'s `isHidden()`/`setHidden()` touch only `window.localStorage`; no API call anywhere in the module |
| 11.3 | Toggling re-applies to Hebrew text already on screen, without a reload | PASS (static) | `setHidden()` calls `applyAll()`, which re-applies to every `[data-hebrew]` element currently in the DOM |
| 11.4 | Every Hebrew display site uses the `data-hebrew`/`nikud.render()` convention | PASS (static) | `study.js`, `quiz.js` (prompt), `exam.js` (pre-submit prompt + review prompt), `srs.js` (prompt) all call `nikud.render(el, text)` instead of setting `textContent` directly |
| 11.5 | Hiding nikud strips vowel points, leaving consonantal text only | PASS | Admin-added `שָׁלוֹם` → Node re-execution of the exact `nikud.js` strip regex (`/[֑-ׇ]/g`) produced `שלום` (7 chars → 4 chars), matching the expected consonantal form |
| 11.6 | Stored Hebrew text is never rewritten by the toggle | PASS | `GET /api/lessons/21/vocabulary` after the Admin add returned `"hebrew":"שָׁלוֹם"` unchanged (fully vocalized, exactly as submitted) |
| 11.7 | Admin's "Add Vocabulary" Hebrew input is excluded from the toggle (Decision 5) | PASS (static) | `admin.js` was not modified for Sprint 01 and never calls `nikud.render`; the `<input>` always shows exactly what's typed |
| 11.8 | Text-to-Speech output is unaffected by the toggle state (spoken text is always the raw fetched value, not the possibly-stripped DOM text) | PASS (static) | Every `createSpeakerButton(...)` call site (`study.js`, `quiz.js`, `exam.js`, `srs.js`) passes the raw API field (`item.hebrew`, `question.prompt`, etc.), not text read back from the DOM, so nikud display state cannot affect what's spoken |
| 11.9 | Existing v0.1 screens (Catalog, Admin) unaffected beyond the added toggle | PASS (static) | `catalog.js`/`lesson.js` were not modified beyond the navbar/script-tag addition (per Stage 7); neither renders Hebrew text today |

## 12. Regression — v0.1 behavior unchanged (representative spot-check)

| # | Check | Result | Evidence |
|---|---|---|---|
| 12.1 | Lesson Catalog: `GET /api/lessons` still returns the full catalog | PASS | `200`, all seed lessons present on a fresh DB |
| 12.2 | Study: `GET /api/lessons/{id}/vocabulary` unchanged shape | PASS | `200`, `{id, hebrew, meaning}` per item, unchanged |
| 12.3 | Quiz: `GET .../quiz` + `POST .../quiz/check` still stateless with immediate feedback | PASS | `200` question list; `POST /api/lessons/1/quiz/check` → `{"is_correct":true,"correct_answer":"hello"}` |
| 12.4 | Exam: full submission still returns `score`/`total`/`taken_at`/`review` and persists to `/exam/history` | PASS | 10/10 submission on lesson 1 → full response shape; `GET /api/lessons/1/exam/history` reflects it |
| 12.5 | Admin: add-only enforcement and validation unchanged (`404`/`422`/`405`) | PASS | `POST .../vocabulary` with unknown `lesson_id` → `404`; `POST .../lessons {}` → `422`; `PUT /api/lessons/1` → `405`; `DELETE /api/admin/vocabulary/1` → `405` |
| 12.6 | Existing Hebrew TTS control unchanged in Quiz/Exam pre-submit (no scope creep) | PASS (static) | See 8.8 |
| 12.7 | Single-process serving of the API and static frontend unchanged | PASS | All 8 existing pages + 2 new pages + sampled static JS assets → `200` from the same `uvicorn` process serving `/api/*` |

## 13. Cross-cutting (enhancement-specific)

| # | Check | Result | Evidence |
|---|---|---|---|
| 13.1 | All new/modified frontend JS is syntactically valid | PASS | `node --check` on all 11 files under `frontend/static/js/` — all OK |
| 13.2 | New pages' DOM element IDs referenced by their JS all exist in markup | PASS | Cross-checked `dashboard.html`/`dashboard.js` and `srs.html`/`srs.js` (all `getElementById` targets present); re-confirmed unchanged pages against their JS |
| 13.3 | XSS-safe rendering in new frontend code | PASS (static) | `dashboard.js` and `srs.js` both use the same `escapeHtml()` pattern as existing pages before interpolating lesson/exam/vocabulary text into `innerHTML` |
| 13.4 | No new dependency/package/service introduced | PASS | `requirements.txt` unchanged (`fastapi==0.115.6`, `uvicorn[standard]==0.34.0`); no new `pip` packages required by `install.sh` |

## Failures

None.

## Limitations

- Frontend interaction (clicking through the new Dashboard/Review pages and
  the extended Study/Exam TTS controls in an actual browser) was **not**
  exercised by an automation tool — only statically reviewed, consistent
  with the v0.1 methodology. No browser-interaction claims are made beyond
  this static review.
- The shipped seed data (`backend/seed_data.py`) contains zero nikud
  characters, so the nikud toggle is a visual no-op against out-of-the-box
  content; this was verified instead against one nikud-bearing vocabulary
  item added live through the Admin API (§11.5–11.6). This is expected per
  Stages 5–7's notes, not a defect.
- The SRS "Due for Review" queue is single-fetch/single-pass per session
  (confirmed intended behavior, per Stage 7's summary): a word answered
  incorrectly becomes due again immediately server-side but will not
  reappear until the learner reopens the queue, not mid-session. This is
  the confirmed design, not an omission.
- Multi-day streak and gap-handling behavior (checks 10.5–10.7) were
  verified via direct `sqlite3` manipulation of `activity_log` rather than
  live multi-day use of the API, since this verification session cannot
  advance real time. These results are clearly labeled "direct SQLite
  verification" above, separate from the curl-based evidence.
- Dashboard and Review page layout, exact wording, and CSS are Stage 7's own
  presentational choices (no wireframe existed in the briefs/architecture);
  they were verified functionally against each brief's acceptance
  expectations, not against any specific visual design.
