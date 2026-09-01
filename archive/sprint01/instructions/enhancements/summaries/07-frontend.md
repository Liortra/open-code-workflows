# Summary: Frontend Engineer (Stage 07)

- **Date:** 2026-09-01
- **Author / Executor:** Claude (Frontend Engineer role)
- **Instruction file:** `instructions/enhancements/07-frontend.md`
- **Scope reference:** `enhancements/scope.md`
- **Commit:** `stage 07: implement frontend per architecture`

## Work Completed

Implemented the frontend surface for all four Sprint 01 features specified
in `docs/architecture.md` §11, against the running Stage 6 backend
(`GET /api/srs/due`, `POST /api/srs/{vocabulary_id}/answer`,
`POST /api/activity`, `GET /api/dashboard`).

Read `features/briefs/01–04-*.md`, `docs/architecture.md` (including §11),
the full existing frontend (all `*.html`, all `static/js/*.js`, `app.css`),
and the Stage 6 backend implementation (`schemas.py`, all routers,
`srs_logic.py`, `quiz_logic.py`) before making changes. Three implementation
judgment calls were escalated to the coordinator before starting and
confirmed:
1. Exam's post-submit review rows get **both** a Hebrew and an English
   speaker button (no Hebrew control existed there before this pass).
2. No new Admin Hebrew listing was built (none exists today, per
   `docs/architecture.md` §11.5) — only the nikud toggle control was added
   to Admin's navbar.
3. The SRS "Due for Review" queue is a single fetch/single pass per session
   (mirrors `quiz.js`'s non-refetching pattern); an incorrectly-answered
   word reappears the next time the queue is opened, not mid-session.

Verified end-to-end against a running dev server (fresh seeded DB, deleted
afterward — gitignored, not committed): all 8 existing pages plus the 2 new
pages (`srs.html`, `dashboard.html`) return `200`; all JS files pass
`node --check`; `GET /api/dashboard` on a fresh DB returns `mastery_percent:
null` for every lesson; `GET /api/srs/due` returns all 200 seed words
(none reviewed yet); a correct SRS answer removed that word from the due
count (200 → 199) and returned a `next_due_at` one day out; `POST
/api/activity {mode:"exam"}` still correctly rejects with `422`; submitting
an Exam updated `GET /api/dashboard`'s mastery percent, exam history, and
streak count exactly as expected; an Admin-added nikud-bearing Hebrew word
(`שָׁלוֹם`) round-trips through the API unchanged (fully vocalized), and the
`nikud.js` strip regex was verified (via Node) to correctly reduce it to
consonantal text (`שלום`) using the documented `U+0591`–`U+05C7` range.

## Outputs Produced / Modified

- `frontend/static/js/api.js` — added `getSrsDue`, `answerSrsItem`,
  `postActivity`, `getDashboard` wrappers; all existing wrappers unchanged.
- `frontend/static/js/tts.js` — generalized `speak(hebrewText)` /
  `createSpeakerButton(hebrewText)` into `speak(text, lang)` /
  `createSpeakerButton(text, lang, labelPrefix)`, per §11.5. Existing
  cancel-before-speak behavior (the mechanism that keeps English/Hebrew
  playback from ever overlapping) is unchanged.
- `frontend/static/js/study.js` — added a second (English) speaker button
  next to each item's meaning; fires `POST /api/activity {mode:"study"}`
  once, fire-and-forget, after vocabulary loads successfully; Hebrew word
  display now goes through `nikud.render()`.
- `frontend/static/js/quiz.js` — existing Hebrew prompt speaker now passes
  `"he-IL"` explicitly (no English control added, per Decision 3); fires
  `POST /api/activity {mode:"quiz"}` once in `showSummary()`; prompt display
  goes through `nikud.render()`. Answer-choice buttons unchanged (English
  meanings, not Hebrew — no nikud transform applies).
- `frontend/static/js/exam.js` — pre-submit prompt speaker now passes
  `"he-IL"` explicitly (no per-choice English control, per Decision 3);
  post-submit review rows (previously had **no** speaker control at all)
  now get a Hebrew speaker for the prompt and an independent English
  speaker for `correct_answer` (the item's actual meaning, not necessarily
  what the learner selected) — shown on its own "Meaning: …" line so the
  English control always speaks what it's next to regardless of whether the
  learner answered correctly. Both prompt displays go through
  `nikud.render()`.
- `frontend/static/js/nikud.js` (new) — owns `localStorage["nikud_hidden"]`;
  `strip()` removes `U+0591`–`U+05C7`; `render(el, text)` / `applyTo(el)` /
  `applyAll()` implement the `data-hebrew` convention so toggling re-applies
  to every Hebrew element currently on screen without a reload;
  `createToggleControl()` / `mount()` build and wire a navbar switch,
  auto-mounted into `#nikud-toggle-slot` on `DOMContentLoaded` on every page.
- `frontend/static/js/srs.js` (new) — fetches `GET /api/srs/due` once,
  steps through the batch one item at a time (quiz.js's UX shape),
  posts each answer to `POST /api/srs/{id}/answer`, shows immediate
  correct/incorrect feedback, shows a "nothing due" empty state on `[]`,
  and a completion summary at the end of the batch with a way to check
  again.
- `frontend/static/js/dashboard.js` (new) — fetches `GET /api/dashboard` on
  load (no caching), renders the streak count, a per-lesson mastery list
  (progress bar + percent, or a "Not yet attempted" state for `null`), and
  the cross-lesson exam history table.
- `frontend/srs.html` (new), `frontend/dashboard.html` (new) — new pages
  following the existing multi-page Bootstrap structure (same navbar,
  CDN links, `app.css`), reachable via new "Review" / "Dashboard" nav links
  added to every page.
- `frontend/index.html`, `lesson.html`, `study.html`, `quiz.html`,
  `exam.html`, `admin.html` — navbar extended with "Dashboard" and "Review"
  links plus a `#nikud-toggle-slot`; `nikud.js` added to each page's script
  list (loaded before the page's own script). `index.html` still serves as
  `/`'s default (Catalog unchanged) — Dashboard is an added, separately
  reachable view, not a replacement.
- `frontend/static/css/app.css` — small additions for the nikud toggle,
  mastery progress bars, and the streak card; no changes to existing rules.
- `instructions/enhancements/summaries/07-frontend.md` (this file, new).

## Key Decisions

Documented in "Work Completed" above (all three were escalated and
confirmed by the coordinator before implementation): Exam review rows get
both Hebrew and English controls; no new Admin Hebrew listing; SRS queue is
single-fetch/single-pass per session.

Additional judgment calls made within normal implementation discretion:

- `nikud.js`'s strip regex uses explicit `֑`-`ׇ` escapes rather
  than literal characters, to stay unambiguous regardless of file/editor
  encoding — verified via Node to strip a real vocalized word
  (`שָׁלוֹם` → `שלום`) correctly.
- `tts.js`'s `createSpeakerButton` third argument (`labelPrefix`) is used
  only for the accessible label/tooltip ("Play Hebrew/English pronunciation
  of …") so the two per-item controls are distinguishable to assistive
  tech; it has no effect on playback.
- Catalog (`catalog.js`) and the Lesson screen (`lesson.js`) were not
  changed beyond their navbar/script-tag additions — neither currently
  renders Hebrew text (lesson titles and exam-history rows are English/
  numeric only), so there is nothing for `nikud.js` to strip there yet; the
  toggle control is still present on both pages for discoverability and
  consistency, per the brief's "reachable from a settings area or a
  persistently accessible control."
- `admin.js` itself was not modified — the Hebrew `<input>` for adding
  vocabulary is explicitly excluded from the toggle per Decision 5/§11.5,
  and there is no existing read-only Hebrew listing in Admin to wire up.

## Open Questions & Concerns

- None blocking. Seed vocabulary contains no nikud characters (confirmed
  again during this stage's verification), so the nikud toggle is a visual
  no-op against seed content until nikud-bearing text exists — this was
  already flagged by Stages 5/6 and is expected, not a bug. I additionally
  verified the strip logic itself against a manually-added nikud-bearing
  word via the Admin API, so the mechanism is confirmed correct even though
  the shipped seed data won't visibly exercise it.
- The SRS queue's single-fetch/single-pass behavior (coordinator-confirmed
  default) means a word answered incorrectly won't reappear until the
  learner reopens `/srs.html` (e.g. via the "Check for More" button on the
  completion screen, which just re-fetches). Flagging for Stage 8
  (Verification) so this isn't mistaken for a bug: it's the confirmed,
  intended behavior, not an omission.
- Dashboard/SRS layout, exact wording, and CSS are my own presentational
  choices (no wireframe was provided in the briefs/architecture) — Stage 8
  should verify they satisfy the briefs' acceptance expectations
  functionally, not against any specific visual design.

## Status

- [x] Complete
- [ ] Needs review
