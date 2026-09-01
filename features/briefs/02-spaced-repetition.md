# Brief: Spaced Repetition (SRS)

## Purpose

Tracks how well a learner recalls each individual vocabulary word over
time, across the entire catalog, and uses that history to surface a
cross-lesson "Due for Review" queue. Today, recall practice only happens
one lesson at a time (Study/Quiz/Exam mode for a chosen lesson); this adds
a way to review specifically the words a learner is weakest on, regardless
of which lesson they belong to.

## Decision recorded in this brief (per coordinator direction)

Spaced Repetition is fed **only** by its own, self-contained review
interaction described below. It does not read from, write to, or otherwise
change Quiz mode (which remains not persisted, per
`features/archive/v1/briefs/03-quiz-mode.md`) or Exam mode (which remains
exactly as it is today, per `features/archive/v1/briefs/04-exam-mode.md`).
Per-word recall history is created and updated exclusively by the learner
answering items presented through the SRS review queue itself.

## Expected behavior

1. The app maintains, for every vocabulary item across every lesson, a
   per-word recall history: at minimum, whether the learner's most recent
   review of that word was recalled correctly or not, and when it was last
   reviewed.
2. A new entry point, the "Due for Review" queue, is reachable independently
   of any single lesson (i.e. not nested under one lesson's screen the way
   Study/Quiz/Exam are) and presents vocabulary items that are due for
   review, drawn from across all lessons rather than from one lesson at a
   time.
3. A word is eligible to appear in the "Due for Review" queue based on its
   recall history: words never reviewed, or reviewed and found to be
   recalled poorly, or whose scheduled review interval has elapsed, are
   surfaced; words recently and successfully recalled are not due yet.
4. For each item in the queue, the learner is asked to recall the word (the
   same style of self-testing question used elsewhere in the app — a
   vocabulary item prompt with a way to answer) and indicates or is
   evaluated on whether they recalled it correctly.
5. Each answer within the review queue updates that word's recall history
   (correct/incorrect and last-reviewed timestamp) and adjusts when that
   word will next become due — words recalled correctly become due again
   later than words recalled incorrectly or not at all.
6. The learner can review as many due items as are available in a session;
   if no words are currently due, the queue indicates there is nothing to
   review right now rather than presenting non-due words.
7. The learner can return to the queue at any later time; the set of due
   words reflects the current recall history and elapsed time at that
   moment.
8. Existing Study, Quiz, and Exam mode behavior for a chosen lesson is
   unchanged; the review queue is an additional, cross-lesson way to
   practice, not a replacement for or modification of those modes.

## Inputs / outputs

- **Input:** the learner opening the "Due for Review" queue, and the
  learner's answer/recall response for each presented item.
- **Output:** a list of due vocabulary items to review; per-item
  correct/incorrect recording that updates that word's stored recall
  history and next-due scheduling; an indication when no items are
  currently due.

## User-visible behavior

- A new place in the app (not nested inside a single lesson) where the
  learner can start a review session spanning words from any/all lessons.
- Each review item shows a vocabulary prompt and lets the learner respond
  and find out whether they recalled it correctly, similar in spirit to
  Quiz mode's per-question feedback.
- If nothing is due, the learner sees a clear message that there is nothing
  to review right now instead of an empty or broken screen.
- Nothing about existing Lesson Catalog, Study, Quiz, Exam, or Admin screens
  changes as a result of this feature, other than the addition of the new
  review-queue entry point.

## Constraints

- Recall history is tracked per individual vocabulary word, not per lesson
  or per quiz/exam attempt.
- The review queue spans all lessons in the catalog, including lessons
  added later via Admin; it is not scoped to a single lesson.
- This feature does not change Quiz mode's existing behavior, including
  that Quiz attempts remain unsaved/not persisted.
- This feature does not change Exam mode's existing behavior, including its
  per-lesson saved score records; Exam answers are not read into or written
  from the SRS recall history.
- A word with no review history yet (never seen in the queue) is treated as
  due, so every vocabulary item is eventually reachable through the review
  queue.
- The review queue must correctly include vocabulary items added later
  through Admin, without requiring any separate setup step.

## Basic acceptance expectations

- Opening the "Due for Review" queue shows vocabulary items due across more
  than one lesson (when more than one lesson has due items), not only the
  most recently visited lesson.
- Answering a review item updates that specific word's recall history and
  changes whether/when it appears again in the queue.
- A word marked as recalled correctly does not immediately reappear in the
  same or next review session; a word recalled incorrectly (or never
  reviewed) is eligible to appear.
- When no words are due, the queue clearly communicates that rather than
  showing an empty list with no explanation.
- Quiz mode continues to produce no saved record after the learner leaves
  it, exactly as before.
- Exam mode continues to save per-lesson results exactly as before, with no
  new dependency on or interaction with SRS data.
