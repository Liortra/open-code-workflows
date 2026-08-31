# Brief: Meal Planner

## Purpose

The Meal Planner exists so the user can decide ahead of time which recipes
they intend to cook on which days over the coming week, turning the static
Recipe Catalog into an actionable weekly plan. It is also the sole source of
truth the Shopping List (feature 04) draws from.

## Definition of "the coming week" *(judgment call — see summary)*

The Meal Planner always presents a **rolling 7-day window starting with
today and running through six days after today** (today + the next 6 days),
not a fixed Monday–Sunday calendar week. Each day slot is identified by its
actual calendar date (with its weekday name shown for readability, e.g.
"Monday, Sep 1"). As each day passes, the window shifts forward by one day,
dropping the day that just ended and picking up a new day six days out, so
the planner always shows "today through 6 days from now."

Rationale: "the coming week" most naturally reads as the week *ahead*,
starting now — a rolling window keeps every visible day still in the future
(or today), which fits a forward-looking planning tool better than a fixed
calendar week that could show several already-past days as still "open" for
planning depending on what day it is.

## Expected behavior

1. The Meal Planner shows 7 day slots covering today through 6 days from
   now, each labeled with its date and weekday name.
2. For any day slot in that window, the user can assign a recipe from the
   catalog to that day.
3. A single day can have zero, one, or multiple recipes assigned — the
   planner does not limit a day to exactly one recipe (e.g., a user may plan
   both a Main and a Side for the same day). Concept.md does not restrict a
   day to a single recipe, and a per-day cap isn't implied by "assign
   recipes to days." *(Judgment call — see summary.)*
4. The same recipe can be assigned to more than one day within the window
   (e.g., repeating a favorite twice in the week) — nothing limits a recipe
   to a single use.
5. For each day, the user can see which recipe(s) (title and category) are
   currently assigned to it, or that the day has nothing planned.
6. The user can remove a specific recipe from a day, clearing that
   assignment. The user can also change what's planned for a day by removing
   an existing assignment and adding a different recipe — planning is
   editable, not write-once. *(Judgment call — see summary: a planner that
   only ever accepted a single, permanent assignment per day would not
   support real planning/re-planning, which "lets the user assign recipes
   to days" implies as an ongoing, interactive activity.)*
7. Only recipes that exist in the Recipe Catalog can be assigned — there is
   no way to plan an ad hoc or free-text meal that isn't a real recipe.
8. Whatever is currently assigned across the 7-day window is exactly the
   input the Shopping List (feature 04) uses to build its aggregated list.

## Inputs / outputs

- **Inputs:** a recipe (from the catalog) and a target day to assign it to;
  a day + recipe pair to remove an existing assignment.
- **Outputs:** the 7-day window with, for each day, the list of currently
  assigned recipes (or an empty state if none).

## User-visible behavior

- A 7-day view (today plus the next 6 days), each day clearly dated.
- Each day shows its assigned recipe(s), or an indication that nothing is
  planned for that day yet.
- The user can add a recipe to any day in the window, remove a recipe from
  a day, and see the plan update immediately.

## Constraints

- Assignment is only possible within the current rolling 7-day window
  (today through 6 days out); a day that rolls out of the window (because
  it's now in the past) is no longer part of the plannable/editable set.
- Only existing catalog recipes may be assigned; there is no free-text
  meal entry.
- Category is not a restriction on assignment — any recipe, regardless of
  category, may be assigned to any day.

## Basic acceptance expectations

- Opening the planner on any given day shows exactly 7 day slots, correctly
  dated as today through 6 days later.
- Assigning a recipe to a day makes it appear under that day.
- Assigning a second, different recipe to the same day adds it alongside
  the first rather than replacing it.
- Removing an assigned recipe clears it from that day, and it no longer
  appears in that day's list.
- After removing a recipe from a day, that recipe's ingredients no longer
  contribute to the Shopping List (unless it's still assigned elsewhere in
  the window).
- The same recipe can be assigned to two different days at once.
