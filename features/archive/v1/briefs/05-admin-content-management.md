# Brief: Admin Content Management

## Purpose

Lets the app's content grow beyond the initial 20 lessons / 10 vocab each,
without requiring a code change, by giving the user a way to add new lessons
and vocabulary directly in the app.

## Expected behavior

1. The user navigates to the Admin section of the app.
2. From Admin, the user can create a new lesson by providing at least a
   lesson title/name.
3. From Admin, the user can add new vocabulary items to any lesson
   (existing or newly created) by providing at least the Hebrew word and its
   meaning (translation).
4. Newly added lessons appear in the Lesson Catalog (see
   `01-lesson-catalog.md`) immediately, without any separate publish step.
5. Newly added vocabulary items appear in that lesson's Study, Quiz, and
   Exam modes immediately.

## Inputs / outputs

- **Input:** a new lesson's title; a vocabulary item's Hebrew word and
  meaning, and the lesson it belongs to.
- **Output:** an updated lesson catalog and/or updated lesson vocabulary,
  visible to the rest of the app right away.

## User-visible behavior

- An Admin area with a form/control to add a lesson (title).
- An Admin area with a form/control to add a vocabulary item (Hebrew word,
  meaning, target lesson).
- Immediate reflection of additions elsewhere in the app (catalog, lesson
  content) — no separate "publish" or "refresh" step needed.

## Constraints

- Admin is scoped strictly to *adding* new lessons and new vocabulary; it
  does not include editing or deleting existing lessons/vocabulary — the
  concept and feature file describe only adding.
- Per the single-user, no-login scope of this app, Admin is not a separate
  authenticated role — it is simply a section of the app any user of the app
  can reach and use.
- A vocabulary item must belong to exactly one lesson.
- Lessons and vocabulary added via Admin are held to the same shape as the
  starting content (a lesson has a title; a vocabulary item has a Hebrew
  word and a meaning) — Admin does not introduce a different content model.

## Basic acceptance expectations

- Adding a lesson through Admin makes it appear in the Lesson Catalog.
- Adding a vocabulary item to a lesson through Admin makes it available in
  that lesson's Study, Quiz, and Exam modes.
- There is no way to edit or delete existing lessons/vocabulary through
  Admin (only adding is supported).
