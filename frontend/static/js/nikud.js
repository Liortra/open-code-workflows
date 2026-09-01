/**
 * nikud.js — the sole place that touches the nikud (vowel points) show/hide
 * setting. Client-side only (Sprint 01, docs/architecture.md §11.4/§11.5;
 * features/briefs/04-nikud-toggle.md): persisted in `localStorage`, no
 * backend involvement, no change to how Hebrew text is stored.
 *
 * Convention: every place Hebrew text is rendered into the DOM sets the
 * element's original, fully-vocalized text on a `data-hebrew` attribute.
 * `nikud.js` owns setting that element's visible `textContent` from the
 * attribute according to the current toggle state, and re-applies itself to
 * every `[data-hebrew]` element on toggle change so text already on screen
 * updates immediately, without a reload.
 *
 * Per Decision 5 (features/briefs/04-nikud-toggle.md, docs/architecture.md
 * §11.5): the Admin "Add Vocabulary" Hebrew <input> is never wrapped this
 * way and always shows exactly what the admin types.
 */

const nikud = {
  STORAGE_KEY: "nikud_hidden",
  // Hebrew points/accents range (U+0591-U+05C7), per
  // instructions/enhancements/summaries/04-system-engineering.md. Written as
  // explicit \u escapes (rather than literal characters) to stay
  // unambiguous regardless of file/editor encoding.
  NIKUD_RANGE: /[\u0591-\u05C7]/g,

  isHidden() {
    try {
      return window.localStorage.getItem(this.STORAGE_KEY) === "true";
    } catch (_) {
      return false;
    }
  },

  setHidden(hidden) {
    try {
      window.localStorage.setItem(this.STORAGE_KEY, hidden ? "true" : "false");
    } catch (_) {
      // localStorage unavailable (e.g. private mode) — setting won't persist
      // across sessions, but the toggle still works for the current page.
    }
    this.applyAll();
  },

  /** Strips nikud characters from `text`, leaving consonantal text only. */
  strip(text) {
    return text.replace(this.NIKUD_RANGE, "");
  },

  /**
   * Sets `el`'s visible text from its `data-hebrew` attribute according to
   * the current toggle state. Call this (instead of setting textContent
   * directly) anywhere Hebrew text is rendered into the DOM.
   */
  applyTo(el) {
    const original = el.getAttribute("data-hebrew");
    if (original === null) return;
    el.textContent = this.isHidden() ? this.strip(original) : original;
  },

  /** Re-applies the current toggle state to every [data-hebrew] element on the page. */
  applyAll() {
    document.querySelectorAll("[data-hebrew]").forEach((el) => this.applyTo(el));
  },

  /**
   * Renders `text` into `el` as Hebrew display text: stores the original on
   * `data-hebrew` and sets the currently-visible text accordingly. Use this
   * instead of `el.textContent = text` for any Hebrew word/prompt.
   */
  render(el, text) {
    el.setAttribute("data-hebrew", text);
    this.applyTo(el);
  },

  /**
   * Builds the navbar toggle control (a labeled checkbox) and wires it to
   * the current/stored state. Safe to call on every page.
   */
  createToggleControl() {
    const wrapper = document.createElement("div");
    wrapper.className = "form-check form-switch nikud-toggle text-light d-flex align-items-center";

    const input = document.createElement("input");
    input.className = "form-check-input";
    input.type = "checkbox";
    input.role = "switch";
    input.id = "nikud-toggle";
    input.checked = !this.isHidden();

    const label = document.createElement("label");
    label.className = "form-check-label ms-1";
    label.setAttribute("for", "nikud-toggle");
    label.textContent = "Nikud";

    input.addEventListener("change", () => this.setHidden(!input.checked));

    wrapper.appendChild(input);
    wrapper.appendChild(label);
    return wrapper;
  },

  /** Mounts the toggle control into `#nikud-toggle-slot` if present on the page. */
  mount() {
    const slot = document.getElementById("nikud-toggle-slot");
    if (slot) {
      slot.appendChild(this.createToggleControl());
    }
    this.applyAll();
  },
};

document.addEventListener("DOMContentLoaded", () => nikud.mount());
