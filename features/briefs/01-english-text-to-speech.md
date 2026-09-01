# Brief: English Text-to-Speech

## Purpose

Extends the existing Text-to-Speech capability (`features/archive/v1/briefs/06-text-to-speech.md`)
so a learner can also hear a vocabulary item's English meaning spoken aloud,
not only its Hebrew pronunciation. This lets Study mode work as a
listen-and-recall drill in both directions (hear the Hebrew, hear the
English), instead of only ever hearing the Hebrew word.

## Expected behavior

1. Wherever a vocabulary item's English meaning (translation) is shown to
   the user — today this is Study mode, and anywhere else a meaning is
   displayed such as Quiz/Exam answer choices or review screens — a control
   is available to play that meaning's spoken English audio, alongside the
   existing Hebrew pronunciation control for the same item.
2. The user activates the English control (e.g. taps/clicks a speaker icon
   next to the English text) independently of the Hebrew control; playing
   the English audio does not require first playing the Hebrew audio, and
   vice versa.
3. The app speaks the English meaning aloud using the device/browser's
   built-in speech synthesis, exactly as the existing Hebrew pronunciation
   does — no separate audio files are recorded or stored, and no external
   TTS service/API is called, for either language.
4. The user can replay the English pronunciation as many times as they
   like, the same as the existing Hebrew control.
5. Only one utterance plays at a time across both languages: activating
   either the Hebrew or English control while any pronunciation (Hebrew or
   English) is already playing stops the current playback and starts the
   new one — audio never stacks or overlaps, whether within one language or
   across both.

## Inputs / outputs

- **Input:** the user's tap/click on the English pronunciation control for a
  given vocabulary item's meaning.
- **Output:** audible English speech of that item's meaning. (Hebrew
  pronunciation input/output is unchanged from the existing feature.)

## User-visible behavior

- A visible, discoverable control (e.g. speaker icon) next to each
  displayed English meaning, mirroring the existing Hebrew word's control,
  wherever a meaning is shown alongside its control today (Study mode at
  minimum).
- Pressing it produces audible English speech within the browser, with no
  visible loading delay beyond what the browser's speech synthesis itself
  takes — matching the existing Hebrew control's responsiveness.
- The existing Hebrew pronunciation control and its behavior are unchanged;
  this feature adds a second, independent control per item rather than
  replacing or altering the first.

## Constraints

- English pronunciation is produced via the browser's built-in speech
  synthesis (client-side), the same mechanism as the existing Hebrew
  pronunciation; it does not depend on an external TTS API, API key, or
  network call, and does not require pre-recorded audio files.
- If the user's browser/device does not support speech synthesis, the
  English control may be disabled or show that pronunciation is
  unavailable, consistent with how the existing Hebrew control handles this
  case; this must not block any other feature from working.
- Does not change where or how the Hebrew word itself is shown or spoken;
  it only adds the ability to also hear the English meaning.
- Text-to-Speech (English or Hebrew) only reads vocabulary words/meanings;
  it is not used for full sentences, UI text, or instructions elsewhere in
  the app — unchanged from the existing constraint.

## Basic acceptance expectations

- Every vocabulary item shown in Study mode (where the Hebrew word and its
  English meaning are shown together, per the existing Study Mode brief)
  has a working English pronunciation control in addition to the existing
  Hebrew control.
- Activating the English control produces audible English speech for that
  item's meaning.
- Activating either the Hebrew or English control while the other is
  currently playing stops the current audio and plays the newly requested
  one, with no overlap.
- The English control can be used repeatedly without errors.
- The existing Hebrew-only pronunciation behavior continues to work exactly
  as before for every vocabulary item.
- No lesson, quiz, or exam requires network access or an API key for either
  Hebrew or English pronunciation to work.
