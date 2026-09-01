# Summary: Architect (Stage 05)

- **Date:** 2026-09-01
- **Author / Executor:** Claude (Architect role)
- **Instruction file:** `instructions/enhancements/05-architecture.md`
- **Scope reference:** `enhancements/scope.md`
- **Commit:** `stage 05: extend architecture for sprint 01 enhancements`

## Work Completed

Read `enhancements/scope.md`, all four Stage 3 feature briefs
(`features/briefs/01-english-text-to-speech.md`,
`02-spaced-repetition.md`, `03-progress-dashboard.md`,
`04-nikud-toggle.md`), the existing `docs/architecture.md`, Stage 4's
confirmation that no environment changes are needed
(`instructions/enhancements/summaries/04-system-engineering.md`), and the
relevant existing backend/frontend source (`tts.js`, `study.js`,
`quiz.js`, `exam.js`, `admin.js`, `catalog.js`, `database.py`, `main.py`,
`schemas.py`, `quiz_logic.py`) to ground the extension in the real
contracts rather than guessing at them.

Five cross-cutting design points were not fully resolved by the briefs and
were confirmed with the coordinator before writing the specification (see
Key Decisions below), since they affect API/data contracts multiple
downstream stages will build against.

Appended a new §11 "Enhancement: Sprint 01 — Study Aids & Progress
Tracking" to `docs/architecture.md`, covering all four features. Sections
1–10 (the v0.1 specification) were left untouched.

## Outputs Produced / Modified

- `docs/architecture.md` — extended (not rewritten) with new §11, covering:
  - Data model: two new tables, `word_review_state` (SRS) and
    `activity_log` (streak tracking); `lessons`/`vocabulary`/`exam_attempts`
    unchanged.
  - API contracts: `GET /api/srs/due`, `POST /api/srs/{vocabulary_id}/answer`,
    `POST /api/activity`, `GET /api/dashboard`. English TTS and the nikud
    toggle add no backend surface (client-only).
  - A precise SRS scheduling transition rule (day-ladder `[0,1,3,7,14,30]`,
    with the exact index-assignment rule needed to satisfy the brief's
    "a correct answer must not make the word immediately due again"
    acceptance test).
  - Backend/frontend responsibility deltas, including which existing JS
    modules gain new behavior (`tts.js`, `study.js`, `quiz.js`, `exam.js`)
    and which are new (`srs.js`/`srs.html`, `dashboard.js`/`dashboard.html`,
    `nikud.js`).
  - Component interaction / state-flow diagram showing the new SRS/
    Dashboard/activity-log write paths alongside the unchanged Study/Quiz/
    Exam flow.
  - An explicit "unchanged / out of scope" list reaffirming that Quiz
    remains unpersisted with respect to results, Exam/SRS data stay
    mutually isolated, and no new dependency or environment change is
    introduced.
- `instructions/enhancements/summaries/05-architecture.md` (this file, new).

## Key Decisions

Confirmed with the coordinator before finalizing (all accepted as
proposed):

1. **Streak completion signal.** New `activity_log` table +
   `POST /api/activity {mode}` endpoint, called by Study (on vocabulary
   load) and Quiz (on reaching the summary screen) only — the two modes
   with no other durable completion signal. Exam's existing
   `exam_attempts` row and SRS's new answer endpoint each serve as their
   own completion signal, so neither calls the generic endpoint. Read
   Quiz's existing "results are not persisted" constraint as being about
   *result* data specifically; a bare completion timestamp is a different,
   narrower thing and doesn't violate it.
2. **SRS scheduling:** fixed day-ladder `[0, 1, 3, 7, 14, 30]`, advance a
   step on correct recall, reset to 0 on incorrect. While writing the
   spec I found and fixed an off-by-one in the naive version of this rule:
   a *correct* answer must never be allowed to land on index 0 (0 days),
   only an incorrect one may — otherwise a first-ever correct answer would
   make the word immediately due again, failing the brief's explicit
   acceptance test. The exact index-assignment rule is spelled out in
   §11.3 with a worked example. This stays within the approved ladder
   values; it only fixes the transition rule, so it wasn't re-escalated.
3. **English TTS control scope:** added to Study mode and Exam's
   post-submit review rows only; not added to Quiz's or Exam's four
   answer-choice buttons/radios.
4. **Nikud toggle persistence:** browser `localStorage`, no backend
   involvement, no new table/endpoint.
5. **Nikud toggle scope:** applies only to rendered/read-only Hebrew text;
   the Admin "Add Vocabulary" Hebrew input box is explicitly excluded and
   always shows exactly what's typed.

Additional judgment calls made without escalation (small enough to fall
within normal architecture discretion):

- Dashboard is reachable via a new nav-bar link on every page rather than
  replacing `/`; `index.html` (Catalog) keeps serving as the default route
  unchanged, per the brief's explicit "alongside ... the Lesson Catalog"
  option.
- SRS's `GET /api/srs/due` reuses Quiz/Exam's existing distractor-selection
  logic in `quiz_logic.py` (that helper is exposed for reuse rather than
  duplicated) so review-queue questions are never built with a different
  strategy than Quiz/Exam.
- New timestamp columns follow the existing `strftime(...)`-based
  convention already used in `database.py`, not `datetime('now')`, to stay
  consistent and lexicographically comparable with `exam_attempts.taken_at`.

## Open Questions & Concerns

- The current seed data's Hebrew words (e.g. `שלום`) contain no nikud
  characters at all, so the nikud toggle will be visually a no-op against
  seed content until nikud-bearing text exists via Admin. This doesn't
  block Stage 6/7 (the toggle and stripping logic are still fully
  specified), but Stage 8 (Verification) will need Admin-entered
  nikud-bearing content to actually observe the show/hide behavior — flag
  this for whoever plans verification.
- `quiz_logic.py`'s distractor helper is currently private
  (`_distractors_for`). Backend Engineer (Stage 6) will need to
  de-privatize or extract it for `srs_logic.py` to reuse, per §11.4/§11.5
  — noted explicitly in the architecture text so this isn't missed or
  duplicated.
- No blocking ambiguity remains for Stage 6/7 beyond normal
  implementation judgment; all five coordinator-facing decisions are
  locked into §11 with concrete schemas/contracts.

## Status

- [x] Complete
- [ ] Needs review
