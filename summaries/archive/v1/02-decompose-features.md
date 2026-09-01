# Summary: Feature Decomposition (Stage 2)

- **Date:** 2026-08-31
- **Author / Executor:** Claude
- **Instruction file:** `instructions/build/02-decompose-features.md`
- **Commit:** `stage 02: decompose Hebrew Language Tutor concept into features`

## Work Completed

Read `concept.md` for the Hebrew Language Tutor web app and broke it into six
discrete product capabilities. Each requirement in the concept maps to
exactly one feature file; no implementation, workflow, or behavioral detail
was written at this stage.

## Outputs Produced

- `features/01-lesson-catalog.md` — browsing the 20-lesson / 10-vocab-each
  catalog.
- `features/02-study-mode.md` — ungraded vocabulary review per lesson.
- `features/03-quiz-mode.md` — multiple-choice quiz per lesson.
- `features/04-exam-mode.md` — multiple-choice exam per lesson.
- `features/05-admin-content-management.md` — adding new lessons/vocab.
- `features/06-text-to-speech.md` — spoken pronunciation of vocabulary.

## Key Decisions

- Study, Quiz, and Exam were split into three separate feature files rather
  than one "lesson modes" feature, since the concept names them as distinct
  modes with different purposes (learning vs. multiple-choice assessment).
- Lesson browsing/selection was called out as its own feature
  (`lesson-catalog`) since it's a prerequisite capability implied by "20
  lessons" but not explicitly named in the concept as part of another mode.
- Admin was scoped strictly to adding lessons/vocab, matching the concept's
  wording; editing/deleting existing content was not assumed.
- The concept's stack preferences (Bootstrap, FastAPI+SQLite) were left
  untouched in `concept.md` and are not repeated here — they belong to later
  architecture/engineering stages.

## Open Questions & Concerns

- Whether Quiz and Exam differ in anything beyond stakes/framing (e.g., pass
  thresholds, retake rules, scope of an exam vs. a single lesson's quiz) is
  not specified in the concept. Left for Stage 3 (briefs) to define
  explicitly, or to flag as underspecified if it can't be inferred.
- No persistence/tracking of scores or progress is mentioned in the concept,
  so none was added as a feature. Flagging in case this was an implicit
  expectation the human wants to add to `concept.md`.

## Status

- [x] Complete
- [ ] Needs review
