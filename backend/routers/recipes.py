"""GET /api/recipes, GET /api/recipes/{id}, POST /api/recipes.

Per docs/architecture.md §7 ("Recipes / Catalog" and "Admin"). Thin router:
parse/validate the request, run simple SELECT/INSERT statements, and return
schemas.py models. No aggregation logic lives here.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from .. import database
from ..schemas import IngredientOut, RecipeCreate, RecipeDetail, RecipeSummary

router = APIRouter()


def _fetch_recipe_detail(recipe_id: int, conn) -> Optional[RecipeDetail]:
    recipe = conn.execute(
        "SELECT id, title, category FROM recipes WHERE id = ?", (recipe_id,)
    ).fetchone()
    if recipe is None:
        return None
    ingredient_rows = conn.execute(
        "SELECT quantity, name FROM recipe_ingredients WHERE recipe_id = ? "
        "ORDER BY position ASC",
        (recipe_id,),
    ).fetchall()
    step_rows = conn.execute(
        "SELECT instruction FROM recipe_steps WHERE recipe_id = ? ORDER BY position ASC",
        (recipe_id,),
    ).fetchall()
    return RecipeDetail(
        id=recipe["id"],
        title=recipe["title"],
        category=recipe["category"],
        ingredients=[
            IngredientOut(quantity=row["quantity"], name=row["name"])
            for row in ingredient_rows
        ],
        steps=[row["instruction"] for row in step_rows],
    )


@router.get("/recipes", response_model=list[RecipeSummary])
def list_recipes(
    category: Optional[str] = Query(default=None),
    conn=Depends(database.get_db),
):
    if category:
        rows = conn.execute(
            "SELECT id, title, category FROM recipes WHERE category = ? "
            "ORDER BY title COLLATE NOCASE ASC",
            (category,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, title, category FROM recipes ORDER BY title COLLATE NOCASE ASC"
        ).fetchall()
    return [
        RecipeSummary(id=row["id"], title=row["title"], category=row["category"])
        for row in rows
    ]


@router.get("/recipes/{recipe_id}", response_model=RecipeDetail)
def get_recipe(recipe_id: int, conn=Depends(database.get_db)):
    detail = _fetch_recipe_detail(recipe_id, conn)
    if detail is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return detail


@router.post("/recipes", response_model=RecipeDetail, status_code=201)
def create_recipe(payload: RecipeCreate, conn=Depends(database.get_db)):
    # Pydantic validates `payload` (title, category, >=1 ingredient with a
    # non-empty name, >=1 non-empty step) before this function body runs at
    # all, so an invalid submission never reaches the INSERT statements
    # below (422, no partial write).
    try:
        cur = conn.execute(
            "INSERT INTO recipes (title, category) VALUES (?, ?)",
            (payload.title, payload.category),
        )
        recipe_id = cur.lastrowid
        for position, ingredient in enumerate(payload.ingredients):
            conn.execute(
                "INSERT INTO recipe_ingredients (recipe_id, position, quantity, name) "
                "VALUES (?, ?, ?, ?)",
                (recipe_id, position, ingredient.quantity, ingredient.name),
            )
        for position, step in enumerate(payload.steps):
            conn.execute(
                "INSERT INTO recipe_steps (recipe_id, position, instruction) VALUES (?, ?, ?)",
                (recipe_id, position, step),
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return _fetch_recipe_detail(recipe_id, conn)
