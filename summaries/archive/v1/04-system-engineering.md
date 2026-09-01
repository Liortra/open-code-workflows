# Summary: System Engineer (Stage 04)

- **Date:** 2026-08-31
- **Author / Executor:** Claude Code (agent)
- **Instruction file:** `instructions/build/04-system-engineering.md`
- **Commit:** `stage 04: define environment for FastAPI + SQLite + Bootstrap stack`

## Work Completed

Defined a reproducible local development environment for the Hebrew Language
Tutor per the concept's stack (Bootstrap frontend, FastAPI + SQLite backend)
and the six approved feature briefs. Confirmed three environment decisions
with the user before proceeding: Bootstrap via CDN (no Node/npm), a single
FastAPI process serving both the API and the static frontend, and Python
3.13. Verified `install.sh` provisions cleanly end-to-end (venv creation +
dependency install succeeded).

## Outputs Produced

- `requirements.txt` — pins `fastapi==0.115.6` and `uvicorn[standard]==0.34.0`.
  No ORM/DB driver pinned; SQLite persistence uses the stdlib `sqlite3`
  module.
- `install.sh` — creates a `.venv` with Python 3.13, installs
  `requirements.txt`, and ensures `./tmp/` exists.
- `run.sh` — starts `uvicorn backend.main:app --reload` on `0.0.0.0:8000`
  (overridable via `HOST`/`PORT`).
- `.gitignore` — extended with `.venv/`, `__pycache__/`, `*.pyc`, `*.db`,
  `*.sqlite3`, and `tmp/*` (keeping `tmp/.gitkeep`).
- `environment-notes.md` — stack summary, prerequisites, setup/run
  instructions, and explicit assumptions flagged for downstream stages.
- `tmp/.gitkeep` — placeholder so the gitignored scratch folder exists in the
  worktree.

## Key Decisions

- **Bootstrap via CDN**, not vendored files or an npm build — keeps the
  environment to Python-only tooling (no Node.js required).
- **Single FastAPI process** serves both API and static frontend — simpler
  run script, one port, no CORS concerns between frontend/backend.
- **Python 3.13** pinned as the target interpreter.
- **No ORM pinned** — left to the architecture stage to decide whether
  stdlib `sqlite3` suffices or an ORM is warranted; added it as an explicit
  "flag if you deviate" note since backend/architecture stages are expected
  to adhere to this environment.

## Open Questions & Concerns

- `run.sh` assumes the backend entry point will be `backend/main.py` exposing
  `app` (imported as `backend.main:app`). Stage 6 may need to adjust this
  import path per its own instructions if it lays out the backend module
  differently — flagged in `environment-notes.md`.
- SQLite database file location/name is not decided here; left to the
  architecture stage, but `.gitignore` already covers `*.db`/`*.sqlite3`
  wherever it ends up under the project root.
- Unrelated working-tree state was observed at the start of this stage
  (deleted `LICENSE`/`README.md`/`concept-examples/*`, untracked
  `concept.md`) — not touched by this stage; flagging in case it's
  unintentional and needs attention separately from the pipeline.

## Status

- [x] Complete
- [ ] Needs review
