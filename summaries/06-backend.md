# Summary: Backend Engineer (Stage 6)

- **Date:** 2026-08-31
- **Author / Executor:** Claude (agent)
- **Instruction file:** `instructions/build/06-backend.md`
- **Commit:** `stage 06: implement FastAPI backend and SQLite persistence per architecture`

## Work Completed

Implemented the full backend under `backend/`, exactly per `docs/architecture.md`'s
file layout, data model, and API contracts: a FastAPI app (`main.py`) mounting
three routers under `/api`; a stdlib-`sqlite3` persistence layer (`database.py`)
with schema creation and first-run seeding; pure-data seed content
(`seed_data.py`, 20 recipes); Pydantic request/response models (`schemas.py`);
the rolling-7-day-window module (`date_utils.py`); the ingredient
normalization/aggregation module (`shopping_logic.py`); and three routers
(`routers/recipes.py`, `routers/meal_plan.py`, `routers/shopping_list.py`)
implementing every endpoint in architecture §7 (`GET/POST /api/recipes`,
`GET /api/recipes/{id}`, `GET/POST /api/meal-plan`, `DELETE
/api/meal-plan/{id}`, `GET /api/shopping-list`, `PATCH
/api/shopping-list/{ingredient}`). No endpoints or fields beyond what
`docs/architecture.md` specifies were added.

## Outputs Produced

- `backend/main.py`, `backend/database.py`, `backend/seed_data.py`,
  `backend/schemas.py`, `backend/date_utils.py`, `backend/shopping_logic.py`
- `backend/routers/recipes.py`, `backend/routers/meal_plan.py`,
  `backend/routers/shopping_list.py` (+ `__init__.py` package files)
- `summaries/06-backend.md` — this summary

## Key Decisions

- **Static frontend mount is conditional on `frontend/` existing.**
  `docs/architecture.md` §2 has `main.py` mount `frontend/` as static files,
  but `frontend/` is Stage 7's output and does not exist yet at this stage.
  Mounting `StaticFiles` against a missing directory raises at import time,
  which would make the backend un-runnable/un-testable on its own. Resolved
  by guarding the mount with `if FRONTEND_DIR.is_dir(): app.mount(...)` —
  the backend boots and serves `/api/*` standalone today, and Stage 7's
  `frontend/` will be served automatically, with no changes to `main.py`
  needed, once it exists. This is a minimal gap-fill, not a contract change
  (the mount path/behavior itself is unchanged from the spec).
- **Seed data content is backend-authored.** `concept.md`/`docs/architecture.md`
  specify the shape (20 recipes across Breakfast, Main, Side, Dessert, each
  with title/category/ingredients/steps) but not actual content, per this
  stage's "Undefined seed / sample content" guidance. Wrote 20 original
  recipes (5 Breakfast, 6 Main, 5 Side, 4 Dessert) with plausible
  ingredients/instructions.
- **Deliberate unit-spelling consistency in seed data**, directly addressing
  the carried-forward flag in `summaries/05-architecture.md`: for volume
  units that recur across recipes on the same ingredient name (flour, sugar,
  milk, butter, etc.), always spelled "cups" (never "cup"); "tbsp"/"tsp" are
  invariant abbreviations. Countable repeats (eggs, garlic cloves, onion)
  use a bare number with no unit word so they always combine. This was
  verified live: planning "Blueberry Pancakes" + "Veggie Scrambled Eggs" on
  the same day correctly summed eggs (1 + 4 → "5") and unsalted butter
  (2 tbsp + 1 tbsp → "3 tbsp"), while genuinely different units for the same
  ingredient (milk: "1 cups" vs "2 tbsp"; salt: "0.5 tsp" vs "to taste")
  correctly fell back to the joined-string form ("1 cups; 2 tbsp") per
  architecture §5 rather than being silently defeated by spelling variance.
- **Admin transactional safety.** `POST /api/recipes` wraps its three INSERTs
  (recipe, ingredients, steps) in a try/except with `rollback()` on failure,
  on top of Pydantic validating the whole payload before any DB call — belt
  and suspenders for the "no partial recipe is ever written" contract.
- **Category query param on `GET /api/recipes` is an unvalidated plain
  string**, not a `Literal`-constrained param: an unrecognized value simply
  matches zero rows rather than 422ing. Architecture §7 doesn't specify
  behavior for an invalid category value, and returning an empty list is a
  safe, minimal reading of "optional query param" that doesn't invent a new
  contract.
- **No deviations from the approved environment or architecture.** Only
  `fastapi`/`uvicorn[standard]` are used (already in `requirements.txt`);
  persistence, date-window, and aggregation logic use only the stdlib
  (`sqlite3`, `datetime`, `re`). `run.sh`'s `backend.main:app` import target
  required no changes — `backend/main.py` exposes `app` exactly as expected.

## Open Questions & Concerns

- `backend/data/` is created at runtime by `database.py` (and is empty in
  the repo, since `app.db` is gitignored via the existing `*.db` entry) —
  Stage 7/8 should expect a fresh `app.db` (freshly seeded with the 20
  recipes) on first run in a clean checkout, not a persisted state from this
  session's smoke testing.
- Smoke-tested the create-recipe endpoint with a 21st recipe ("Test Grilled
  Cheese") during verification; this was against the throwaway local
  `app.db` that was deleted afterward (gitignored, never committed) — it
  does not appear in `seed_data.py` and will not exist in a fresh checkout.
- Frontend Engineer (Stage 7) should know: the `frontend/` mount in
  `backend/main.py` is conditional on the directory's existence (see Key
  Decisions above) — no action needed on Stage 7's part, the mount will
  activate automatically once `frontend/` is created with any content
  (`index.html` etc., per architecture §2).
- None of the above are blocking.

## Status

- [x] Complete
- [ ] Needs review
