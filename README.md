# Recipe Box

A personal recipe box and meal-planning web app for home cooks. Recipe Box
lets you browse a catalog of recipes, cook through one step at a time without
losing your place, plan meals across a rolling week, and generate a single
combined shopping list from whatever you've planned.

Built end-to-end by an agentic 9-stage build pipeline (see
`instructions/build/00-README.md`) from the seed concept in `concept.md`.

## Features

- **Recipe Catalog** — browse all recipes (title + category), filter by
  category (Breakfast, Main, Side, Dessert), and open a recipe's full detail
  view (ingredients + ordered steps). Read-only: there is no edit/delete
  capability anywhere in the app, by design.
- **Cook Mode** — walk through a recipe one step at a time ("Step X of N"),
  with a per-step checkbox, Next/Previous navigation, and a Reset action.
  Checkbox/step-position state lives entirely in the browser
  (`sessionStorage`, per recipe) and is remembered for the browser session
  but never sent to the backend.
- **Meal Planner** — a rolling 7-day window (today through 6 days out, not a
  fixed calendar week) where you can assign any catalog recipe to any day.
  A day can hold zero, one, or several recipes; the same recipe can be
  assigned to more than one day; assignments can be added and removed
  freely.
- **Shopping List** — automatically derived from everything currently
  planned in the Meal Planner's 7-day window. Each distinct ingredient
  appears once, with quantities combined where units match (and shown
  together on one line, unsummed, where they don't). Items are checkable
  while shopping and stay in sync with the plan with no manual "refresh"
  step.
- **Admin: Add a Recipe** — a form to add a new recipe (title, category,
  ingredients, steps). Newly created recipes are immediately usable
  everywhere a seed recipe is — Catalog, Cook Mode, Meal Planner — with no
  extra publish step. Admin can only create recipes; there is no edit or
  delete capability.

The full behavioral spec for each feature is in `features/briefs/*.md`.

## Stack

- **Backend:** Python 3.13, FastAPI, served by Uvicorn.
- **Persistence:** SQLite via the Python standard-library `sqlite3` module
  (no ORM). Database file: `backend/data/app.db` (gitignored, created and
  seeded automatically on first run).
- **Frontend:** Static, multi-page HTML/CSS/JS styled with Bootstrap 5
  loaded from a CDN — no SPA framework, no npm/Node.js, no build step.
- **Serving model:** A single FastAPI process serves both the JSON API
  (under `/api`) and the static frontend files. Requires internet access at
  load time for the Bootstrap CDN; no other external dependency.

Full technical detail (file layout, data model, API contracts) is in
`docs/architecture.md`.

## Setup and running

Prerequisite: Python 3.13 available as `python3.13` on `PATH` (or set
`PYTHON_BIN` to a compatible interpreter).

```bash
./install.sh   # creates .venv, installs requirements.txt
./run.sh       # starts the app on http://localhost:8000
```

`./run.sh` respects `HOST`/`PORT` environment variables (defaults
`0.0.0.0:8000`). On first run, `backend/data/app.db` is created and seeded
automatically with 20 starter recipes spread across the four categories —
no manual data-loading step is needed. Open `http://localhost:8000` in a
browser once the server is up.

## Implementation summary

The app was built by the pipeline's stages 1–9 in order: a human-supplied
concept (`concept.md`) was decomposed into five features (`features/*.md`),
each written up as a detailed behavioral brief (`features/briefs/*.md`);
an environment was pinned (`environment-notes.md`, `requirements.txt`,
`install.sh`, `run.sh`); a technical architecture was authored
(`docs/architecture.md`) covering file layout, the SQLite schema, shopping
list aggregation rules, and every API contract; the backend (`backend/`)
and frontend (`frontend/`) were implemented against that architecture; and
the whole system was verified against the approved specifications
(`docs/verification-report.md`).

All five features — Recipe Catalog, Cook Mode, Meal Planner, Shopping List,
Admin Recipe Creation — were implemented as specified in their briefs, with
no invented endpoints, fields, or capabilities beyond what the architecture
and briefs define (e.g. no editing or deleting recipes anywhere in the
product).

## Status

**Feature-complete and verified at the feature level.** The one
blocking-severity backend defect found by verification (SQLite
thread-safety under concurrent requests) has since been **fixed** — see
Known Issues below.

## Verification results (as delivered by Stage 8)

Stage 8 performed a genuinely clean install (`.venv` and `backend/data/app.db`
deleted before `./install.sh`), then verified every feature's own "Basic
acceptance expectations" via direct `curl` calls against every `/api/*`
endpoint (including negative/validation cases) and via a real headless
Chromium browser (Playwright) driving actual clicks, form fills, and DOM
assertions against the running app. Full detail and evidence are in
`docs/verification-report.md`.

| Feature | Result |
|---|---|
| Recipe Catalog | PASS |
| Cook Mode | PASS |
| Meal Planner | PASS |
| Shopping List | PASS (one non-blocking spec ambiguity — see Known Issues) |
| Admin Recipe Creation | PASS |
| **Backend concurrency (cross-cutting)** | **FAIL at the time of Stage 8** — reproduced reliably (~90%+ failure rate under concurrent load in Stage 8's testing) across every `/api/*` route, both reads and writes. **Fixed** in a post-verification bug-fix pass — see Known Issues. |

Every feature's own behavioral acceptance criteria pass under **isolated,
sequential** use, which is exactly how the shipped frontend calls the API
today. The concurrency defect below does not surface under that
single-request-at-a-time usage pattern, which is why the per-feature rows
above still show PASS even though the cross-cutting defect exists and is
rated blocking-severity by Stage 8.

## Known issues

### Blocking: SQLite thread-safety bug — FIXED

**Status: fixed.** `backend/database.py`'s `get_connection()` now opens
each connection with `sqlite3.connect(DB_PATH, check_same_thread=False)`.
This is the correct, complete fix for this codebase specifically because
`get_db()` (the FastAPI dependency every router uses) already opens a
*fresh* connection per request and closes it at the end of that same
request (see `get_db`'s `try`/`finally` in `backend/database.py`) — no
connection object is ever shared or reused across requests or threads.
`check_same_thread=False` only disables sqlite3's same-thread assertion; it
does not by itself make concurrent access to one shared connection safe,
but there was no shared connection here to begin with, so no additional
locking or connection-pooling was needed. Retested with the same method
Stage 8 used (`concurrent.futures`-driven truly concurrent requests): 155
concurrent `GET` requests across `/api/recipes`, `/api/meal-plan`, and
`/api/shopping-list` (including a 60-request burst) plus concurrent
`PATCH /api/shopping-list/{ingredient}` and `POST /api/meal-plan` calls —
**0 failures, 0 `ProgrammingError`s, 0 `500`s**, versus Stage 8's ~96%
failure rate on the same pattern. The original findings below are kept for
the historical record.

### Blocking: SQLite thread-safety bug (unfixed) — historical, see above

`backend/database.py`'s connection helper (`get_connection()`, used by the
`get_db` FastAPI dependency) opens its SQLite connection with plain
`sqlite3.connect(DB_PATH)`, which defaults to `check_same_thread=True`.
Because FastAPI runs synchronous endpoint/dependency code across a
threadpool, a connection can be created on one worker thread and used/torn
down on another whenever two requests are in flight at overlapping moments,
raising `sqlite3.ProgrammingError: SQLite objects created in a thread can
only be used in that same thread`.

- **Reproduces reliably:** Stage 8 measured a 96% failure rate (48/50)
  firing repeated concurrent `GET /api/recipes` requests, and confirmed the
  same failure firing concurrently against `GET /api/meal-plan`,
  `GET /api/shopping-list`, concurrent `PATCH /api/shopping-list/{ingredient}`
  calls, and concurrent `POST /api/meal-plan` calls — it affects every
  router (`recipes.py`, `meal_plan.py`, `shopping_list.py`) and both reads
  and writes, because all three depend exclusively on `database.get_db`.
- **Trigger conditions:** two browser tabs open at once, a user
  double-clicking two different Shopping List checkboxes (each issuing its
  own independent request), or simply two requests landing close together.
- **Frontend mitigation already in place:** Stage 7 discovered this during
  its own testing (the Meal Planner page originally issued two `fetch`
  calls concurrently via `Promise.all`) and sequenced those two calls in
  `planner.js` instead of firing them together. This avoids the one
  concurrent-call pattern the frontend itself produced, but does **not**
  fix the underlying backend defect — any other source of overlapping
  requests (two tabs, rapid double-clicks, etc.) can still trigger it.
- **Root cause and fix location, identified but not applied (out of Stage 8's
  and this stage's scope):** `backend/database.py`'s `get_connection()`
  (around line 58) needs `sqlite3.connect(DB_PATH, check_same_thread=False)`
  combined with a lock, a per-thread connection strategy, or a connection
  pool. `grep -rn "sqlite3.connect" backend/` shows this is the only
  connection-acquisition path in the backend, so this single location
  addresses the entire defect.

### Non-blocking: Shopping List quantity ambiguity for a recipe repeated in the window

The Meal Planner brief explicitly allows the same recipe to be assigned to
more than one day within the 7-day window. The Shopping List's aggregation
query selects `DISTINCT recipe_id` from the planned entries before pulling
ingredients, so a recipe assigned to two different days has its ingredients
counted **once**, not doubled. Neither the Meal Planner nor the Shopping
List brief explicitly states which behavior is expected here; Stage 8 read
the Shopping List brief's "needed by more than one currently planned
recipe" language as referring to *different* recipes sharing an ingredient
(which is what was tested and passes), not a single recipe repeated. A user
who plans to cook the same dish twice in a week would likely expect
ingredients for two batches — this is recorded as a genuine ambiguity for a
human or a future pass to resolve, not a defect.

### Scope limitations, by design (not defects)

- Cook Mode's step/checkbox progress is intentionally session-only
  (`sessionStorage`) and resets on browser/tab close — there is no
  persistent, cross-session cook-mode progress, per the app's no-auth/
  no-session-store design.
- The app is single-user with no login/auth anywhere.
- Only local development is supported — no production hardening (HTTPS,
  process manager, WSGI tuning) is in scope.
- The Bootstrap CDN requires internet access at page-load time; the API and
  raw HTML/JS work offline, but pages will render unstyled without it.
- Unit matching in Shopping List quantity combination is a case-insensitive
  exact string match (e.g. "cup" and "cups" are treated as different units
  and shown on the same line unsummed rather than combined) — an accepted
  simplification, not a bug, per `docs/architecture.md` §5.

## Suggested next actions for a future pass

1. ~~Fix the SQLite concurrency bug in `backend/database.py`~~ — **done**,
   see Known Issues above.
2. **Resolve the repeated-recipe Shopping List ambiguity** — decide (with
   the product owner) whether a recipe planned twice in the window should
   double its ingredient quantities, and update `features/briefs/04-shopping-list.md`
   and `backend/routers/shopping_list.py` accordingly if so.
3. Consider automated tests (unit tests for `shopping_logic.py` and
   `date_utils.py`, and integration tests for the API) — none exist today;
   all verification to date has been manual/scripted `curl` and browser
   sessions run once per stage.
4. Consider a load/concurrency test in CI to prevent regression of the
   SQLite fix above.

## Repository layout

See `instructions/build/00-README.md` for the full build-pipeline layout
and conventions. In brief:

```
concept.md                    Product seed (Stage 1)
features/*.md                 Feature decomposition (Stage 2)
features/briefs/*.md          Feature briefs (Stage 3)
requirements.txt, install.sh,
run.sh, environment-notes.md  Environment (Stage 4)
docs/architecture.md          Technical architecture (Stage 5)
backend/                      FastAPI + SQLite backend (Stage 6)
frontend/                     Bootstrap static frontend (Stage 7)
docs/verification-report.md   Verification results (Stage 8)
README.md                     This file (Stage 9)
summaries/                    Per-stage summaries
```
