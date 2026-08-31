/**
 * tts.js — the sole place that touches SpeechSynthesis.
 * Cancels any in-flight utterance before starting a new one, so playback
 * never stacks or overlaps (per 06-text-to-speech.md).
 */

const tts = {
  isAvailable() {
    return typeof window !== "undefined" && "speechSynthesis" in window;
  },

  speak(hebrewText) {
    if (!this.isAvailable()) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(hebrewText);
    utterance.lang = "he-IL";
    window.speechSynthesis.speak(utterance);
  },

  /**
   * Creates a speaker button that speaks `hebrewText` when clicked.
   * Disabled (not hidden) with a tooltip if speech synthesis is unavailable,
   * so layout stays consistent and the rest of the page keeps working.
   */
  createSpeakerButton(hebrewText) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "btn btn-outline-secondary btn-sm speaker-btn";
    button.innerHTML = "&#128266;";
    button.setAttribute("aria-label", `Play pronunciation of ${hebrewText}`);
    if (!this.isAvailable()) {
      button.disabled = true;
      button.title = "Pronunciation is unavailable in this browser";
    } else {
      button.addEventListener("click", () => this.speak(hebrewText));
    }
    return button;
  },
};
