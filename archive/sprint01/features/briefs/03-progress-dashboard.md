# Brief: Progress Dashboard

## Purpose

Gives the learner a home-screen view that surfaces their overall progress
at a glance — per-lesson mastery, exam history, and a day-streak — instead
of progress only being visible by opening individual lessons one at a time
and checking each one's saved exam result.

## Decisions recorded in this brief (per coordinator direction)

- **Per-lesson mastery % source:** mastery for a lesson is based on that
  lesson's **most recent Exam attempt only** (per
  `features/archive/v1/briefs/04-exam-mode.md`, exam results are already
  saved per lesson with a score). It does not fold in Spaced Repetition
  recall data (see `02-spaced-repetition.md`) — the two features' progress
  signals are kept independent in this pass.
- **Day-streak definition:** a calendar day counts toward the streak if the
  learner completes at least one Study, Quiz, Exam, or SRS "Due for Review"
  session that day. Merely opening the app without completing a session
  does not count.

## Expected behavior

1. The learner is shown a dashboard view as (or from) the app's home
   screen, alongside or in place of the existing Lesson Catalog entry
   point — the Lesson Catalog itself continues to work exactly as it does
   today (see `features/archive/v1/briefs/01-lesson-catalog.md`); the
   dashboard is an additional view, not a replacement for the catalog's
   ability to browse and open lessons.
2. The dashboard shows, per lesson, a mastery percentage derived from that
   lesson's most recent saved Exam score (e.g. an 8/10 most recent exam
   shows as 80% mastery for that lesson). A lesson with no exam attempt yet
   shows as having no mastery percentage yet (e.g. "not yet attempted"),
   rather than a fabricated or default percentage.
3. The dashboard shows overall exam history: exam results across all
   lessons, not just one lesson at a time, so the learner can see their
   exam activity across the whole catalog in one place.
4. The dashboard shows a day-streak counter: the number of consecutive
   calendar days (up to and including the current day, or ending on the
   most recent qualifying day if today has no activity yet) on which the
   learner completed at least one Study, Quiz, Exam, or SRS review session.
5. The dashboard reflects current data every time it is viewed — a new
   exam attempt, a completed Study/Quiz/SRS session, or a newly added
   lesson via Admin is reflected the next time the dashboard is opened,
   without a separate refresh step.
6. From the dashboard, the learner can still reach the Lesson Catalog and,
   through it, any lesson's Study/Quiz/Exam modes, exactly as before.

## Inputs / outputs

- **Input:** the learner opening the dashboard (home screen); no other
  input is required to view it. The underlying data comes from existing
  Exam results and from Study/Quiz/Exam/SRS session completions used to
  compute the streak.
- **Output:** a read-only summary view showing per-lesson mastery
  percentages, cross-lesson exam history, and the current day-streak count.

## User-visible behavior

- A new dashboard view, visible from the home screen, showing at a glance:
  a mastery percentage per lesson, a list/summary of exam attempts across
  lessons, and a day-streak number.
- Lessons never attempted via Exam show a clear "not yet attempted" state
  rather than 0% or a misleading value.
- The existing Lesson Catalog, and the ability to open any lesson and use
  Study/Quiz/Exam, is unchanged and still reachable.
- The streak counter updates to reflect a day's activity once the learner
  has completed at least one qualifying session that day; it does not
  increase merely from opening the app or the dashboard itself.

## Constraints

- Mastery percentage is computed only from a lesson's most recent Exam
  attempt; it does not average across attempts, does not use Quiz results
  (which are not persisted), and does not incorporate SRS recall data.
- The day-streak counts a day only when a Study, Quiz, Exam, or SRS review
  session is completed that day; simply launching the app does not extend
  or start the streak.
- The dashboard is read-only: it does not provide new ways to modify
  lessons, vocabulary, or scores — those remain the responsibility of their
  existing features (Admin, Exam, etc.).
- The dashboard must not omit or hide any lesson, including lessons added
  later through Admin, and must not omit any lesson's exam history from the
  overall exam history view.
- Viewing the dashboard must not itself count as a session for streak
  purposes.
- No existing Lesson Catalog, Study, Quiz, Exam, or Admin behavior is
  changed, removed, or regressed by adding the dashboard.

## Basic acceptance expectations

- Opening the app's home screen shows the dashboard with a mastery
  percentage for every lesson that has at least one saved exam attempt.
- A lesson with no exam attempt shows a distinguishable "not yet attempted"
  state rather than a numeric percentage.
- The dashboard's exam history reflects attempts from more than one lesson
  when more than one lesson has been attempted.
- Completing an Exam updates that lesson's mastery percentage and appears
  in the exam history the next time the dashboard is viewed.
- Completing a Study, Quiz, Exam, or SRS review session on a given day
  causes that day to count toward the streak; a day with none of those
  completed does not extend the streak.
- The Lesson Catalog and all existing lesson-level modes remain fully
  reachable and functional from/alongside the dashboard.
