# Summary: Architect (Stage 5)

- **Date:** 2026-08-31
- **Author / Executor:** Claude (agent)
- **Instruction file:** `instructions/build/05-architecture.md`
- **Commit:** `stage 05: define technical architecture for Recipe Box`

## Work Completed

Read `concept.md`, all five `features/briefs/*.md` files, and the
environment definition (`requirements.txt`, `environment-notes.md`), then
wrote `docs/architecture.md` as the technical specification for the
Backend and Frontend Engineer stages. It covers: project/file structure
(`backend/` with routers + shared modules, `frontend/` as static
multi-page HTML/JS), module boundaries, the full SQLite schema, the
Shopping List's quantity-aggregation algorithm, the rolling 7-day window
definition, complete API contracts (routes, request/response JSON,
status codes) for Recipes/Admin, Meal Planner, and Shopping List, a clear
backend/frontend responsibility split, and a component-interaction/state-flow
diagram. No application code was written, per this stage's scope.

## Outputs Produced

- `docs/architecture.md` — the full technical specification.
- `summaries/05-architecture.md` — this summary.

## Key Decisions

- **No ORM.** Persistence uses the stdlib `sqlite3` module directly, per
  the default in `environment-notes.md`; nothing in the briefs warrants an
  ORM's added complexity.
- **SQLite file location:** `backend/data/app.db`, created on first run by
  `database.py`. Resolves the deferred decision from Stage 4; already
  covered by `.gitignore`'s `*.db` entry.
- **Seed loading:** a plain `seed_data.py` module (20 recipes as Python
  data) applied by `database.py` on first run when `recipes` is empty — no
  extra package, resolving Stage 4's other deferred item.
- **Ingredients stored as free-text `quantity` + `name` pairs**, not a
  structured amount/unit. The Admin brief only requires "an ingredient
  list," and free text is simpler to author ("a pinch," "to taste"). The
  Shopping List's combination logic (architecture §5) works from this free
  text via a regex-based amount/unit parser, summing when units match
  exactly (case-insensitive) and otherwise joining raw strings on one line
  — satisfying the brief's explicit allowance for amounts that "can't be
  combined cleanly." *Known, accepted limitation:* unit matching is exact
  string match, so "cup" and "cups" won't combine — no pluralization/unit-
  conversion library is in the approved environment, and the brief permits
  this fallback behavior.
- **Meal-plan assignments removed by synthetic `id`, not `(date,
  recipe_id)`.** The brief describes removal as "a day + recipe pair," but
  since the same recipe can be assigned to the same day more than once
  (nothing prohibits it), an id-based `DELETE /api/meal-plan/{id}` is
  unambiguous where a pair-based lookup would not be. The frontend already
  has each entry's `id` from `GET /api/meal-plan`, so this doesn't change
  user-visible behavior — the user still removes "this specific recipe from
  this specific day" by acting on the entry shown in the UI.
- **Shopping List checked state is persisted server-side** (a
  `shopping_list_checks` table keyed by normalized ingredient name), not
  client-side. Unlike Cook Mode — which `environment-notes.md` explicitly
  scopes to session-only to keep the environment auth/session-free — the
  Shopping List brief has no "for this session" language, and every other
  piece of app state (recipes, meal plan) is durably persisted in SQLite.
  Persisting checked state by ingredient name keeps it stable even if the
  contributing recipe is briefly unplanned and re-planned.
- **Rolling window uses server local date** (`datetime.date.today()`), no
  timezone handling — consistent with the single-user,
  local-development-only scope already stated in `environment-notes.md`.
- **No backend surface for Cook Mode at all.** Step position and per-step
  checkboxes live only in browser `sessionStorage`, keyed per recipe —
  directly implementing the deferred assumption flagged in Stage 4's
  summary and `environment-notes.md`. Current step index resets to step 1
  each time Cook Mode is (re-)entered; only the checkbox state is required
  by the brief to survive leaving/re-entering within a session.
- **No deviations from the approved environment.** `requirements.txt`
  (`fastapi`, `uvicorn[standard]`) is sufficient; aggregation and
  date-window logic use only the `datetime` and `re` standard-library
  modules.

## Open Questions & Concerns

- The Shopping List's unit-matching is deliberately simple (exact
  case-insensitive string match on the unit word). If the sample seed data
  ends up mixing unit spellings/pluralization for the same ingredient
  across recipes (e.g. "cup" vs "cups"), those lines will show as
  unmerged/joined amounts rather than a single summed quantity — this is
  by design per the brief's fallback allowance, but worth the Backend
  Engineer (Stage 6) knowing about when writing seed data, so as not to
  accidentally produce a confusing-looking merge failure the seed data
  itself could have avoided by using consistent unit spelling.
- None of the above are blocking; all deferred items from Stage 4 have been
  resolved in this document.

## Status

- [x] Complete
- [ ] Needs review
