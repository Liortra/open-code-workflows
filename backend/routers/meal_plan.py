"""GET/POST /api/meal-plan, DELETE /api/meal-plan/{id}.

Per docs/architecture.md §7 ("Meal Planner"). Calls date_utils for the
rolling 7-day window so it can never disagree with shopping_list.py about
what "the coming week" means.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response

from .. import database, date_utils
from ..schemas import (
    MealPlanCreate,
    MealPlanCreateResponse,
    MealPlanDay,
    MealPlanEntryOut,
    MealPlanResponse,
)

router = APIRouter()


@router.get("/meal-plan", response_model=MealPlanResponse)
def get_meal_plan(conn=Depends(database.get_db)):
    window = date_utils.get_window()
    dates = [d for d, _ in window]
    date_placeholders = ",".join("?" for _ in dates)
    rows = conn.execute(
        f"""
        SELECT mp.id AS id, mp.recipe_id AS recipe_id, mp.date AS date,
               r.title AS title, r.category AS category
        FROM meal_plan_entries mp
        JOIN recipes r ON r.id = mp.recipe_id
        WHERE mp.date IN ({date_placeholders})
        ORDER BY mp.date ASC, mp.id ASC
        """,
        dates,
    ).fetchall()

    entries_by_date: dict[str, list[MealPlanEntryOut]] = {}
    for row in rows:
        entries_by_date.setdefault(row["date"], []).append(
            MealPlanEntryOut(
                id=row["id"],
                recipe_id=row["recipe_id"],
                title=row["title"],
                category=row["category"],
            )
        )

    days = [
        MealPlanDay(date=d, weekday=weekday, entries=entries_by_date.get(d, []))
        for d, weekday in window
    ]
    return MealPlanResponse(days=days)


@router.post("/meal-plan", response_model=MealPlanCreateResponse, status_code=201)
def create_meal_plan_entry(payload: MealPlanCreate, conn=Depends(database.get_db)):
    recipe = conn.execute(
        "SELECT id FROM recipes WHERE id = ?", (payload.recipe_id,)
    ).fetchone()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    if not date_utils.in_window(payload.date):
        raise HTTPException(
            status_code=400,
            detail="Date is outside the current 7-day planning window",
        )
    cur = conn.execute(
        "INSERT INTO meal_plan_entries (recipe_id, date) VALUES (?, ?)",
        (payload.recipe_id, payload.date),
    )
    conn.commit()
    return MealPlanCreateResponse(
        id=cur.lastrowid, recipe_id=payload.recipe_id, date=payload.date
    )


@router.delete("/meal-plan/{entry_id}", status_code=204)
def delete_meal_plan_entry(entry_id: int, conn=Depends(database.get_db)):
    row = conn.execute(
        "SELECT id FROM meal_plan_entries WHERE id = ?", (entry_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Meal plan entry not found")
    conn.execute("DELETE FROM meal_plan_entries WHERE id = ?", (entry_id,))
    conn.commit()
    return Response(status_code=204)
