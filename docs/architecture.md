# Architecture — Recipe Box

Technical specification for implementation. Backend and frontend engineers
should be able to build independently from this document without guessing at
contracts.

## 1. Overview

A single-process FastAPI app serves both a JSON API and a static, multi-page
Bootstrap frontend (no SPA framework, no build step, per
`environment-notes.md`). Persistence is SQLite via the stdlib `sqlite3`
module (no ORM). Cook Mode's per-step checkbox state is entirely client-side
(browser `sessionStorage`) and has no backend surface, per
`environment-notes.md`'s no-auth/no-session-store constraint.

```
Browser (static HTML/CSS/JS + Bootstrap CDN)
   │  fetch() → JSON
   ▼
FastAPI app (single process, uvicorn)
   │  sqlite3
   ▼
backend/data/app.db
```

## 2. Project / File Structure

```
backend/
├── main.py                    # FastAPI() instance ("app"), mounts routers + static frontend
├── database.py                 # connection helper, schema creation, seeding on startup
├── seed_data.py                 # the 20 starter recipes, as plain data
├── schemas.py                    # Pydantic request/response models
├── date_utils.py                  # rolling 7-day window computation
├── shopping_logic.py               # ingredient normalization + quantity aggregation
├── routers/
│   ├── recipes.py                   # GET /api/recipes, GET /api/recipes/{id}, POST /api/recipes
│   ├── meal_plan.py                  # GET/POST /api/meal-plan, DELETE /api/meal-plan/{id}
│   └── shopping_list.py                # GET /api/shopping-list, PATCH /api/shopping-list/{ingredient}
└── data/
    └── app.db                          # SQLite file, created on first run (gitignored)

frontend/
├── index.html                 # Recipe Catalog
├── recipe.html                 # Recipe detail view
├── cook.html                    # Cook Mode
├── planner.html                  # Meal Planner (rolling 7-day window)
├── shopping-list.html             # Shopping List
├── admin.html                      # Admin: create a recipe
└── static/
    ├── css/
    │   └── app.css                    # small overrides on top of Bootstrap
    └── js/
        ├── api.js                       # fetch() wrappers for every endpoint below
        ├── catalog.js
        ├── recipe.js
        ├── cook.js                        # step navigation + sessionStorage checkbox state
        ├── planner.js
        ├── shopping-list.js
        └── admin.js
```

`backend/main.py` mounts `frontend/` as static files (`StaticFiles`) at `/`,
and the API routers under `/api`. This satisfies `run.sh`'s
`backend.main:app` import target and the single-process serving model from
`environment-notes.md`.

## 3. Module Boundaries

- **`database.py`** owns the SQLite connection, schema creation
  (`CREATE TABLE IF NOT EXISTS ...`), and first-run seeding. No router opens
  its own connection logic — all go through this module.
- **`seed_data.py`** is pure data (20 recipes spanning Breakfast, Main, Side,
  Dessert). It has no behavior; `database.py` reads it once, on first run,
  when `recipes` is empty.
- **`date_utils.py`** is the single place that computes "today through 6
  days from now" (a list of `(date, weekday_name)` pairs) and validates
  whether a given date falls inside that window. Both `meal_plan.py` and
  `shopping_list.py` call into it so the window definition can never diverge
  between the two features.
- **`shopping_logic.py`** is the single place that normalizes ingredient
  names (for grouping/matching) and combines quantities across recipes. It
  is pure/stateless — it takes rows already fetched from the DB and returns
  the aggregated list — so it can be reasoned about (and tested)
  independently of SQL or HTTP.
- **Routers** are thin: parse/validate the request, call `database.py` /
  `date_utils.py` / `shopping_logic.py`, return a `schemas.py` model. No SQL
  or aggregation logic lives in a router body directly beyond simple
  `SELECT`s/`INSERT`s/`DELETE`s.
- **Frontend JS modules** are one per screen (`catalog.js`, `recipe.js`,
  etc.), each responsible only for its own page's DOM and API calls.
  `api.js` is the sole place that knows endpoint URLs/payload shapes;
  `cook.js` is the sole place that touches `sessionStorage` for checkbox
  state.

## 4. Data Model / SQLite Schema

```sql
CREATE TABLE recipes (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT NOT NULL,
    category   TEXT NOT NULL CHECK (category IN ('Breakfast','Main','Side','Dessert')),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE recipe_ingredients (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL REFERENCES recipes(id),
    position  INTEGER NOT NULL,   -- 0-based order as entered
    quantity  TEXT,                -- free text, e.g. "2 cups", "1", "to taste"; may be NULL/empty
    name      TEXT NOT NULL        -- e.g. "flour"
);

CREATE TABLE recipe_steps (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id   INTEGER NOT NULL REFERENCES recipes(id),
    position    INTEGER NOT NULL,   -- 0-based order; Cook Mode and the detail view both use this
    instruction TEXT NOT NULL
);

CREATE TABLE meal_plan_entries (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id  INTEGER NOT NULL REFERENCES recipes(id),
    date       TEXT NOT NULL,   -- ISO date 'YYYY-MM-DD'
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE shopping_list_checks (
    ingredient_key TEXT PRIMARY KEY,           -- normalized ingredient name (see §5)
    checked        INTEGER NOT NULL DEFAULT 0  -- 0/1
);
```

Notes:

- No `cook_mode_progress` table: Cook Mode's checkbox/step state is
  explicitly session-scoped and client-side only, per
  `environment-notes.md`'s no-auth/no-session-store constraint and the
  Cook Mode brief's "for the duration of the session" language. It lives in
  the browser's `sessionStorage`, keyed per recipe, and is never sent to the
  backend.
- `recipe_ingredients.quantity` is free text rather than a structured
  `(amount, unit)` pair. The Admin brief only requires "an ingredient list
  (one or more ingredient entries)" with no structured-amount requirement,
  and free text is simpler for the user to enter ("a pinch", "to taste", "2
  cups"). §5 defines how the Shopping List still combines these where
  possible. *(Judgment call — see summary.)*
- `meal_plan_entries` has no uniqueness constraint on `(recipe_id, date)`:
  the Meal Planner brief permits multiple recipes per day and doesn't
  prohibit the same recipe appearing twice on the same day, so duplicates
  are allowed. Each assignment is independently identified by its `id`,
  which is what removal (`DELETE /api/meal-plan/{id}`) targets — this
  is more robust than removing by `(date, recipe_id)`, which would be
  ambiguous if that same pair exists twice. *(Judgment call — see summary.)*
- `shopping_list_checks` stores checked state keyed by the same normalized
  ingredient name used for aggregation grouping (§5), not by recipe. This
  means checking "eggs" stays checked across app restarts and even if the
  contributing recipe is temporarily unplanned and re-planned later —
  consistent with the app's SQLite-backed, cross-session persistence
  everywhere except Cook Mode (which the environment notes explicitly scope
  to session-only). *(Judgment call — see summary.)*
- No `users`/auth tables — the app is single-user/no-login per the concept
  and `environment-notes.md`.
- SQLite file lives at `backend/data/app.db`, created by `database.py` on
  first run if absent (the `backend/data/` directory is created if missing).
  Already covered by the `*.db` entry in `.gitignore` regardless of the
  containing directory.

## 5. Shopping List Aggregation

The Shopping List is derived, on every `GET /api/shopping-list` request,
from whatever recipes are currently assigned within the rolling 7-day
window (§6, `date_utils.py`). No list state is persisted except the
per-ingredient checked flag (§4).

**Normalization** (`shopping_logic.normalize_name`): lowercase, strip
leading/trailing whitespace, collapse internal whitespace runs to a single
space. This normalized string is the grouping key and also the key used in
`shopping_list_checks` and the `PATCH /api/shopping-list/{ingredient}`
path parameter.

**Combining quantities**, per normalized-name group (in the order recipes
are joined — lowest `recipe_id`, then ingredient `position`):

1. Each contributing `quantity` string is matched against
   `^\s*(\d+(?:\.\d+)?|\d+/\d+)\s*([a-zA-Z]*)\s*$` (an optional decimal or
   simple `a/b` fraction, followed by an optional unit word).
2. If **every** contributing quantity in the group matches this pattern
   **and** all matched unit words are equal case-insensitively (including
   all-blank, i.e. no unit, counting as one shared "unit"), the numeric
   parts are summed (fractions evaluated as `a/b`) and rendered as a single
   `"<sum> <unit>"` string (unit omitted if blank; trailing `.0` trimmed).
3. Otherwise — a blank/free-text quantity (e.g. "to taste"), an
   unparseable quantity, or mismatched units — the group is **not**
   combined into a number. Instead, the distinct raw quantity strings
   (first-seen order, skipping true blanks) are joined with `"; "` on the
   single output line, e.g. `"2 cups; 1 tbsp"` or `"to taste; 1/2 tsp"`.
   This still satisfies "one line per ingredient, never duplicated" even
   when the amounts themselves can't be cleanly summed, per the Shopping
   List brief.
4. The displayed ingredient name is the raw (non-normalized) `name` text
   from the first-encountered contributing ingredient row, for stable,
   human-readable casing.
5. Output is sorted alphabetically (case-insensitive) by displayed name.

Known, intentional limitation: unit matching is a case-insensitive exact
string match ("cup" and "cups" are treated as different units and will not
combine). This is an accepted simplification — the brief explicitly allows
amounts that "can't be combined cleanly" to be shown together on one line
rather than summed, and no unit-conversion/pluralization library is in the
approved environment.

## 6. Rolling 7-Day Window

`date_utils.get_window(today: date) -> list[(date, weekday_name)]` returns
exactly 7 `(ISO date string, weekday name)` pairs: `today` through `today +
6 days`, using the server's local date (`datetime.date.today()`) — no
timezone handling is implemented, consistent with the single-user, local-
development-only scope in `environment-notes.md`. `date_utils.in_window(d,
today)` checks whether a given ISO date string falls in that same range;
both `meal_plan.py` (to validate assignment dates) and `shopping_list.py`
(to select which `meal_plan_entries` rows contribute) call this so the two
features can never disagree about what "the coming week" means.

Entries whose `date` has rolled out of the window (now in the past) are
simply no longer returned by `GET /api/meal-plan` or aggregated by the
Shopping List — they are left in place in SQLite rather than deleted, since
no feature brief requires purging past assignments and doing so isn't
needed for correctness at this scale.

## 7. API Contracts

All endpoints are under `/api`, return JSON, and use standard HTTP status
codes (`404` for an unknown id, `422` for validation failures via
FastAPI/Pydantic, `400` for a semantically invalid request such as a
date outside the current window).

### Recipes / Catalog

**`GET /api/recipes`**
Optional query param: `?category=Breakfast|Main|Side|Dessert`.
Response `200`, ordered by title (case-insensitive) ascending:
```json
[
  { "id": 1, "title": "Blueberry Pancakes", "category": "Breakfast" }
]
```

**`GET /api/recipes/{recipe_id}`**
Response `200`:
```json
{
  "id": 1,
  "title": "Blueberry Pancakes",
  "category": "Breakfast",
  "ingredients": [
    { "quantity": "2 cups", "name": "flour" },
    { "quantity": "1", "name": "egg" }
  ],
  "steps": [
    "Whisk dry ingredients together.",
    "Fold in blueberries and cook on a griddle."
  ]
}
```
`404` if `recipe_id` doesn't exist. `steps` is ordered exactly as the
recipe defines (`recipe_steps.position` ascending) — this is the same
ordering Cook Mode walks through.

### Admin (create-only, per `05-admin-recipe-creation.md`)

**`POST /api/recipes`**
Request:
```json
{
  "title": "Blueberry Pancakes",
  "category": "Breakfast",
  "ingredients": [
    { "quantity": "2 cups", "name": "flour" },
    { "quantity": "1", "name": "egg" }
  ],
  "steps": [
    "Whisk dry ingredients together.",
    "Fold in blueberries and cook on a griddle."
  ]
}
```
Validation (via Pydantic, enforced before any row is written): `title`
non-empty (trimmed), `category` one of the four fixed values, `ingredients`
has at least one entry with a non-empty `name`, `steps` has at least one
non-empty entry. Response `201`: the created recipe in the same shape as
`GET /api/recipes/{id}` (including its new `id`). Response `422` on any
validation failure, with FastAPI's standard per-field error body (`detail`:
list of `{loc, msg, type}`), which is enough for the frontend to show the
user what's missing/invalid. No partial recipe is ever written on failure —
the whole request is validated before any `INSERT`.

No update/delete endpoints exist anywhere in this API — Admin is strictly
additive, and there is no editing/deleting capability anywhere in the
product, matching the Recipe Catalog and Admin briefs' constraints.

### Meal Planner

**`GET /api/meal-plan`**
Response `200` — always exactly 7 day entries, today through 6 days out:
```json
{
  "days": [
    {
      "date": "2026-08-31",
      "weekday": "Monday",
      "entries": [
        { "id": 12, "recipe_id": 1, "title": "Blueberry Pancakes", "category": "Breakfast" }
      ]
    },
    { "date": "2026-09-01", "weekday": "Tuesday", "entries": [] }
  ]
}
```
`entries` is `[]` for a day with nothing planned (not omitted), so the
frontend can render a consistent empty state.

**`POST /api/meal-plan`**
Request:
```json
{ "recipe_id": 1, "date": "2026-09-01" }
```
Response `201`: `{ "id": 13, "recipe_id": 1, "date": "2026-09-01" }`.
`404` if `recipe_id` doesn't exist. `400` if `date` is not one of the 7
dates in the current window (e.g. already in the past, or more than 6 days
out) — the window itself (from `GET /api/meal-plan`) is the source of truth
for which dates the frontend should ever offer.

**`DELETE /api/meal-plan/{entry_id}`**
Response `204` on success. `404` if `entry_id` doesn't exist. Removing an
entry immediately affects the next `GET /api/shopping-list` call (its
ingredients drop off unless another still-planned recipe also needs them),
per the Shopping List brief — there is no separate refresh step.

### Shopping List

**`GET /api/shopping-list`**
Response `200`, alphabetical by ingredient, `[]` if nothing is currently
planned:
```json
[
  { "ingredient": "eggs", "quantity": "6", "checked": false },
  { "ingredient": "flour", "quantity": "2 cups; 1 tbsp", "checked": true }
]
```

**`PATCH /api/shopping-list/{ingredient}`**
`{ingredient}` is the normalized ingredient name (§5), URL-encoded by the
frontend (spaces as `%20`, e.g. `/api/shopping-list/olive%20oil`).
Request: `{ "checked": true }`.
Response `200`: `{ "ingredient": "olive oil", "checked": true }`.
`404` if that ingredient is not currently on the derived list (checking an
ingredient that isn't currently planned is rejected rather than silently
stored, since the list's contents are fully determined by the Meal
Planner per the Shopping List brief's constraints).

## 8. Backend Responsibilities

- Own all persistence (SQLite) and be the sole source of truth for recipe
  content and meal-plan assignments.
- Compute the rolling 7-day window (`date_utils.py`) and enforce it as the
  only valid range for meal-plan assignment and the only input to Shopping
  List aggregation.
- Derive the Shopping List on every request from current meal-plan state
  (`shopping_logic.py`) — normalize ingredient names, combine quantities
  where possible, and merge in persisted checked state. The frontend never
  computes aggregation itself.
- Validate Admin recipe submissions (title, category, ≥1 ingredient, ≥1
  step) and reject invalid submissions atomically (no partial writes).
- Seed the 20 starting recipes on first run (`seed_data.py`, applied by
  `database.py` when `recipes` is empty), so a fresh checkout is
  immediately usable without a manual data-loading step.
- Serve the static frontend files (single process, per
  `environment-notes.md`).
- Never touch Cook Mode's checkbox/step-position state — that is 100%
  client-side.

## 9. Frontend Responsibilities

- Render the Recipe Catalog, recipe detail, Cook Mode, Meal Planner,
  Shopping List, and Admin screens as separate static pages, navigating via
  normal links/`fetch` calls — no SPA router, no build step.
- Catalog (`catalog.js`): fetch and render `GET /api/recipes` (with the
  optional category filter as a query param), link each recipe to
  `recipe.html?id=...`.
- Recipe detail (`recipe.js`): fetch `GET /api/recipes/{id}`, show full
  ingredients/steps, and link into Cook Mode and the Meal Planner for that
  recipe.
- Cook Mode (`cook.js`): fetch `GET /api/recipes/{id}` once, then entirely
  client-side — track the current step index in memory (starting at step 1
  each time Cook Mode is entered) and each step's checked state in
  `sessionStorage` under a per-recipe key (e.g. `cookmode:{id}`), so
  checkbox state survives leaving and re-entering Cook Mode within the same
  browser session but resets on a new session (browser/tab close), per the
  Cook Mode brief. Provide next/previous (disabled at the first/last step)
  and a reset action that clears that recipe's `sessionStorage` entry.
  Never calls the backend for step/checkbox state.
- Meal Planner (`planner.js`): fetch `GET /api/meal-plan`, render the 7 day
  slots exactly as returned (only those 7 dates are ever offered for
  assignment), `POST`/`DELETE` against `/api/meal-plan` for
  add/remove, and re-fetch (or optimistically update) after each change.
- Shopping List (`shopping-list.js`): fetch `GET /api/shopping-list` and
  render it; `PATCH` per item on check/uncheck. Since the list is always
  server-derived, the page can simply re-fetch after returning from the
  Meal Planner rather than tracking derivation itself.
- Admin (`admin.js`): a form for title, category (select from the four
  fixed values), a repeatable ingredient row (quantity + name), and a
  repeatable step row (ordered text), posting to `POST /api/recipes` and
  surfacing `422` field errors inline; no edit/delete UI anywhere.

## 10. Component Interaction / State Flow

```
Catalog (GET /api/recipes[?category=])
   │ select recipe
   ▼
Recipe detail (GET /api/recipes/{id})
   │
   ├─ Cook Mode   → same GET /api/recipes/{id} data, all further state
   │                 (current step, checkboxes) lives in sessionStorage only
   │
   └─ Meal Planner → GET /api/meal-plan (7-day window)
                        │ assign/remove
                        ▼
                     POST /api/meal-plan | DELETE /api/meal-plan/{id}
                        │ (persisted to meal_plan_entries)
                        ▼
                     Shopping List: GET /api/shopping-list
                        (recomputed from meal_plan_entries + recipe_ingredients
                         on every request; check state read/written via
                         PATCH /api/shopping-list/{ingredient})

Admin → POST /api/recipes
   → next GET /api/recipes / GET /api/recipes/{id} calls see the new recipe
     immediately (no cache, no separate publish step) — it is usable in
     Cook Mode and the Meal Planner exactly like a seed recipe, satisfying
     05-admin-recipe-creation.md.
```

All application state that must outlive a single page view or be shared
across features (recipes, meal-plan assignments, shopping-list checked
state) lives in SQLite and is re-fetched by the frontend as needed. The
only state that lives purely in the browser is Cook Mode's current step and
per-step checkboxes (`sessionStorage`), by design (§4, §9).

## 11. Deviations From the Approved Environment

None. `requirements.txt` (`fastapi`, `uvicorn[standard]`) is sufficient —
persistence uses the stdlib `sqlite3` module (no ORM), the rolling window
and quantity parsing use the stdlib `datetime` and `re` modules, and seed
data loading needs nothing beyond plain Python data structures. This
resolves the three items `environment-notes.md` deferred to this stage: no
ORM introduced, seed data loaded via a plain `seed_data.py` module read by
`database.py` on first run, and the SQLite file placed at
`backend/data/app.db` (already covered by `.gitignore`'s `*.db` entry).
