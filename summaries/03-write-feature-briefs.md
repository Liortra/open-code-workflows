# Summary: Feature Brief Writer (Stage 3)

- **Date:** 2026-08-31
- **Author / Executor:** Claude
- **Instruction file:** `instructions/build/03-write-feature-briefs.md`
- **Commit:** `stage 03: write behavioral briefs for all five features`

## Work Completed

Read `concept.md`, all five `features/*.md` files, and Stage 2's summary
(which flagged two open questions for this stage). Wrote one behavioral
brief per feature under `features/briefs/`, each covering Purpose, Expected
behavior, Inputs/outputs, User-visible behavior, Constraints, and Basic
acceptance expectations, per the stage instructions. No filenames, classes,
SQL, or implementation/architecture decisions were written.

This is an unattended pipeline run with no human gate available. Per the
Stage Manager's dispatch, routine underspecified behavior (including both
open questions Stage 2 flagged) was resolved using best judgment consistent
with `concept.md` and the feature files, rather than paused on. Each such
call is recorded below and inline in the relevant brief, marked as a
judgment call.

## Outputs Produced

- `features/briefs/01-recipe-catalog.md`
- `features/briefs/02-cook-mode.md`
- `features/briefs/03-meal-planner.md`
- `features/briefs/04-shopping-list.md`
- `features/briefs/05-admin-recipe-creation.md`

## Key Decisions

- **"The coming week" = a rolling 7-day window starting today** (today
  through 6 days from now, each day identified by actual calendar date),
  not a fixed Monday–Sunday calendar week. Rationale: "coming week" reads
  most naturally as the week *ahead*, starting now; a rolling window keeps
  every visible day still current-or-future, avoiding the confusion of a
  fixed calendar week showing several already-past days as still "open" for
  planning depending on what weekday it happens to be. The window shifts
  forward by one day as each day passes. This same definition is reused by
  the Shopping List brief ("the week" = the same window).
- **A planned day's assignment can be changed or cleared, not just set
  once.** The Meal Planner brief gives the user the ability to remove a
  recipe from a day and to replace a day's assignment. Rationale: concept.md
  describes the Meal Planner as something that "lets the user assign
  recipes to days" as an ongoing planning activity; a write-once planner
  that could never be corrected or re-planned would not be a good-faith
  reading of that as an interactive tool, and would also leave no way to
  keep the Shopping List accurate as plans change.
- **A day may have zero, one, or multiple recipes assigned; a recipe may be
  assigned to multiple days.** Concept.md says "assign recipes to days"
  without a stated one-recipe-per-day cap or a meal-type/slot concept
  (breakfast/lunch/dinner), and real planning commonly pairs a Main with a
  Side, or repeats a favorite recipe within the week. Neither restriction
  is implied, so neither was added.
- **Shopping List aggregation described behaviorally, not as a data
  model.** When the same ingredient appears in multiple planned recipes,
  the brief specifies the *user-visible* outcome (one combined line, not
  duplicate lines, with amounts shown together when they can't be cleanly
  combined) without prescribing how matching/combination is implemented.
- **Shopping List contents are fully plan-derived; no manual list
  editing.** Concept.md describes the list only as an aggregation of
  planned recipes' ingredients. The brief explicitly scopes out letting the
  user add arbitrary extra (non-recipe) items to the list, since that
  capability isn't implied anywhere in concept.md or the feature file, to
  avoid inventing new behavior.
- **Cook Mode: checkbox and step-navigation are independent actions.**
  Checking a step's box does not auto-advance to the next step, and moving
  between steps does not require the current step to be checked.
  Rationale: concept.md says Cook Mode "walks through a recipe's steps one
  at a time, with a checkbox per step" — two distinct stated capabilities
  (stepping and checking) with no stated coupling between them; keeping
  them independent avoids inventing a specific coupling behavior that isn't
  implied either way.
- **Cook Mode checkbox state persists for a recipe within a session, plus a
  reset action.** Leaving and returning to a recipe's Cook Mode within the
  same session preserves its checked steps (so an accidental navigation
  away doesn't lose progress), and the user can reset a recipe's checkmarks.
  The reset action is a minimal, behaviorally-implied addition: without it,
  cooking the same recipe a second time would show every step pre-checked
  from the first time, which undermines the stated purpose of "track
  progress while cooking."
- **Recipe Catalog supports filtering/viewing by category.** Not stated
  explicitly in concept.md or the feature file, but category is a defined
  attribute of every recipe and filtering-while-browsing is a minimal
  browsing convenience rather than a new capability, so it was included in
  the Expected Behavior as part of "browsing the catalog."
- **Admin recipe validation rules made explicit.** Concept.md and the
  feature file only say Admin "allows the user to add new recipes"; the
  brief specifies the minimal fields a recipe needs to exist at all (title,
  a category from the fixed set, at least one ingredient, at least one
  step) and that incomplete submissions are rejected with feedback, since
  "add new recipes" implies the recipe added is a usable one.

## Open Questions & Concerns

None of the above rose to the level of a genuine blocker — each was routine
underspecified behavior within the features' stated scope, resolved per the
unattended-run instructions and recorded above (and inline in the affected
briefs, marked as judgment calls). No contradiction or unresolvable
ambiguity was found between `concept.md` and the feature files.

For the System Engineer / Architect stages to be aware of, though not
blocking:
- The Shopping List's ingredient-combination behavior (brief 04) assumes
  ingredient text can sometimes be matched/combined across recipes and
  sometimes only shown side-by-side on one line when units/amounts don't
  align cleanly. How ingredients are represented and matched is left
  entirely to those stages, per this stage's behavioral-only scope.
- The Meal Planner's rolling 7-day window (today + 6 days) needs a real
  "today" reference at runtime; how that's determined (server clock, client
  clock, timezone handling) is an implementation concern for later stages.

## Status

- [x] Complete
- [ ] Needs review
