# Summary: Frontend Engineer (Stage 7)

- **Date:** 2026-08-31
- **Author / Executor:** Claude (agent)
- **Instruction file:** `instructions/build/07-frontend.md`
- **Commit:** `stage 07: implement Bootstrap frontend against the live API per architecture`

## Work Completed

Implemented the full browser interface under `frontend/`, exactly per
`docs/architecture.md`'s file layout (§2) and API contracts (§7), and each
feature brief's behavior: six static pages (`index.html` Catalog,
`recipe.html` detail, `cook.html` Cook Mode, `planner.html` Meal Planner,
`shopping-list.html`, `admin.html`) plus `static/css/app.css` and one ES
module per screen under `static/js/` (`api.js`, `catalog.js`, `recipe.js`,
`cook.js`, `planner.js`, `shopping-list.js`, `admin.js`). No build step —
plain HTML/CSS/JS with Bootstrap 5.3.3 loaded from the jsdelivr CDN, per
`concept.md`/`environment-notes.md`. `api.js` is the sole place that knows
endpoint URLs/payload shapes, exactly matching `backend/routers/*.py`'s real
routes (verified by direct diff, see Verification below) — no endpoints were
invented or redesigned.

Feature coverage:
- **Recipe Catalog** (`catalog.js`): fetches `GET /api/recipes[?category=]`,
  category filter buttons for the four fixed categories plus "All", links to
  `recipe.html?id=`.
- **Recipe detail** (`recipe.js`): fetches `GET /api/recipes/{id}`, shows
  ingredients/steps, links into Cook Mode and the Meal Planner.
- **Cook Mode** (`cook.js`): fetches the recipe once; current step index is
  in-memory only (resets to step 1 on entry); per-step checked state lives in
  `sessionStorage` under `cookmode:{id}`; Prev/Next disabled at the ends;
  checking a box never moves the step and moving never requires checking;
  Reset clears that recipe's `sessionStorage` entry only. No backend call for
  step/checkbox state anywhere, per the architecture's explicit constraint.
- **Meal Planner** (`planner.js`): renders the 7 day slots exactly as
  `GET /api/meal-plan` returns them; assign via `POST /api/meal-plan`,
  remove via `DELETE /api/meal-plan/{id}`; re-fetches after each change.
- **Shopping List** (`shopping-list.js`): renders `GET /api/shopping-list`;
  check/uncheck via `PATCH /api/shopping-list/{ingredient}` (URL-encoded);
  reverts the checkbox and refetches on a failed PATCH (e.g. the ingredient
  dropped off the derived list).
- **Admin** (`admin.js`): repeatable ingredient rows (quantity + name) and
  step rows, client-side validation mirroring the server's rules (non-blank
  title, a category, ≥1 ingredient with a name, ≥1 step — blank trailing
  rows are silently ignored rather than treated as errors), posts to
  `POST /api/recipes`, and renders FastAPI's 422 `detail` array as a
  human-readable list on failure. On success, shows a link to the new
  recipe and an "Add another" action; no edit/delete UI anywhere.

## Outputs Produced

- `frontend/index.html`, `recipe.html`, `cook.html`, `planner.html`,
  `shopping-list.html`, `admin.html`
- `frontend/static/css/app.css`
- `frontend/static/js/api.js`, `catalog.js`, `recipe.js`, `cook.js`,
  `planner.js`, `shopping-list.js`, `admin.js`
- `summaries/07-frontend.md` — this summary

## Verification

Ran `./run.sh` (the existing `.venv` already had dependencies installed) and
exercised the live app:
- `curl`ed every page and static asset (`/`, `/index.html`, `/recipe.html`,
  `/cook.html`, `/planner.html`, `/shopping-list.html`, `/admin.html`, and
  all of `static/css`/`static/js`) — all returned `200`.
- Grepped `frontend/static/js/api.js`'s endpoint paths against
  `backend/routers/*.py`'s actual `@router.*` decorators — exact match, no
  invented routes.
- Exercised the real API sequentially with `curl`: recipe list/detail,
  meal-plan assignment on today's date, shopping-list aggregation reflecting
  that assignment, `PATCH` check/uncheck, `DELETE` removal (shopping list
  correctly emptied afterward), an invalid `POST /api/recipes` (422 with the
  expected `detail` shape) and a valid one (201, then visible via
  `GET /api/recipes`).
- Used headless Chrome (screenshots + the DevTools Protocol for console/
  network-error inspection and scripted interaction) to visually confirm the
  Catalog, Recipe Detail, Cook Mode, and Admin pages render correctly with
  Bootstrap styling, and to drive an actual end-to-end flow through the
  rendered pages: submitted the Meal Planner's "Add to this day" form for
  Monday, confirmed the entry appeared in the DOM, confirmed the Shopping
  List page then showed that recipe's aggregated ingredients, and confirmed
  clicking a Shopping List checkbox flipped its class to `checked` (i.e. the
  PATCH round-tripped correctly from a real click, not just a scripted
  fetch).
- Stopped the server afterward; deleted the throwaway `backend/data/app.db`
  created during this session's testing (gitignored, never committed) so a
  fresh checkout reseeds cleanly from `seed_data.py` on first run, per Stage
  6's summary's own precedent.

## Key Decisions / Judgment Calls

- **Discovered and mitigated a real backend concurrency bug in
  `backend/database.py`'s `get_db()` dependency**, found during verification
  (not invented): the Meal Planner page originally fired
  `GET /api/meal-plan` and `GET /api/recipes` concurrently via
  `Promise.all`, which reliably triggered
  `sqlite3.ProgrammingError: SQLite objects created in a thread can only be
  used in that same thread` (visible in `tmp/server.log` during this
  session) — a 500 on both requests. Isolated (non-concurrent) page loads
  (Catalog, Recipe Detail, Cook Mode, Admin) never hit this in repeated
  trials; only the one place the frontend issued two simultaneous API calls
  did. **Fix applied (frontend-only, in `planner.js`):** the two GETs are
  now awaited sequentially instead of via `Promise.all`. This is a
  request-sequencing choice, not a backend fix, and does not touch any
  `backend/` file — it is within Stage 7's scope (orchestrating its own
  fetch calls) and was necessary to make the delivered Meal Planner actually
  functional, which the "actually run and verify" part of this stage's
  assignment requires.
  **This does not eliminate the underlying bug** — the root cause is in
  `backend/database.py`: `get_connection()` uses a plain
  `sqlite3.connect(DB_PATH)` (default `check_same_thread=True`), and
  FastAPI/Starlette can enter and exit a sync generator dependency on
  different threadpool worker threads, so *any* two concurrent requests
  hitting `Depends(database.get_db)` at the same time (e.g. two browser tabs
  open at once, or a user double-clicking two different Shopping List
  checkboxes in quick succession — each checkbox issues its own independent
  `PATCH`) can still 500 the same way. **Flagging this prominently for Stage
  8 (Verification Engineer) and for whoever next touches `backend/`:** the
  fix belongs in the backend (e.g. `check_same_thread=False` with a lock, a
  connection pool, or a per-thread connection cache), not the frontend, and
  Stage 7 correctly did not attempt it. See `tmp/server.log`'s traceback
  from this session's testing for the exact stack (not preserved — `tmp/` is
  gitignored — but trivially reproduced by firing two simultaneous requests
  at any `/api/*` route touching `database.get_db`).
- **Ingredient quantity treated as optional free text in the Admin form**,
  matching `schemas.IngredientIn.quantity: Optional[str]` — a blank
  quantity is sent as `null`, not an empty string, consistent with what the
  seed/backend data already does.
- **Admin form silently drops fully-blank ingredient/step rows** (both
  fields empty) rather than treating them as validation errors, so a user
  who adds a spare row and doesn't fill it isn't blocked; a row with only
  one field filled in (e.g. quantity but no name) *is* flagged, since that's
  a genuinely incomplete entry. This mirrors natural form UX and isn't a
  behavior change from the brief (which only specifies the *complete* set of
  required fields, not how partially-empty repeatable rows should be
  handled).
- **`planner.html` preselects a recipe from `?recipe=` on the query string**
  (set by `recipe.js`'s "Add to Meal Planner" link) in every day's dropdown,
  as a convenience — this is pure UI ergonomics, not a new capability; the
  user still explicitly picks a day and clicks "Add to this day."
- **No polling/auto-refresh anywhere** — every page re-fetches on load and
  after its own mutations, per architecture §9 ("the page can simply
  re-fetch ... rather than tracking derivation itself"); this matches the
  single-user, single-tab-at-a-time assumption in `environment-notes.md`.

## Open Questions & Concerns

- **The backend concurrency bug above is the main open item.** It's
  mitigated for the frontend's own primary call pattern (planner.js no
  longer fires concurrent requests), but it is a latent backend defect that
  Stage 8 should explicitly test for (e.g. by firing two simultaneous
  requests at any endpoint) and that should be fixed in `backend/database.py`
  directly, not worked around further from the frontend.
- Bootstrap and its bundled JS are loaded from `cdn.jsdelivr.net`, per
  `environment-notes.md`'s "Internet access at runtime for the Bootstrap
  CDN" assumption — the app will not render styled pages (though the API and
  raw HTML/JS still work) without internet access at load time.
- None of the above are blocking for handoff; the app is fully usable
  end-to-end as verified above once the backend concurrency issue is kept in
  mind (avoid firing simultaneous requests, e.g. don't open the app in two
  tabs at once, until it's fixed upstream).

## Status

- [x] Complete
- [ ] Needs review
