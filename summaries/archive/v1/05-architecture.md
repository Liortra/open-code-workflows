# Summary: Architect (Stage 05)

- **Date:** 2026-08-31
- **Author / Executor:** Claude Code (agent)
- **Instruction file:** `instructions/build/05-architecture.md`
- **Commit:** `stage 05: define architecture for Hebrew Language Tutor`

## Work Completed

Read `concept.md`, all six feature briefs, and the approved environment
(`requirements.txt`, `environment-notes.md`), and produced a full technical
specification at `docs/architecture.md`: project/file structure, module
boundaries, SQLite schema, question-generation logic shared by Quiz and
Exam, complete API contracts (routes/payloads/responses), and
backend/frontend responsibility split. No application code was written.

## Outputs Produced

- `docs/architecture.md` — the technical specification.

## Key Decisions

- **Single FastAPI process**, multi-page static Bootstrap frontend (no SPA
  framework, no build step) — per the approved environment.
- **No ORM** — stdlib `sqlite3` only, matching `environment-notes.md`.
- **Three tables**: `lessons`, `vocabulary`, `exam_attempts`. No
  `quiz_attempts` table, since Quiz results are explicitly not persisted
  per `03-quiz-mode.md`.
- **Exam persistence is score-only**: `exam_attempts` stores
  `(lesson_id, score, total, taken_at)`. The per-question review shown on
  submission is computed and returned once, not stored — the brief only
  requires past *scores* to remain viewable, not a replayable review.
- **Question direction fixed**: Hebrew word is always the prompt; the 4
  choices are meanings. The briefs left this open deliberately; this
  resolves it consistently across Quiz and Exam.
- **Distractor pool**: same lesson's other vocabulary first, falling back
  to other lessons' vocabulary if an Admin-created lesson has fewer than 4
  items total — handles the edge case of a brand-new lesson with only 1-2
  vocabulary items.
- **Quiz is fully stateless server-side**: a `check` endpoint gives
  immediate per-question feedback; the frontend tallies its own final
  score from those responses, so no server-side quiz session/state is
  needed.
- **SQLite file** at `backend/data/app.db` (first-run-created, already
  covered by `.gitignore`'s `*.db` entry).
- **Seeding**: `seed_data.py` (plain data) is applied by `database.py` on
  first run when `lessons` is empty, so a fresh checkout is usable without
  a manual data-load step. This is a Stage 6 implementation detail
  specified here so backend engineering doesn't have to invent it.

## Open Questions & Concerns

- None blocking. The feature briefs were specific enough that no product
  clarification was needed; the handful of implementation-shape choices
  above were made and documented directly in `docs/architecture.md` rather
  than left for Stage 6 to guess at.
- `summaries/00-template.md` referenced by `instructions/build/00-README.md`
  does not exist in this repo (only `02-`, `03-`, `04-` summaries are
  present). This summary follows the style of `summaries/04-*.md` instead;
  flagging in case the template was meant to be added at some point.

## Status

- [x] Complete
- [ ] Needs review
