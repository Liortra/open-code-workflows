# Brief: Admin Recipe Creation

## Purpose

Admin Recipe Creation exists so the user can grow the recipe collection
beyond the initial seed set, adding their own recipes for the Catalog, Cook
Mode, and Meal Planner to use.

## Expected behavior

1. The user accesses an Admin area and is presented with a way to create a
   new recipe.
2. To create a recipe, the user provides:
   - a title,
   - a category, chosen from the fixed set (Breakfast, Main, Side, Dessert),
   - an ingredient list (one or more ingredient entries),
   - step-by-step instructions (one or more ordered steps).
3. On submission, required fields are checked: a non-empty title, a category
   from the fixed set, at least one ingredient, and at least one step.
4. If any required field is missing or invalid, the recipe is not created
   and the user is told what needs to be fixed, so they can correct and
   resubmit.
5. On successful creation, the new recipe is added to the collection and
   becomes immediately usable everywhere an existing recipe is: it appears
   in the Recipe Catalog, can be opened in Cook Mode, and can be assigned to
   a day in the Meal Planner — exactly like a seed recipe, with no extra
   step required to "publish" it.

## Inputs / outputs

- **Inputs:** title (text), category (a choice among the four fixed
  categories), ingredients (one or more text entries), steps (one or more
  ordered text entries).
- **Outputs:** on success, a new recipe added to the collection; on
  failure, feedback identifying what's missing or invalid, with no partial
  or incomplete recipe created.

## User-visible behavior

- A form/flow for entering a new recipe's title, category, ingredients, and
  steps.
- Clear feedback if something required is missing when the user tries to
  submit.
- After a successful submission, the new recipe is visible in the Recipe
  Catalog like any other recipe.

## Constraints

- Category must be one of the four fixed categories (Breakfast, Main, Side,
  Dessert); there is no way to create, rename, or otherwise manage
  categories from Admin.
- Admin's scope is limited to creating new recipes. Editing or deleting an
  existing recipe (seed or user-added) is out of scope for this feature —
  concept.md only describes adding recipes, and no editing/deleting
  capability exists anywhere in this product.
- A recipe cannot be created without a title, a valid category, at least
  one ingredient, and at least one step.

## Basic acceptance expectations

- Submitting a complete, valid new recipe (title, valid category, at least
  one ingredient, at least one step) results in it appearing in the Recipe
  Catalog afterward.
- Submitting with a missing title, missing/invalid category, no
  ingredients, or no steps is rejected, the user is informed why, and no
  recipe is added.
- A recipe created this way can be opened in Cook Mode and assigned to a
  day in the Meal Planner, the same as a seed recipe.
