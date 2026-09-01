# Summary: Feature Brief Writer (Stage 03)

- **Date:** 2026-09-01
- **Author / Executor:** Claude (enhancement pipeline, Stage 3)
- **Instruction file:** `instructions/enhancements/03-write-feature-briefs.md`
- **Scope reference:** `enhancements/scope.md`
- **Commit:** `stage 03: write feature briefs for sprint01 features`

## Work Completed

Read `enhancements/scope.md`, all four Stage 2 feature files under
`features/`, and the existing v0.1 briefs under `features/archive/v1/briefs/`
for context on the behavior each new feature extends. Wrote one behavioral
brief per feature under the newly created `features/briefs/` folder,
covering purpose, expected behavior, inputs/outputs, user-visible behavior,
constraints, and basic acceptance expectations for each, with explicit
attention to how each feature integrates with (and does not regress)
existing v0.1 behavior.

Four points were materially underspecified by the scope/feature files.
These were surfaced to the coordinator before writing began; the
coordinator confirmed a decision for each, and each decision is recorded
explicitly in its brief (not in `enhancements/scope.md`), per the
instruction file's guidance.

## Outputs Produced / Modified

- `features/briefs/01-english-text-to-speech.md` — new. Adds an independent
  English-meaning speaker control alongside the existing Hebrew
  pronunciation control, sharing the "only one utterance at a time" rule
  across both languages; leaves the existing Hebrew-only behavior
  unchanged.
- `features/briefs/02-spaced-repetition.md` — new. Defines a per-word
  recall history and a cross-lesson "Due for Review" queue, fed only by its
  own review interaction. Records the confirmed decision that this does not
  read from or alter Quiz mode (still unpersisted) or Exam mode (unchanged).
- `features/briefs/03-progress-dashboard.md` — new. Defines a home-screen
  dashboard showing per-lesson mastery %, cross-lesson exam history, and a
  day-streak counter. Records the confirmed decisions that mastery % is
  based solely on a lesson's most recent Exam attempt (not folding in SRS
  data), and that the streak counts a day only when a Study, Quiz, Exam, or
  SRS review session is completed that day.
- `features/briefs/04-nikud-toggle.md` — new. Defines an app-wide,
  display-only nikud show/hide setting. Records the confirmed assumption
  that existing/future Hebrew content already includes nikud, and that the
  toggle affects display only (not storage, authoring, or pronunciation)
  across Catalog, Study, Quiz, Exam, and Admin.

## Key Decisions

The following four points were flagged as open questions before work began
and were confirmed by the coordinator; each is recorded explicitly in its
brief so downstream engineering roles do not have to guess:

1. **SRS data source:** the "Due for Review" queue is fed only by its own
   self-contained review interaction, which persists per-word recall
   history. It does not touch Quiz mode's no-persistence behavior or Exam
   mode's existing behavior.
2. **Day-streak definition:** a day counts toward the Progress Dashboard's
   streak only if the learner completes at least one Study, Quiz, Exam, or
   SRS review session that day — not merely opening the app.
3. **Mastery % source:** per-lesson mastery percentage is based on that
   lesson's most recent Exam attempt only; it does not average multiple
   attempts and does not fold in SRS recall data.
4. **Nikud toggle scope:** existing/future Hebrew content is assumed to
   already include nikud; the toggle is a display-only, app-wide show/hide
   across Catalog, Study, Quiz, Exam, and Admin, with no effect on
   Text-to-Speech (Hebrew or English) or on how content is stored/authored.

Additionally, kept strict brief-to-feature-file numbering (`01`-`04`)
matching Stage 2's feature files, and wrote each brief to describe only the
new delta on top of existing v0.1 behavior, per instruction, without
rewriting or redefining any existing v1 brief.

## Open Questions & Concerns

- Non-blocking structural note (carried forward from Stage 1 and Stage 2
  summaries): `instructions/enhancements/00-README.md` and
  `instructions/enhancements/03-write-feature-briefs.md` both describe the
  existing v0.1 briefs as living at `features/completed/briefs/` (or
  `archive/build/`), but this repo actually has them at
  `features/archive/v1/briefs/`. This did not block Stage 3 — the existing
  briefs were located and read for context — but a later stage or a human
  may want to reconcile the instruction files' described layout with the
  actual repo path.
- All four features now have unambiguous, coordinator-confirmed briefs.
  Downstream stages (Architect, Backend/Frontend Engineers) should treat
  the four "Key Decisions" above as settled behavioral requirements, not as
  open design space — in particular, SRS must remain isolated from Quiz/Exam
  persistence, and mastery % must not be redefined to include SRS data
  without a new decision.

## Status

- [x] Complete
- [ ] Needs review
