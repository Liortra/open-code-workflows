"""Pydantic request/response models, per docs/architecture.md §7 (API
Contracts). Routers import from here and return/accept only these shapes.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

Category = Literal["Breakfast", "Main", "Side", "Dessert"]


# ---- Recipes / Catalog -----------------------------------------------

class RecipeSummary(BaseModel):
    id: int
    title: str
    category: Category


class IngredientOut(BaseModel):
    quantity: Optional[str] = None
    name: str


class RecipeDetail(BaseModel):
    id: int
    title: str
    category: Category
    ingredients: list[IngredientOut]
    steps: list[str]


# ---- Admin (create-only) ----------------------------------------------

class IngredientIn(BaseModel):
    quantity: Optional[str] = None
    name: str

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("ingredient name must not be empty")
        return stripped


class RecipeCreate(BaseModel):
    title: str
    category: Category
    ingredients: list[IngredientIn] = Field(min_length=1)
    steps: list[str] = Field(min_length=1)

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("title must not be empty")
        return stripped

    @field_validator("steps")
    @classmethod
    def steps_must_not_be_blank(cls, value: list[str]) -> list[str]:
        cleaned = []
        for step in value:
            stripped = step.strip()
            if not stripped:
                raise ValueError("step text must not be empty")
            cleaned.append(stripped)
        return cleaned


# ---- Meal Planner -------------------------------------------------------

class MealPlanEntryOut(BaseModel):
    id: int
    recipe_id: int
    title: str
    category: Category


class MealPlanDay(BaseModel):
    date: str
    weekday: str
    entries: list[MealPlanEntryOut]


class MealPlanResponse(BaseModel):
    days: list[MealPlanDay]


class MealPlanCreate(BaseModel):
    recipe_id: int
    date: str


class MealPlanCreateResponse(BaseModel):
    id: int
    recipe_id: int
    date: str


# ---- Shopping List --------------------------------------------------------

class ShoppingListItem(BaseModel):
    ingredient: str
    quantity: str
    checked: bool


class ShoppingListPatch(BaseModel):
    checked: bool


class ShoppingListPatchResponse(BaseModel):
    ingredient: str
    checked: bool
