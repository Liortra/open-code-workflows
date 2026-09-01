# Brief: Nikud (Vowel Points) Toggle

## Purpose

Adds a setting that lets a learner show or hide Hebrew vowel pointing
(nikud) on displayed Hebrew text, so they can practice reading unvocalized
Hebrew as their skill progresses, instead of always seeing fully vocalized
text as they do today.

## Decision recorded in this brief (per coordinator direction)

Existing and future Hebrew vocabulary content is assumed to already include
nikud (none of the v0.1 briefs describe nikud, but the app's Hebrew text is
taken as already vocalized). This feature is a **display-only, app-wide
show/hide** of nikud characters on top of that existing text — it does not
change how Hebrew words are stored, authored, or spoken, and does not
require Admin-entered content to be entered any differently than today.

## Expected behavior

1. A setting is available to the learner (e.g. a toggle control, reachable
   from a settings area or a persistently accessible control) to show or
   hide nikud.
2. When nikud is set to hidden, every Hebrew word shown anywhere in the app
   is displayed without its vowel points (consonantal text only). When set
   to shown (the current/default behavior), Hebrew words display exactly as
   they do today, fully vocalized.
3. The toggle applies app-wide and consistently across every screen that
   displays Hebrew text: Lesson Catalog (if lesson names include Hebrew),
   Study mode, Quiz mode, Exam mode, and Admin (both when entering new
   content and when displaying existing content) — the learner does not
   have to set it separately per screen or per lesson.
4. Changing the setting takes effect immediately for Hebrew text currently
   on screen and for any Hebrew text displayed afterward, without requiring
   the learner to reload the app or re-enter a lesson.
5. The setting persists across the learner's sessions (it does not silently
   reset to shown/default the next time the app is opened) — consistent
   with this being a single-user app with no login.
6. The Text-to-Speech feature (Hebrew and, per `01-english-text-to-speech.md`,
   English) is unaffected by this toggle: pronunciation is spoken the same
   way regardless of whether nikud is currently shown or hidden on screen.

## Inputs / outputs

- **Input:** the learner's interaction with the nikud show/hide setting
  (e.g. toggling it on or off).
- **Output:** Hebrew text displayed throughout the app immediately reflects
  the current setting (vocalized or unvocalized), with no other visible
  change to the surrounding screen or functionality.

## User-visible behavior

- A discoverable, persistent setting/control for showing or hiding nikud.
- With nikud hidden, Hebrew words appear as consonantal text only, wherever
  they are shown in the app.
- With nikud shown (default), the app looks exactly as it does today.
- The current setting is remembered the next time the learner returns to
  the app.
- No other part of the app's appearance, layout, or behavior changes as a
  result of toggling nikud.

## Constraints

- This is a display-only change: it does not alter the underlying stored
  Hebrew text, does not require re-entering vocabulary, and does not change
  what Admin content authors type in.
- The toggle must not affect pronunciation (Hebrew or English
  Text-to-Speech) — spoken output is identical regardless of the toggle's
  state.
- The toggle must apply consistently everywhere Hebrew text is shown; it
  must not leave some screens vocalized and others not while a single
  setting value is active.
- Existing v0.1 behavior for Lesson Catalog, Study, Quiz, Exam, and Admin
  must otherwise continue exactly as today — this feature only adds the
  nikud show/hide behavior on top of them.
- The setting is global to the single-user app (no per-lesson or per-user
  variation), consistent with the app's no-login, single-user scope.

## Basic acceptance expectations

- Hiding nikud removes vowel points from Hebrew word display across Study,
  Quiz, Exam, Catalog, and Admin screens.
- Showing nikud again restores the original fully vocalized display
  everywhere.
- Toggling the setting takes effect without requiring a page reload or
  re-navigation to see updated text on the current screen where feasible,
  and at minimum takes effect on the next screen/navigation.
- The setting's value is still in effect (not reset) after leaving and
  reopening the app.
- Playing Hebrew or English pronunciation produces the same audio whether
  nikud is currently shown or hidden.
