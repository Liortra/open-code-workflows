"""GET /api/shopping-list, PATCH /api/shopping-list/{ingredient}.

Per docs/architecture.md §7 ("Shopping List"). The list is derived on every
GET from whatever recipes are currently assigned within the rolling 7-day
window (date_utils) — no list state is persisted except the per-ingredient
checked flag. Combination logic lives entirely in shopping_logic.py.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from .. import database, date_utils, shopping_logic
from ..schemas import ShoppingListItem, ShoppingListPatch, ShoppingListPatchResponse

router = APIRouter()


def _current_aggregated(conn) -> list[shopping_logic.AggregatedItem]:
    window = date_utils.get_window()
    dates = [d for d, _ in window]
    date_placeholders = ",".join("?" for _ in dates)
    recipe_id_rows = conn.execute(
        f"SELECT DISTINCT recipe_id FROM meal_plan_entries WHERE date IN ({date_placeholders})",
        dates,
    ).fetchall()
    recipe_ids = sorted(row["recipe_id"] for row in recipe_id_rows)
    if not recipe_ids:
        return []
    id_placeholders = ",".join("?" for _ in recipe_ids)
    ingredient_rows = conn.execute(
        f"""
        SELECT recipe_id, position, quantity, name
        FROM recipe_ingredients
        WHERE recipe_id IN ({id_placeholders})
        ORDER BY recipe_id ASC, position ASC
        """,
        recipe_ids,
    ).fetchall()
    return shopping_logic.aggregate(ingredient_rows)


@router.get("/shopping-list", response_model=list[ShoppingListItem])
def get_shopping_list(conn=Depends(database.get_db)):
    aggregated = _current_aggregated(conn)
    checks = {
        row["ingredient_key"]: bool(row["checked"])
        for row in conn.execute(
            "SELECT ingredient_key, checked FROM shopping_list_checks"
        ).fetchall()
    }
    return [
        ShoppingListItem(
            ingredient=item["ingredient"],
            quantity=item["quantity"],
            checked=checks.get(item["ingredient_key"], False),
        )
        for item in aggregated
    ]


@router.patch("/shopping-list/{ingredient}", response_model=ShoppingListPatchResponse)
def patch_shopping_list_item(
    ingredient: str, payload: ShoppingListPatch, conn=Depends(database.get_db)
):
    key = shopping_logic.normalize_name(ingredient)
    aggregated = _current_aggregated(conn)
    match = next((item for item in aggregated if item["ingredient_key"] == key), None)
    if match is None:
        raise HTTPException(
            status_code=404,
            detail="Ingredient is not currently on the derived shopping list",
        )
    conn.execute(
        """
        INSERT INTO shopping_list_checks (ingredient_key, checked) VALUES (?, ?)
        ON CONFLICT(ingredient_key) DO UPDATE SET checked = excluded.checked
        """,
        (key, int(payload.checked)),
    )
    conn.commit()
    return ShoppingListPatchResponse(ingredient=key, checked=payload.checked)
