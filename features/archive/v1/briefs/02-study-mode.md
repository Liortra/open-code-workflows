# Brief: Study Mode

## Purpose

Lets the user learn a lesson's vocabulary at their own pace before being
tested on it, with no pressure, scoring, or time limit.

## Expected behavior

1. The user enters Study mode for a chosen lesson (from the Lesson Catalog).
2. The user is shown the lesson's 10 vocabulary items, one at a time or as a
   browsable list (implementation detail left open — the requirement is that
   the user can view each item).
3. For each vocabulary item, the user sees the Hebrew word and its meaning
   (translation) together, so no guessing or answering is required.
4. The user can play the spoken pronunciation of any vocabulary item using
   the Text-to-Speech feature (see `06-text-to-speech.md`).
5. The user can move between vocabulary items freely, in any order and any
   number of times, until they choose to leave Study mode.
6. Leaving Study mode returns the user to the lesson screen, where they may
   choose Quiz or Exam mode next.

## Inputs / outputs

- **Input:** the user's navigation between vocabulary items within the
  lesson, and optional taps to hear pronunciation.
- **Output:** display of each vocabulary item's Hebrew word and meaning, and
  audio playback on request. No score or result is produced by Study mode.

## User-visible behavior

- The user sees Hebrew word + meaning shown together for each item — never
  hidden or asked as a question.
- A control (e.g. a speaker icon/button) next to each item plays its
  pronunciation.
- Progress through Study mode is not graded, timed, or scored, and nothing
  about a Study session is recorded or shown as a result afterward.

## Constraints

- Study mode must never quiz, grade, or score the user; it is purely
  presentational/review.
- All 10 vocabulary items of the lesson must be reachable from Study mode.
- Study mode has no pass/fail condition and no time limit.

## Basic acceptance expectations

- Entering Study mode for a lesson shows that lesson's vocabulary with
  answers visible (not hidden).
- The user can revisit any vocabulary item any number of times.
- Playing pronunciation works for each vocabulary item.
- No score, grade, or history entry is produced by using Study mode.
