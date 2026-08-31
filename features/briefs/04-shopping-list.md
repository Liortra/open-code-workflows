# Brief: Shopping List

## Purpose

The Shopping List exists so the user doesn't have to manually cross-reference
every planned recipe's ingredients when they go shopping. It turns the
week's Meal Planner assignments into one consolidated list of what to buy.

## Expected behavior

1. The Shopping List is derived from the Meal Planner: it includes the
   ingredients of every recipe currently assigned to any day in the
   coming-week window (as defined in the Meal Planner brief — today through
   6 days out).
2. Each distinct ingredient appears on the list as a single checkable entry.
3. When the same ingredient is called for by more than one currently planned
   recipe (e.g., "eggs" needed by both a planned breakfast recipe and a
   planned dessert recipe), the list shows it as one combined line rather
   than one line per contributing recipe — the user should never see the
   same ingredient listed twice just because it's used in two planned
   recipes. Where the amounts from the different recipes can be combined
   into one quantity, the entry shows the combined amount; where they can't
   be combined cleanly (e.g. incompatible units or free-text amounts), the
   entry still appears once, with the separate amounts shown together on
   that single line rather than as duplicate lines. *(Judgment call — see
   summary: this is described behaviorally, not as a data-model decision.)*
4. The user can check off an item once it's been picked up while shopping,
   and can uncheck it again if needed.
5. The list stays in sync with the Meal Planner automatically: assigning a
   new recipe to the week adds its ingredients to the list (merging with any
   existing matching entries), and removing a recipe's assignment removes
   the ingredients that recipe uniquely contributed. No separate "regenerate
   the list" action is needed.
6. If no recipes are currently planned for the week, the Shopping List has
   no items.

## Inputs / outputs

- **Inputs:** none needed to generate the list — it's derived automatically
  from the Meal Planner's current state; the user's check/uncheck actions
  per item.
- **Outputs:** the combined, checkable list of ingredients needed for
  everything currently planned for the week.

## User-visible behavior

- A single list of ingredients, each with a checkbox.
- No duplicate lines for an ingredient that's needed by more than one
  planned recipe — it's combined into one line.
- The list changes as the user adds or removes planned recipes in the Meal
  Planner, without any separate action to refresh it.
- Checking an item visually marks it done (and can be unchecked again).

## Constraints

- Only ingredients from recipes currently planned within the coming-week
  window are included; nothing from unplanned recipes appears.
- The list's contents (which ingredients appear) are fully determined by
  the current Meal Planner state — the user does not manually add arbitrary
  extra items (e.g., non-recipe items like "paper towels") to the list
  itself. Only the checked/unchecked state of each derived item is directly
  user-controlled. Concept.md describes the list only as an aggregation of
  planned recipes' ingredients, so manual list editing beyond checking items
  off is out of scope. *(Judgment call — see summary.)*

## Basic acceptance expectations

- With no recipes planned for the week, the Shopping List has zero items.
- With one recipe planned, the list shows exactly that recipe's ingredients.
- With two planned recipes that share an ingredient, that ingredient
  appears once on the list, not twice.
- Removing a planned recipe removes the ingredients only it contributed
  (ingredients still needed by another planned recipe remain on the list).
- Checking an item marks it done; unchecking it reverses that.
