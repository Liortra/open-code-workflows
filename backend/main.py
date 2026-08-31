"""FastAPI app: mounts the API routers and the static frontend.

Single-process serving model per environment-notes.md — this app serves both
the JSON API (under /api) and the static frontend (everything else).
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .database import init_db
from .routers import admin, exam, lessons, quiz, study


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Hebrew Language Tutor", lifespan=lifespan)

app.include_router(lessons.router)
app.include_router(study.router)
app.include_router(quiz.router)
app.include_router(exam.router)
app.include_router(admin.router)

# `check_dir=False`: the frontend/ folder is Stage 7's output and may not
# exist yet when the backend is built/tested standalone. Routes above are
# registered first, so /api/* is matched before falling through to this
# catch-all static mount.
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount(
    "/", StaticFiles(directory=FRONTEND_DIR, html=True, check_dir=False), name="frontend"
)
