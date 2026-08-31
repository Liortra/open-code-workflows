# Summary: Frontend Engineer (Stage 07)

- **Date:** 2026-08-31
- **Author / Executor:** Claude (agent)
- **Instruction file:** `instructions/build/07-frontend.md`
- **Commit:** `stage 07: implement frontend per architecture`

## Work Completed

Implemented the full browser frontend under `frontend/` exactly per
`docs/architecture.md` §2/§8: six static, multi-page Bootstrap (CDN, no build
step) HTML pages plus one JS module per page, `api.js` as the sole owner of
endpoint URLs/payload shapes, and `tts.js` as the sole wrapper around
`window.speechSynthesis`. Verified end-to-end against a live `uvicorn`
instance using headless Chrome (via puppeteer-core): lesson catalog listing
(21 lessons incl. one added during testing), lesson screen mode links, Study
mode (all 10 vocabulary items shown word+meaning together, speaker buttons
present), Quiz mode (per-question `POST /quiz/check` with immediate
correct/incorrect feedback, client-tallied end score, retake), Exam mode
(submit disabled until every question answered, feedback withheld until
`POST /exam/submit`, score + review rendered, result persists and shows in
the lesson screen's exam history), and Admin (add lesson, add vocabulary
with lesson picker sourced from `GET /api/lessons`, both reflected in the
catalog immediately with no publish step). Also verified graceful handling
of an unknown lesson id (404 surfaced as an inline message, no crash) and a
missing `id` query param. The dev SQLite file was deleted after testing so
the next stage starts from a fresh seed (20 lessons × 10 vocab items).

## Outputs Produced

- `frontend/index.html`, `lesson.html`, `study.html`, `quiz.html`,
  `exam.html`, `admin.html` — one static page per screen, Bootstrap 5.3.3
  via CDN, no SPA router.
- `frontend/static/css/app.css` — small overrides (RTL Hebrew text styling,
  correct/incorrect choice and review coloring).
- `frontend/static/js/api.js` — `fetch()` wrappers for every endpoint in
  architecture §6; the only module that knows a URL or payload shape.
- `frontend/static/js/tts.js` — `SpeechSynthesis` wrapper; cancels any
  in-flight utterance before speaking, and disables (not hides) the speaker
  control when unsupported.
- `frontend/static/js/catalog.js`, `lesson.js`, `study.js`, `quiz.js`,
  `exam.js`, `admin.js` — one module per screen, each owning only that
  page's DOM and API calls.
- `summaries/07-frontend.md` (this file).

## Key Decisions

- **Study mode layout:** the brief left "one at a time or a browsable list"
  open. Implemented as a single scrollable list of all 10 vocabulary cards
  (word + meaning + speaker button) rather than a one-item-at-a-time
  carousel — satisfies "revisit any item any number of times" with no extra
  navigation state to manage.
- **Exam layout:** all questions are rendered on one page (radio-button
  groups) rather than paginated one-at-a-time, so "submit disabled until
  every question is answered" is a simple, visible client-side check against
  a `Map` of answered vocabulary ids.
- **Question direction (Hebrew → meaning):** followed architecture §5
  exactly — prompt is the Hebrew word, choices are meanings — for both Quiz
  and Exam.
- **XSS hygiene:** all admin-authored text (lesson titles, Hebrew words,
  meanings) that's interpolated into `innerHTML` templates is escaped via a
  small `escapeHtml()` helper in each screen module, since Admin content is
  free-text and ends up rendered on every other screen.

## Open Questions & Concerns

- None from the architecture or briefs — the API contract in
  `docs/architecture.md` §6 matched the live backend router code exactly, so
  no assumptions or deviations were needed.
- Verification stage: no favicon is defined (an unstyled 404 for
  `/favicon.ico` in browser console) — cosmetic only, not part of any brief
  or the architecture's file list, so left as-is.

## Status

- [x] Complete
- [ ] Needs review
