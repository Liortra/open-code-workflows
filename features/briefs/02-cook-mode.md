# Brief: Cook Mode

## Purpose

Cook Mode exists so a user actively cooking can follow a recipe without
losing their place, by focusing on one instruction at a time and letting
them mark steps as done as they go.

## Expected behavior

1. The user enters Cook Mode for a recipe selected from the Recipe Catalog.
2. Cook Mode shows exactly one step of the recipe's instructions at a time,
   in the order the recipe defines, along with an indicator of position
   (e.g., "Step 2 of 6") so the user always knows where they are in the
   recipe.
3. Each step has its own checkbox that the user can check to mark that step
   done, and uncheck to mark it not done again. Checking or unchecking a
   step's box is independent of moving between steps — checking a box does
   not by itself change which step is displayed, and moving to another step
   does not require the current step's box to be checked first. This keeps
   step-tracking (checkbox) and step-navigation (next/previous) as two
   separate, user-controlled actions rather than forcing one to trigger the
   other. *(Judgment call — see brief-writer's summary.)*
4. The user can move forward to the next step and backward to the previous
   step. On the first step there is no "previous" action available; on the
   last step there is no "next" action available, making the start and end
   of the recipe clear.
5. Each step's checked/unchecked state is remembered per recipe for the
   duration of the session: if the user leaves Cook Mode (e.g., returns to
   the recipe detail view or the catalog) and comes back to the same
   recipe's Cook Mode later in the same session, previously checked steps
   are still shown as checked. *(Judgment call — see summary.)*
6. The user can reset a recipe's Cook Mode progress, clearing all of that
   recipe's checkmarks back to unchecked, so that cooking the same recipe
   again later doesn't start with every step already marked done from a
   previous time. *(Judgment call — see summary.)*
7. The user can exit Cook Mode at any point, regardless of how many steps
   are checked — completing every checkbox is not required to leave.

## Inputs / outputs

- **Inputs:** the recipe selected to cook; next/previous navigation actions;
  per-step checkbox toggles; a reset action.
- **Outputs:** the currently displayed step's instruction text, its
  position indicator, its checkbox state, and the set of available
  navigation actions (previous/next, as applicable).

## User-visible behavior

- One instruction visible on screen at a time, with a clear sense of
  progress through the recipe (e.g., "Step X of N").
- A checkbox next to the current step the user can tick off.
- Next/Previous controls to move through the recipe.
- Returning to a recipe already partly checked off shows the same checked
  steps as before, until the user resets it.

## Constraints

- Only one step is displayed at a time — Cook Mode is distinct from the
  Recipe Catalog's detail view, which shows the entire step list at once.
- Step order shown in Cook Mode must match the recipe's defined step order.
- Checkbox/progress state is scoped per recipe (checking steps in one
  recipe's Cook Mode does not affect another recipe's checkboxes).

## Basic acceptance expectations

- Entering Cook Mode on a recipe with N steps starts on step 1 of N, with
  an unchecked checkbox and no "previous" action available.
- Repeatedly choosing "next" moves through steps 2..N in order; "previous"
  moves back correctly; neither action is offered past either end.
- Checking a step's box marks it done; leaving Cook Mode and re-entering it
  for the same recipe in the same session shows that step still checked.
- Using the reset action clears all checkmarks for that recipe back to
  unchecked.
- The user can exit Cook Mode at any step without being forced to check
  every box first.
