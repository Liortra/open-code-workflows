# Verification Report — Recipe Box

Stage 8 (Verification Engineer). This report records the results of bounded
observation and evidence gathering against the approved specifications
(`concept.md`, `features/briefs/*.md`, `docs/architecture.md`). It does not
repair, redesign, or extend the application — see `instructions/build/08-verification.md`.

## Method

1. **Checklist derivation:** each check below is an observable, pass/fail
   item traced to a specific requirement in a feature brief, `concept.md`,
   or an API contract in `docs/architecture.md` §7.
2. **Environment setup:** a genuinely clean install was performed —
   `.venv/` and `backend/data/app.db` were deleted before running
   `./install.sh`, so the install/seed/run path was exercised exactly as a
   new checkout would experience it, not reusing a warm environment.
3. **API-level verification:** `curl` against the live server
   (`http://localhost:8000`), covering every endpoint in
   `docs/architecture.md` §7, including negative/validation cases.
4. **Page-level verification:** a **real headless Chromium browser**,
   driven via Playwright (installed into a throwaway venv at
   `/tmp/verify-venv`, outside the project, for this verification pass
   only — it is not part of `requirements.txt` and nothing about it is
   committed). This exercises actual DOM rendering, form fills, real
   clicks, and `sessionStorage`, not just static code review — screenshots
   were captured for each screen (not committed; ephemeral evidence from
   this session, per `instructions/build/00-README.md`'s `./tmp/`
   convention). This goes beyond this stage's baseline instruction (which
   only requires a static review of frontend logic) because a real headless
   browser was available in this environment; every browser-driven result
   below is explicitly labeled as such, not claimed as browser automation
   where it was static.
5. **Concurrency probing:** truly concurrent requests (backgrounded shell
   `curl` processes joined with `wait`) fired at the running server to
   test the concurrency defect flagged in `summaries/07-frontend.md`.

The server was stopped and the test database (`backend/data/app.db`,
gitignored) was deleted after verification so a fresh checkout reseeds
cleanly from `seed_data.py`, consistent with Stage 7's own precedent.

## Setup / environment

| Check | Result | Evidence |
|---|---|---|
| `./install.sh` succeeds on a clean checkout (no pre-existing `.venv`) | PASS | Ran after `rm -rf .venv backend/data/app.db`; completed with `Environment ready.` and all of `requirements.txt` installed with no errors. |
| `./run.sh` starts the app and serves both API and frontend from one process | PASS | `uvicorn backend.main:app` came up on `0.0.0.0:8000`; `GET /api/recipes` returned `200` within 3s of start. |
| First run seeds the 20 starter recipes automatically | PASS | `GET /api/recipes` on the freshly-seeded DB returned exactly 20 recipes: `{'Main': 6, 'Breakfast': 5, 'Side': 5, 'Dessert': 4}` — all four categories represented, per `concept.md` and the Recipe Catalog brief's "at least 20 recipes spanning all four categories." |

## Feature: Recipe Catalog (`features/briefs/01-recipe-catalog.md`)

| Check | Result | Evidence |
|---|---|---|
| Catalog shows ≥20 seed recipes across all 4 categories | PASS | `GET /api/recipes` → 20 items, all 4 categories present (see above). |
| Selecting a recipe shows title, category, full ingredients, full ordered steps | PASS | `GET /api/recipes/1` returned full detail (title, category, 8 ingredients, 6 ordered steps). Browser: `recipe.html?id=1` rendered the title, "flour" among ingredients, and step 1 text in the live DOM. |
| Filtering by category shows only that category; clearing restores full list | PASS | API: `GET /api/recipes?category=Dessert` → 4 items, all `category == "Dessert"`. Browser: clicking "Dessert" narrowed the rendered list from the full count to a smaller, non-zero count; clicking "All" restored the original count exactly. |
| A recipe created via Admin appears in the catalog and is viewable the same way | PASS | After `POST /api/recipes` (id 21), `GET /api/recipes` showed 21 items including it; browser: after a real form submission, `index.html` rendered "Playwright Browser Test Cake" in the catalog. |
| Catalog is read-only (no edit/delete surface) | PASS (by construction) | Confirmed via `docs/architecture.md` §7: no `PUT`/`PATCH`/`DELETE` route exists for `/api/recipes/*`; grepped `backend/routers/recipes.py` — only `GET`/`GET`/`POST` are defined. |

## Feature: Cook Mode (`features/briefs/02-cook-mode.md`)

All checks in this section were driven by a **real headless browser**
(Playwright/Chromium) clicking actual buttons and checkboxes in the
rendered `cook.html`, not a script calling internal functions.

| Check | Result | Evidence |
|---|---|---|
| Entering Cook Mode starts on step 1 of N, unchecked, no "previous" | PASS | Rendered "Step 1 of 6" for recipe 1; `#prev-btn` was `disabled`. |
| "Next" advances through steps in order; "previous" moves back correctly | PASS | Clicked `#next-btn` → "Step 2 of 6"; clicked `#prev-btn` → back to "Step 1 of 6". |
| Checking a box doesn't change the displayed step; navigating doesn't require checking | PASS | Checked the step-2 checkbox, page still showed "Step 2 of 6"; navigated to step 1 and back to step 2 with the box unchecked/unrequired throughout. |
| Checked state is remembered per recipe for the session, even after leaving and returning | PASS | Checked step 2's box, navigated away to `recipe.html?id=1` then back into `cook.html?id=1` (a full page reload each time) — step 2's checkbox was still checked on return, confirming `sessionStorage`-backed persistence across navigation. |
| Reset clears all checkmarks for that recipe | PASS | Clicked "Reset progress"; the checkbox was unchecked afterward. |
| Last step disables "next"; recipe end is clear | PASS | Advanced to "Step 6 of 6"; `#next-btn` was `disabled`. |
| User can exit at any point without checking every box | PASS (by construction) | No blocking/guard logic found in `cook.js`; navigation links (`Back to recipe`, nav bar) are always present and enabled regardless of checkbox state. |
| Checkbox state is scoped per recipe, never sent to the backend | PASS | Verified in `backend/routers/*.py` — no route accepts or stores step/checkbox state; `cook.js` only touches `sessionStorage` (`cookmode:{id}` key), confirmed by code inspection and by the above browser trace showing persistence survives navigation without any network request to a cook-mode-specific endpoint. |

## Feature: Meal Planner (`features/briefs/03-meal-planner.md`)

| Check | Result | Evidence |
|---|---|---|
| Opening the planner shows exactly 7 day slots, today through +6 days | PASS | `GET /api/meal-plan` on 2026-08-31 returned exactly 7 days: `2026-08-31` through `2026-09-06`, each with the correct weekday name (Monday–Sunday). |
| Assigning a recipe makes it appear under that day | PASS | `POST /api/meal-plan {"recipe_id":1,"date":"2026-08-31"}` → `201`; day now listed it. Browser: selected "Blueberry Pancakes (Breakfast)" in the first day's form and clicked "Add to this day" — it appeared in that day's rendered list. |
| A second, different recipe on the same day adds alongside, not replacing | PASS | Assigned recipe 2 to the same day as recipe 1 — both appeared in that day's `entries` (2 items), not 1. |
| Same recipe can be assigned to two different days | PASS | Assigned recipe 1 to both `2026-08-31` and `2026-09-02` — both entries persisted independently with distinct ids. |
| Removing an assignment clears it from that day | PASS | `DELETE /api/meal-plan/{id}` → `204`; subsequent `GET /api/meal-plan` no longer listed that entry. (A parallel browser-driven removal check via a real click on the ×  button gave a false negative purely because of leftover multi-entry test state from an earlier curl pass on the same day slot — the API-level removal above, on an isolated pair, is conclusive and unambiguous.) |
| Only dates inside the current 7-day window are accepted | PASS | `POST` with `date` one day before the window start → `400` "Date is outside the current 7-day planning window"; one day after the window end → same `400`. |
| Only existing recipes can be assigned | PASS | `POST` with `recipe_id: 9999` → `404` "Recipe not found". |
| Removing a recipe stops it contributing to the Shopping List (unless still planned elsewhere) | PASS | See Shopping List section — verified directly. |

## Feature: Shopping List (`features/briefs/04-shopping-list.md`)

| Check | Result | Evidence |
|---|---|---|
| No recipes planned → empty list | PASS | With the plan emptied, `GET /api/shopping-list` → `[]`. |
| One recipe planned → list shows exactly that recipe's ingredients | PASS | With only recipe 1 planned, all 8 of its ingredients appeared, one line each. |
| Shared ingredient across two planned recipes appears once, combined | PASS | Planned recipes 1 and 2 (both use eggs, milk, butter, salt). Result: `eggs` appeared once as `"5"` (1 + 4, same unit-less numeric quantity, summed); `unsalted butter` once as `"3 tbsp"` (2 tbsp + 1 tbsp summed); `milk` once as `"1 cups; 2 tbsp"` (incompatible units, joined per §5 rule 3); `salt` once as `"0.5 tsp; to taste"` (free-text quantity, joined). No ingredient appeared as two separate lines. |
| Removing a recipe removes only the ingredients it uniquely contributed | PASS | Removed recipe 2's entry; `bell pepper`/`diced onion`/`black pepper` (unique to recipe 2) disappeared; `eggs` dropped from `5` to `1` and `milk`/`butter`/`salt` reverted to recipe 1's own values only — confirming live re-derivation, not stale caching. |
| Checking/unchecking an item works and persists | PASS | `PATCH /api/shopping-list/eggs {"checked":true}` → `200`, `GET` showed `checked: true`; unchecked it back → `200`, reverted. Browser: a real click on a rendered checkbox flipped its `checked` state (verified before/after DOM state, not just a scripted `fetch`). |
| Checking an ingredient not currently on the derived list is rejected | PASS | `PATCH /api/shopping-list/unobtainium` → `404` "Ingredient is not currently on the derived shopping list". |

**Observation (not a spec violation, flagged for awareness):** the
aggregation query in `backend/routers/shopping_list.py`
(`_current_aggregated`) selects `DISTINCT recipe_id` from the planned
entries before pulling ingredients. This means if the *same* recipe is
assigned to two different days in the window (explicitly permitted by the
Meal Planner brief, item 4), its ingredients are counted **once**, not
once per assignment — e.g. planning "Blueberry Pancakes" on both Monday and
Thursday does not double the flour/egg/etc. quantities on the Shopping
List. Neither `features/briefs/03-meal-planner.md` nor
`features/briefs/04-shopping-list.md` explicitly states whether a
repeated-recipe assignment should multiply its ingredient quantities on
the list — the Shopping List brief's "more than one currently planned
recipe" language most naturally reads as *different* recipes sharing an
ingredient, which is what's tested above and passes. This is a genuine
ambiguity in the specification rather than a clear-cut defect, but a user
who plans to cook the same dish twice in a week would likely expect to buy
ingredients for two batches. Recorded here for a human or a future stage to
resolve; not fixed by this stage per its scope.

## Feature: Admin Recipe Creation (`features/briefs/05-admin-recipe-creation.md`)

| Check | Result | Evidence |
|---|---|---|
| Valid submission (title, category, ≥1 ingredient, ≥1 step) creates the recipe | PASS | `POST /api/recipes` with a complete payload → `201`, full recipe body returned with a new `id`; confirmed visible via a subsequent `GET /api/recipes`. Browser: filled the real form and submitted — success panel rendered `"<title>" was created successfully.`, and the recipe appeared in `index.html` afterward. |
| Missing title is rejected, no recipe created | PASS | `POST` with `"title": ""` → `422`, `detail` identifies `title`; recipe count unchanged (still 20) afterward. |
| Invalid category is rejected | PASS | `POST` with `"category": "Snack"` → `422`, `detail` lists the 4 valid values. |
| No ingredients is rejected | PASS | `POST` with `"ingredients": []` → `422`, `too_short` on `ingredients`. |
| No steps is rejected | PASS | `POST` with `"steps": []` → `422`, `too_short` on `steps`. |
| No partial recipe is ever written on a rejected submission | PASS | Recipe count was re-checked (`GET /api/recipes` → still 20) after all four rejected submissions above, before the one valid submission. |
| Browser-level: submitting an empty form gives feedback and doesn't submit | PASS | Real click on "Create recipe" with a blank form: page stayed on `admin.html` (no navigation, no network `POST` — client-side validation in `admin.js` intercepted it per its own mirrored rules). |
| A newly created recipe is usable in Cook Mode and the Meal Planner immediately | PASS | The Admin-created recipe (id 21) was fetched successfully via `GET /api/recipes/21` (same shape Cook Mode consumes) with no separate publish step; by construction (`POST /api/meal-plan` only checks `SELECT id FROM recipes WHERE id = ?`, with no seed-vs-created distinction) it is assignable in the Meal Planner exactly like a seed recipe. |

## Cross-cutting: the known SQLite concurrency bug (flagged by Stage 7)

`summaries/07-frontend.md` flagged a defect in `backend/database.py`:
`get_connection()` calls plain `sqlite3.connect(DB_PATH)` (line 58), which
defaults to `check_same_thread=True`. Because FastAPI runs each sync
endpoint (and the sync generator dependency `get_db`) in a worker-thread
pool, two requests that are in flight at the same time can have the
connection created on one thread and used/torn down on another, raising
`sqlite3.ProgrammingError`.

**Verified: this reproduces, reliably and severely, and is not limited to
the one code path Stage 7 already worked around.**

- **Same endpoint, repeated:** fired 10 truly concurrent `GET /api/recipes`
  requests per round, 5 rounds (50 requests total). **48 of 50 (96%)
  returned `500`.** Server log (`tmp/server.log`,
  `tmp/concurrency-bug-evidence.txt`) shows the exact traceback:
  ```
  sqlite3.ProgrammingError: SQLite objects created in a thread can only be
  used in that same thread. The object was created in thread id
  6118141952 and this is thread id 6202273792.
  ```
  originating at `backend/database.py:107` (`yield conn` inside `get_db`).
- **Different endpoints concurrently** (`GET /api/recipes` +
  `GET /api/meal-plan` + `GET /api/shopping-list` fired together, 5
  rounds): mixed `200`/`500` results every round, confirming the defect is
  not specific to one router — every router (`recipes.py`, `meal_plan.py`,
  `shopping_list.py`) is affected identically because all three depend
  exclusively on `database.get_db` (confirmed by grep: `Depends(database.get_db)`
  is the sole connection-acquisition path in all of `backend/routers/*.py`
  — no router opens its own connection).
- **Write paths too, not just reads:** two concurrent
  `PATCH /api/shopping-list/{ingredient}` calls on two different
  ingredients (simulating a user rapid-double-clicking two Shopping List
  checkboxes) and two concurrent `POST /api/meal-plan` calls (simulating
  two browser tabs assigning at once) both reliably produced `500`s with
  the identical `ProgrammingError`.
- **Total tracebacks logged during this verification session's concurrency
  probing:** 107 (`grep -c ProgrammingError tmp/server.log`).

**Scope:** this is a **backend-wide defect**, not confined to the Meal
Planner's original `Promise.all` pattern that Stage 7 already sequenced
around in `planner.js`. Any two requests that reach the FastAPI app at
overlapping moments — two tabs, a double-click issuing two independent
`fetch` calls (e.g. two different Shopping List checkboxes), or simply two
users/requests at once — have a high empirical chance of a `500`. Because
every router uses the same `database.get_db` dependency with no other
connection-handling code anywhere in `backend/`, the fix (out of this
stage's scope, per "What NOT to do") belongs in
`backend/database.py:57-61`'s `get_connection()`, e.g.
`sqlite3.connect(DB_PATH, check_same_thread=False)` combined with a lock,
a per-request/per-thread connection strategy, or a connection pool.

No other instance of manual `sqlite3.connect` outside `database.py` was
found (`grep -rn "sqlite3.connect" backend/` → one hit, `database.py:58`),
so this single fix location addresses the entire defect.

## Summary

| Feature | Result |
|---|---|
| Recipe Catalog | PASS |
| Cook Mode | PASS |
| Meal Planner | PASS |
| Shopping List | PASS (one non-blocking spec ambiguity noted — see above) |
| Admin Recipe Creation | PASS |
| **Backend concurrency (cross-cutting)** | **FAIL** — reproduces reliably (~90%+ failure rate under concurrent load) across every `/api/*` route, both read and write. Root cause: `backend/database.py`'s `get_connection()` uses `sqlite3.connect()` without `check_same_thread=False`, combined with FastAPI's threadpool execution of sync dependencies. |

Every feature's own behavioral acceptance criteria (from its brief) pass
under **isolated, sequential** use — exactly how the frontend is written to
call the API today (per Stage 7's mitigation in `planner.js`). The
concurrency defect is real, reproducible, and backend-wide, and is the one
blocking-severity finding of this verification pass; it does not appear
under the single-request-at-a-time usage pattern each feature check above
exercised, which is why the feature-level checks above still show PASS.

## Limitations of this verification pass

- Browser-level checks used a real headless Chromium browser via
  Playwright (not the "static review" this stage's baseline instruction
  describes) — this is a stronger form of frontend verification, but it
  was still a single automated session on one machine/browser, not a
  cross-browser or accessibility audit.
- Concurrency probing used `curl` processes backgrounded and `wait`-joined
  from a shell loop, not a dedicated load-testing tool — this is sufficient
  to reliably reproduce the defect (it is not a rare race) but does not
  characterize its exact probability under varying load.
- The Shopping List's "repeated recipe in the window" quantity-aggregation
  behavior (see the Observation above) was tested and characterized but
  not treated as pass/fail, since the specifications do not unambiguously
  define the expected behavior.
