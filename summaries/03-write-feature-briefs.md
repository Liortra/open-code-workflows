# Summary: Feature Brief Writer (Stage 3)

- **Date:** 2026-08-31
- **Author / Executor:** Claude
- **Instruction file:** `instructions/build/03-write-feature-briefs.md`
- **Commit:** `stage 03: write behavioral briefs for the six features`

## Work Completed

Read `concept.md` and all six files in `features/`, and wrote one behavioral
brief per feature under `features/briefs/`, matching numbering and naming.
Each brief covers purpose, expected behavior, inputs/outputs, user-visible
behavior, constraints, and basic acceptance expectations, with no
implementation detail (no filenames, classes, SQL, or frameworks).

Stage 2's summary flagged two things as underspecified in the concept: (1)
how Quiz and Exam differ beyond stakes/framing, and (2) whether score/progress
history is tracked at all. Since resolving these correctly affects nearly
every brief, three clarifying questions were put to the human before writing
the briefs (see "Key Decisions" below for the resolutions) rather than
guessing and risking rework downstream.

## Outputs Produced

- `features/briefs/01-lesson-catalog.md`
- `features/briefs/02-study-mode.md`
- `features/briefs/03-quiz-mode.md`
- `features/briefs/04-exam-mode.md`
- `features/briefs/05-admin-content-management.md`
- `features/briefs/06-text-to-speech.md`

## Key Decisions

Resolved with the human (not inferred, and not written back into
`concept.md`):

- **No user accounts / no login.** The app is single-user; "Admin" is simply
  an unrestricted section of the app, not a separate authenticated role.
  This affects `05-admin-content-management.md` (Admin has no auth gate) and
  rules out any per-user data model.
- **Quiz vs. Exam distinction.** Quiz mode gives immediate per-question
  feedback, is retakeable without limit, and its attempts are never saved.
  Exam mode withholds feedback until submission, requires all 10 questions
  answered, and its result (score + timestamp) is saved as a permanent,
  viewable record per lesson. This is now explicit in
  `03-quiz-mode.md` and `04-exam-mode.md`.
- **Exam results are saved; Quiz results are not.** This resolves Stage 2's
  open question about progress tracking — persistence exists, but only for
  Exam attempts, not Quiz or Study activity.
- **Text-to-Speech uses the browser's built-in speech synthesis**
  (client-side, no external API/key, no pre-recorded audio files), fitting
  the "simple" framing and the FastAPI+SQLite+Bootstrap stack with no
  external services mentioned in the concept. Captured as a constraint in
  `06-text-to-speech.md`.

Other decisions made without needing to ask, as reasonable readings of the
concept/feature files:

- Admin was kept strictly to *adding* lessons/vocab (no edit/delete), per
  Stage 2's own scoping and the concept's wording ("add new Lessons/Vocab").
- Quiz/Exam questions test one vocabulary item at a time with distractors
  drawn from other vocabulary, since the concept only specifies
  "multiple-choice" without further detail.
- Newly added Admin content (lessons/vocab) is required to appear
  immediately everywhere else in the app (catalog, modes) with no separate
  publish step, since nothing in the concept suggests a draft/review stage.

## Open Questions & Concerns

- The concept and feature files don't specify exact multiple-choice
  mechanics (e.g. number of answer options, whether questions test
  Hebrew→meaning, meaning→Hebrew, or both directions). Left open
  intentionally as an implementation-level decision for the Architect/Backend
  stages, since pinning it here would edge into technical design.
- No pass/fail threshold was specified for Exam mode, so none was added —
  the brief only requires the score to be shown and saved, not judged against
  a threshold. Flagging in case a pass/fail concept is expected later.
- The actual 200 starting vocabulary items (20 lessons × 10 words) are not
  authored anywhere yet; that remains a content/seeding concern for a later
  stage (System Engineer or Backend), not Stage 3.

## Status

- [x] Complete
- [ ] Needs review
