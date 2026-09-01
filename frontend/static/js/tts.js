/**
 * tts.js — the sole place that touches SpeechSynthesis.
 * Cancels any in-flight utterance before starting a new one, so playback
 * never stacks or overlaps — across languages too (Sprint 01, per
 * docs/architecture.md §11.5 / features/briefs/01-english-text-to-speech.md
 * point 5): every speak() call already cancels first, regardless of lang,
 * so "only one utterance plays at a time across both languages" falls out
 * of the existing implementation for free.
 */

const tts = {
  isAvailable() {
    return typeof window !== "undefined" && "speechSynthesis" in window;
  },

  /**
   * Speaks `text` using the given BCP-47 `lang` (e.g. "he-IL" or "en-US").
   */
  speak(text, lang) {
    if (!this.isAvailable()) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang;
    window.speechSynthesis.speak(utterance);
  },

  /**
   * Creates a speaker button that speaks `text` (in `lang`) when clicked.
   * `labelPrefix` (e.g. "Hebrew" / "English") is used only for the
   * accessible label/tooltip, so the two per-item controls (Hebrew word,
   * English meaning) are distinguishable to assistive tech.
   * Disabled (not hidden) with a tooltip if speech synthesis is unavailable,
   * so layout stays consistent and the rest of the page keeps working.
   */
  createSpeakerButton(text, lang, labelPrefix) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "btn btn-outline-secondary btn-sm speaker-btn";
    button.innerHTML = "&#128266;";
    button.setAttribute("aria-label", `Play ${labelPrefix} pronunciation of ${text}`);
    if (!this.isAvailable()) {
      button.disabled = true;
      button.title = "Pronunciation is unavailable in this browser";
    } else {
      button.title = `Play ${labelPrefix} pronunciation`;
      button.addEventListener("click", () => this.speak(text, lang));
    }
    return button;
  },
};
