# Summary: Feature Decomposition (Stage 2)

- **Date:** 2026-08-31
- **Author / Executor:** Claude
- **Instruction file:** `instructions/build/02-decompose-features.md`
- **Commit:** `stage 02: decompose Recipe Box concept into features`

## Work Completed

Read `concept.md` for the Recipe Box app and broke it into five discrete
product capabilities. Each requirement in the concept maps to a feature
file; no implementation, workflow, or behavioral detail was written at this
stage — files stay at the "what capability exists" level.

This run is an unattended pipeline execution with no human gate available.
Per the Stage Manager's dispatch, routine open questions that would normally
be checked with a human were instead resolved using best judgment consistent
with `concept.md` and the stage's capability-level boundary; those calls are
recorded below under Key Decisions rather than left as blocking questions.

## Outputs Produced

- `features/01-recipe-catalog.md` — browsing the recipe catalog and viewing
  an individual recipe's details.
- `features/02-cook-mode.md` — step-by-step guided cooking with a checkbox
  per step.
- `features/03-meal-planner.md` — assigning recipes to days of the coming
  week.
- `features/04-shopping-list.md` — aggregated, checkable shopping list built
  from the week's planned recipes.
- `features/05-admin-recipe-creation.md` — adding new recipes to the
  catalog.

## Key Decisions

- **Recipe Catalog added as its own feature.** `concept.md` never names
  "browse/view recipes" explicitly, but Cook Mode ("walks through a
  recipe's steps") and Meal Planner ("assign recipes to days") both
  presuppose a way to see the recipe list and a recipe's details in order to
  pick one. Rather than leaving that capability implicit or folding it into
  Cook Mode/Meal Planner (which would blur their scope), it is broken out as
  a standalone prerequisite capability, mirroring how the concept's other
  capabilities are each scoped to one clear purpose.
- **Admin scoped strictly to adding recipes.** `concept.md` says only that
  Admin "allows the user to add new recipes" — nothing about editing or
  deleting existing recipes. Per the stage's "do not add features absent
  from concept.md" boundary, Admin was kept to recipe creation only; edit/
  delete were not assumed as implicit Admin sub-capabilities.
- **Meal Planner and Shopping List kept as two separate features.**
  `concept.md` introduces them in two separate sentences as two distinct
  capabilities ("Include a Meal Planner that... and a Shopping List
  that..."), even though Shopping List's data is derived entirely from Meal
  Planner state. They are functionally and purpose-wise distinct (planning
  what to cook vs. producing a list to shop with), so they are decomposed as
  two features rather than merged into one, consistent with how the concept
  itself separates them.
- **20-recipe seed dataset is not its own feature.** The requirement to
  start with 20 recipes across Breakfast/Main/Side/Dessert categories is a
  content/data-shape requirement, not a product capability in itself — it's
  called out here so it isn't silently dropped from downstream awareness,
  and is folded into the Recipe Catalog feature's description as the data
  the catalog holds. A later stage (feature briefs, system engineering, or
  architecture) is responsible for actually specifying/seeding it.
- **No category-management feature.** `concept.md` only says recipes have a
  category among a fixed handful (Breakfast, Main, Side, Dessert); it gives
  no basis for a capability to create, edit, or manage categories, so none
  was added.

## Open Questions & Concerns

None of the above rose to the level of a genuine blocker — each was a
routine scoping call within the concept's stated boundaries, resolved
per the unattended-run instructions and recorded above. No contradiction
or unresolvable ambiguity was found in `concept.md` itself.

For Stage 3 (briefs) to be aware of, though not blocking:
- Whether "the coming week" in Meal Planner means a fixed calendar week or a
  rolling 7-day window is unspecified; left for the brief stage to define
  as behavior.
- Whether a recipe can be removed from the Meal Planner once assigned (and
  how that reflects in the Shopping List) is behavior, not capability, and
  is left for the brief stage.

## Status

- [x] Complete
- [ ] Needs review
