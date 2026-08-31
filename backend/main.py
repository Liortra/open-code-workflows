"""FastAPI() instance ("app"). Mounts the API routers under /api and the
static frontend at /, per docs/architecture.md §1/§2. This is the module
run.sh imports as `backend.main:app` (environment-notes.md's entry-point
convention).
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from . import database
from .routers import meal_plan, recipes, shopping_list

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(title="Recipe Box")

database.init_db()

app.include_router(recipes.router, prefix="/api")
app.include_router(meal_plan.router, prefix="/api")
app.include_router(shopping_list.router, prefix="/api")

# Single-process serving model (environment-notes.md): the same FastAPI app
# serves the static Bootstrap frontend from frontend/. That folder is
# Stage 7's output and does not exist yet at the time this backend stage
# runs, so the mount is conditional — this lets the backend boot and be
# smoke-tested on its own, and Stage 7's frontend/ will be served
# automatically, with no changes needed here, once it exists.
if FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
