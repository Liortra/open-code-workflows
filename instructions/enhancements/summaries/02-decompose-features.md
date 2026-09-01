# Summary: Feature Decomposition (Stage 02)

- **Date:** 2026-09-01
- **Author / Executor:** Claude (enhancement pipeline, Stage 2)
- **Instruction file:** `instructions/enhancements/02-decompose-features.md`
- **Scope reference:** `enhancements/scope.md`
- **Commit:** `stage 02: decompose sprint01 scope into four features`

## Work Completed

Read `enhancements/scope.md` (Stage 1 output) and the existing v0.1 feature
set for context (found at `features/archive/v1/`, not `features/completed/`
as the instruction file names it — see Open Questions). Created the fresh
`features/` folder and wrote one feature file per in-scope enhancement from
the scope document, at the capability level only (no behavior, workflow, or
implementation detail).

## Outputs Produced / Modified

- `features/01-english-text-to-speech.md` — new. Extends the existing
  Text-to-Speech capability (`features/archive/v1/06-text-to-speech.md`) to
  also speak a vocabulary item's English meaning; described as an extension,
  not a duplicate of the existing capability.
- `features/02-spaced-repetition.md` — new. Cross-lesson recall tracking and
  a "Due for Review" queue.
- `features/03-progress-dashboard.md` — new. Home-screen view of per-lesson
  mastery, exam history, and day-streak.
- `features/04-nikud-toggle.md` — new. Setting to show/hide Hebrew vowel
  pointing.

## Key Decisions

- Mapped the four scope items (a-d) to four feature files 1:1, since
  `enhancements/scope.md` already scoped each item at capability
  granularity (each was individually labeled "Feature" by Stage 1); no
  further splitting or merging was warranted.
- Numbered the feature files 01-04 in the same order as scope.md's a-d
  listing.
- Item (a) (English TTS) was written explicitly as an extension of the
  existing Text-to-Speech feature rather than a standalone/duplicate
  capability, per the instruction to not duplicate existing capabilities.
- Kept all four files at the capability level: what the product will be able
  to do, with no mention of API routes, data models, screens, or other
  implementation detail.

## Open Questions & Concerns

- Non-blocking structural note (carried forward from the Stage 1 summary):
  `instructions/enhancements/00-README.md` and
  `instructions/enhancements/02-decompose-features.md` both describe the
  existing v0.1 feature set as living at `features/completed/` (or
  `archive/build/`), but this repo actually has it at
  `features/archive/v1/`. This did not block Stage 2 — the archived features
  were located and read for context — but a later stage or a human may want
  to reconcile the instruction files' described layout with the actual repo
  path.
- No open questions on the feature list itself. The four features fully and
  exactly cover scope items a-d with nothing added or dropped; downstream
  stages (Feature Brief Writer, Architect) will make the behavioral and
  technical decisions the scope and feature files leave open (e.g., how the
  SRS review queue integrates with Study/Quiz/Exam modes, where the Nikud
  toggle setting is surfaced in the UI).

## Status

- [x] Complete
- [ ] Needs review
