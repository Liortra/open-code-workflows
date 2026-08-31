# Summary: System Engineer (Stage 4)

- **Date:** 2026-08-31
- **Author / Executor:** Claude (agent)
- **Instruction file:** `instructions/build/04-system-engineering.md`
- **Commit:** `stage 04: define reproducible dev/runtime environment`

## Work Completed

Defined the reproducible development/runtime environment for the Recipe Box
app, following the default stack named in `concept.md` (Bootstrap frontend,
FastAPI + SQLite backend, Python) and reviewing all five feature briefs in
`features/briefs/` for any environment implications. None of the briefs
(Recipe Catalog, Cook Mode, Meal Planner, Shopping List, Admin Recipe
Creation) introduce a need beyond the default stack — no file/image uploads,
no auth, no external APIs, no scheduling/date libraries beyond the Python
standard library. Verified the environment end-to-end: ran `./install.sh`
(creates `.venv`, installs pinned dependencies) and `./run.sh` (confirmed it
correctly launches Uvicorn and attempts to import `backend.main:app`, failing
only with `ModuleNotFoundError: No module named 'backend'`, as expected since
`backend/` does not exist until Stage 6).

## Outputs Produced

- `requirements.txt` — pins `fastapi==0.115.6` and `uvicorn[standard]==0.34.0`.
- `install.sh` — creates `.venv` with `python3.13`, installs dependencies,
  ensures `./tmp/` exists.
- `run.sh` — starts `uvicorn backend.main:app --host 0.0.0.0 --port 8000
  --reload` (overridable via `HOST`/`PORT` env vars).
- `.gitignore` — extended the pre-existing root `.gitignore` (which only had
  `.DS_Store`) to also exclude `.venv/`, `__pycache__/`, `*.pyc`, `*.db`,
  `*.sqlite3`, and `tmp/*` (except `tmp/.gitkeep`).
- `environment-notes.md` — documents the stack, prerequisites, setup/run
  steps, and assumptions/caveats for downstream stages.

## Key Decisions

- **No ORM pinned.** SQLite is accessed via the standard-library `sqlite3`
  module by default; if the Architect (Stage 5) decides an ORM (e.g.
  SQLAlchemy) is warranted, that's flagged in `environment-notes.md` as a
  deviation for that stage to declare explicitly, rather than pre-deciding it
  here.
- **Cook Mode's per-session checkbox state is expected to be client-side**
  (in-memory JS or `sessionStorage`), not a backend session store. The brief
  for Cook Mode requires state to persist "for the duration of the session"
  when navigating within Cook Mode, which is satisfiable without any
  server-side session package — this keeps the environment auth/session-free,
  consistent with the concept's single-user, no-login design. Flagged in
  `environment-notes.md` as a constraint downstream stages should respect
  (or explicitly deviate from and justify).
- **No seed-loading tooling pinned.** The concept's 20 starter recipes will
  need to be loaded somehow (fixture/migration/seed script), but that needs
  nothing beyond the Python standard library, so no extra package was added
  for it — left as an architecture/backend decision.
- **Python 3.13 via `python3.13` on `PATH`**, matching the convention used by
  the sibling app under this same pipeline (kept for consistency across
  builds from this repo template); verified present in this environment.
- **SQLite file location left undecided**, deferred to the Architect per its
  own instructions; `.gitignore` already covers `*.db`/`*.sqlite3` wherever
  it ends up under the project root.
- Extended (rather than replaced) the pre-existing root `.gitignore`, since
  it already contained `.DS_Store` from repo scaffolding — preserved that
  line and added the new environment-related entries.

## Open Questions & Concerns

- None blocking. The two "left to the architecture stage" items noted above
  (SQLite file path, and whether an ORM is introduced) are intentionally
  deferred, not open problems — Stage 5 owns them per the pipeline's
  division of labor.

## Status

- [x] Complete
- [ ] Needs review
