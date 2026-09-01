# Brief: Text-to-Speech

## Purpose

Helps the user learn correct pronunciation of Hebrew vocabulary, which
written text alone cannot convey, by letting them hear any vocabulary item
spoken aloud on demand.

## Expected behavior

1. Wherever a vocabulary item's Hebrew word is shown to the user (Study
   mode, and anywhere else a Hebrew word appears, such as Quiz/Exam question
   prompts if the word itself is shown), a control is available to play its
   spoken pronunciation.
2. The user activates the control (e.g. taps/clicks a speaker icon).
3. The app speaks the Hebrew word aloud using the device/browser's built-in
   speech synthesis — no separate audio files are recorded or stored, and no
   external TTS service/API is called.
4. The user can replay the pronunciation as many times as they like.
5. Only one word is spoken at a time; requesting playback again (e.g. before
   the previous playback finishes, or for a different word) does not stack
   or overlap audio.

## Inputs / outputs

- **Input:** the user's tap/click on a pronunciation control for a given
  vocabulary item.
- **Output:** audible speech of that item's Hebrew word.

## User-visible behavior

- A visible, discoverable control (e.g. speaker icon) next to each Hebrew
  vocabulary word that can be played.
- Pressing it produces audible pronunciation within the browser, with no
  visible loading delay beyond what the browser's speech synthesis itself
  takes.

## Constraints

- Pronunciation is produced via the browser's built-in speech synthesis
  (client-side); it does not depend on an external TTS API, API key, or
  network call, and does not require pre-recorded audio files for the 200
  starting vocabulary items or any items added later via Admin.
- If the user's browser/device does not support speech synthesis, the
  control may be disabled or show that pronunciation is unavailable, but
  this must not block any other feature (Study/Quiz/Exam/Admin/Catalog) from
  working.
- Text-to-Speech only reads vocabulary words; it is not used for full
  sentences, UI text, or instructions elsewhere in the app.

## Basic acceptance expectations

- Every vocabulary item shown in Study mode has a working pronunciation
  control.
- Activating the control produces audible Hebrew speech for that word.
- The control can be used repeatedly without errors.
- No lesson, quiz, or exam requires network access or an API key for
  pronunciation to work.
