# Brief: Lesson Catalog

## Purpose

Gives the user a starting point for every session: a single place to see what
lessons exist and to jump into any of them. Without this, there is no way to
reach Study, Quiz, or Exam mode for a given lesson.

## Expected behavior

1. On opening the app, the user is shown a list (catalog) of all lessons.
2. There are 20 lessons in the catalog, each holding 10 vocabulary items.
3. Each lesson in the catalog is shown with at least an identifying title
   (e.g. its name or number) so the user can tell lessons apart.
4. The user selects a lesson from the catalog.
5. Selecting a lesson takes the user to a lesson-level screen where they can
   then choose Study, Quiz, or Exam mode for that lesson (the modes
   themselves are described in their own briefs).
6. New lessons and vocabulary added through the Admin feature (see
   `05-admin-content-management.md`) appear in the catalog without any
   separate action required.

## Inputs / outputs

- **Input:** the user's selection of a lesson from the catalog.
- **Output:** a view of the chosen lesson, from which the user proceeds to a
  mode (Study/Quiz/Exam).

## User-visible behavior

- A list/grid of lessons, each distinguishable from the others.
- Clicking or tapping a lesson opens that lesson.
- The catalog reflects the current set of lessons at all times — a lesson
  added via Admin shows up the next time the catalog is viewed.

## Constraints

- The catalog must be able to hold at least 20 lessons and must not silently
  drop or hide lessons beyond an arbitrary limit.
- Each lesson must have exactly 10 vocabulary items associated with it per
  the concept's starting content; the catalog itself does not enforce this
  count (that is a content/authoring concern — see
  `05-admin-content-management.md`), but it must be able to display lessons
  with 10 vocabulary items correctly.
- No user accounts exist (per the single-user, no-login scope of this app);
  the catalog is the same for anyone using the app.

## Basic acceptance expectations

- Opening the app shows a list of lessons.
- The list contains the 20 starting lessons.
- Selecting any lesson opens that lesson's screen.
- A lesson added through Admin appears in the catalog.
