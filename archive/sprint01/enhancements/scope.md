# Enhancement Scope — Sprint 01

Source: `enhancements/sprint01.md` ("Sprint 01 — Study Aids & Progress
Tracking"). This document records the agreed scope of the enhancement pass in
plain language, with no technical detail. It is the reference for every
downstream stage.

## Items

### a. English Text-to-Speech — **Feature**

**Intent:** Extend the existing text-to-speech capability so it can also
speak the English meaning of a vocabulary item aloud, not only the Hebrew
word. This lets Study mode work as a listen-and-recall drill in both
directions (hear the Hebrew, hear the English), instead of only hearing the
Hebrew pronunciation.

### b. Spaced Repetition (SRS) — **Feature**

**Intent:** Track how well a user recalls each vocabulary word over time,
and use that history to surface a "Due for Review" queue that spans all
lessons. This gives learners a way to review the words they're weakest on
across the whole catalog, rather than only being able to drill one lesson
at a time from start to finish.

### c. Progress Dashboard — **Feature**

**Intent:** Provide a home-screen view that shows, at a glance: per-lesson
mastery percentage, overall exam history, and a day-streak counter. This
surfaces progress that today is only visible by digging into individual
lessons.

### d. Nikud (Vowel Points) Toggle — **Feature**

**Intent:** Add a setting that lets a learner show or hide Hebrew vowel
pointing (nikud). This lets learners practice reading unvocalized Hebrew
text as their skill progresses, rather than always seeing fully vocalized
text.

### e. Boundary

**Intent:** This is a scoped enhancement pass. Only the four features above
(a–d) are in scope. No existing v0.1 behavior outside of these four features
should change — the existing Lesson Catalog, Study mode, Quiz mode, Exam
mode, Admin content management, and existing (Hebrew) text-to-speech
behavior all continue to work as they do today except where a., b., c., or
d. above explicitly extends them.

## Constraints / Boundaries on the Pass

- Scope is limited strictly to items a–d; nothing beyond what is listed in
  `enhancements/sprint01.md` is in scope for this pass.
- No out-of-scope existing (v0.1) behavior should be changed, removed, or
  regressed by this pass.
- This document intentionally contains no API routes, schemas, data models,
  or other implementation detail — those are decided by later stages
  (Feature Decomposition, Feature Brief Writer, Architect, Backend/Frontend
  Engineers).
