# Environment Notes

## Stack

- **Backend:** Python 3.13, FastAPI, served by Uvicorn.
- **Persistence:** SQLite via Python's standard-library `sqlite3` module. No
  ORM or database driver is pinned in `requirements.txt`; if the architecture
  stage decides an ORM (e.g. SQLAlchemy) is warranted, that is a deviation
  from this environment and must be flagged per its own instructions.
- **Frontend:** Static HTML/CSS/JS, styled with Bootstrap loaded from a CDN
  (`<link>`/`<script>` tags, no npm/Node.js toolchain, no build step).
- **Serving model:** A single FastAPI process serves both the JSON API and
  the static frontend assets (e.g. via Starlette's `StaticFiles`). There is
  no separate frontend dev server.
- **Text-to-Speech:** Client-side only, via the browser's built-in
  `SpeechSynthesis` API. No backend involvement, no external TTS service, no
  API key.

## Prerequisites

- Python 3.13 available on `PATH` as `python3.13` (override with the
  `PYTHON_BIN` env var if your interpreter is named differently).
- No Node.js/npm required — the frontend has no build step.
- Internet access at runtime for the Bootstrap CDN (per the chosen
  "CDN link" delivery option); the app has no other external network
  dependency.

## Setup / run

- `./install.sh` creates a `.venv` virtual environment and installs
  `requirements.txt` into it. Also ensures `./tmp/` exists (gitignored
  scratch space for logs, per `instructions/build/00-README.md`).
- `./run.sh` starts the app with `uvicorn backend.main:app --reload` on
  `0.0.0.0:8000` (override with `HOST`/`PORT` env vars).

## Assumptions / caveats for downstream stages

- **Entry point convention:** `run.sh` assumes the backend exposes a FastAPI
  instance named `app` importable as `backend.main:app` (i.e.
  `backend/main.py`). If Stage 6 organizes the backend differently, it is
  expected to update the import target in `run.sh` accordingly (per Stage 6's
  own instructions on run-script/module-layout conflicts).
- **Static frontend mount:** the architecture/backend stages should mount the
  `frontend/` folder as static files from the FastAPI app (single-process
  serving model) rather than introducing a second server process.
- **SQLite file location:** not yet decided — this is left to the
  architecture stage. Whatever path is chosen should live under the project
  root and be covered by the `*.db` / `*.sqlite3` entries already added to
  `.gitignore`.
- **No auth/session dependency:** the app is single-user/no-login per the
  concept, so no auth-related packages (e.g. session/JWT libraries) are
  included here. If Admin content management needs an auth gate later, that
  addition must be flagged as an environment deviation.
- Only tested for local development; no production deployment (e.g. WSGI
  hardening, HTTPS, process manager) is in scope.
