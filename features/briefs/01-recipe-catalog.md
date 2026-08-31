# Brief: Recipe Catalog

## Purpose

The Recipe Catalog is the entry point for discovering recipes. It exists so
the user has a way to see what recipes are available and inspect a recipe's
full details before deciding to cook it (Cook Mode) or schedule it (Meal
Planner). Without it, neither of those features would have a way to select a
recipe.

## Expected behavior

1. When the user opens the catalog, they see a list of all recipes currently
   in the system, with each entry showing at least the recipe's title and
   category.
2. The user can narrow the list to a single category (Breakfast, Main, Side,
   or Dessert) and return to seeing all recipes. This is a browsing aid, not
   a separate capability — category is a defining attribute of every recipe,
   so being able to view the list by category is part of "browsing the
   catalog."
3. Selecting a recipe from the list opens that recipe's detail view, showing
   its title, category, full ingredient list, and full ordered step-by-step
   instructions.
4. From a recipe's detail view, the user can proceed into Cook Mode for that
   recipe, or assign it to a day in the Meal Planner (the catalog is the
   shared starting point for both of those features; how the user reaches
   them is described in this brief only as "the recipe is selectable from
   here," with the destination features' own briefs covering what happens
   next).
5. The catalog always reflects the current full set of recipes: the initial
   seed recipes plus any recipes since added through Admin Recipe Creation.
   No separate step is needed to make a newly created recipe show up.

## Inputs / outputs

- **Inputs:** none required to browse; an optional category choice to filter
  the displayed list; a recipe selection to view its details.
- **Outputs:** a list of recipe summaries (title, category); a detail view
  for a selected recipe (title, category, ingredients, steps).

## User-visible behavior

- A list/grid of recipes, each showing title and category at a glance.
- A way to filter that list down to one category at a time.
- Clicking/selecting a recipe shows a dedicated view with everything needed
  to know what the recipe is and how to make it.

## Constraints

- The catalog is read-only from the user's point of view: creating a new
  recipe is out of scope here and belongs entirely to Admin Recipe Creation
  (feature 05). The catalog does not offer editing or deleting recipes —
  that capability doesn't exist anywhere in this product per the feature
  decomposition.
- Only the four fixed categories (Breakfast, Main, Side, Dessert) are used
  for organizing and filtering; there is no way to add, rename, or manage
  categories.
- The catalog must contain at least the seed set of 20 recipes spread across
  the four categories at first run, plus any recipes added afterward via
  Admin.

## Basic acceptance expectations

- With the seed data loaded, opening the catalog shows at least 20 recipes
  spanning all four categories.
- Selecting any recipe opens a detail view containing its title, category,
  full ingredient list, and full step list.
- Filtering by a category shows only recipes belonging to that category, and
  clearing the filter restores the full list.
- A recipe created via Admin Recipe Creation appears in the catalog listing
  and is viewable the same way as a seed recipe.
