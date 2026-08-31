// cook.js — Cook Mode screen (cook.html). Fetches GET /api/recipes/{id}
// once, then is entirely client-side: the current step index lives in
// memory (starting at step 1 each time Cook Mode is entered) and each
// step's checked state lives in sessionStorage under a per-recipe key
// (`cookmode:{id}`), per docs/architecture.md §9/§3. This module never
// calls the backend for step/checkbox state — no such endpoint exists.

import { api, renderAlert } from "./api.js";

const alertContainer = document.getElementById("alert-container");
const cookModeEl = document.getElementById("cook-mode");
const titleEl = document.getElementById("recipe-title");
const indicatorEl = document.getElementById("step-indicator");
const stepTextEl = document.getElementById("step-text");
const checkboxEl = document.getElementById("step-checkbox");
const prevBtn = document.getElementById("prev-btn");
const nextBtn = document.getElementById("next-btn");
const resetBtn = document.getElementById("reset-btn");
const backLink = document.getElementById("back-to-recipe");

const params = new URLSearchParams(window.location.search);
const recipeId = params.get("id");

function storageKey(id) {
  return `cookmode:${id}`;
}

function loadChecked(id, stepCount) {
  try {
    const raw = sessionStorage.getItem(storageKey(id));
    if (raw) {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed) && parsed.length === stepCount) {
        return parsed.map(Boolean);
      }
    }
  } catch {
    // Ignore malformed/unavailable sessionStorage; fall through to a fresh array.
  }
  return new Array(stepCount).fill(false);
}

function saveChecked(id, checked) {
  try {
    sessionStorage.setItem(storageKey(id), JSON.stringify(checked));
  } catch {
    // sessionStorage unavailable (e.g. private browsing) — checkbox state
    // simply won't persist across navigation; not fatal to using Cook Mode.
  }
}

function clearChecked(id) {
  try {
    sessionStorage.removeItem(storageKey(id));
  } catch {
    // See saveChecked above.
  }
}

let recipe = null;
let checked = [];
let currentStep = 0; // in-memory only; resets to 0 (step 1) each page load.

function render() {
  const total = recipe.steps.length;
  indicatorEl.textContent = `Step ${currentStep + 1} of ${total}`;
  stepTextEl.textContent = recipe.steps[currentStep];
  stepTextEl.classList.toggle("step-checked", checked[currentStep]);
  checkboxEl.checked = checked[currentStep];
  prevBtn.disabled = currentStep === 0;
  nextBtn.disabled = currentStep === total - 1;
}

checkboxEl.addEventListener("change", () => {
  checked[currentStep] = checkboxEl.checked;
  saveChecked(recipeId, checked);
  render();
});

prevBtn.addEventListener("click", () => {
  if (currentStep > 0) {
    currentStep -= 1;
    render();
  }
});

nextBtn.addEventListener("click", () => {
  if (currentStep < recipe.steps.length - 1) {
    currentStep += 1;
    render();
  }
});

resetBtn.addEventListener("click", () => {
  checked = new Array(recipe.steps.length).fill(false);
  clearChecked(recipeId);
  render();
});

async function load() {
  if (!recipeId) {
    renderAlert(alertContainer, "No recipe was specified.");
    return;
  }
  backLink.href = `/recipe.html?id=${encodeURIComponent(recipeId)}`;
  try {
    recipe = await api.getRecipe(recipeId);
    renderAlert(alertContainer, "");
    document.title = `Cook Mode — ${recipe.title}`;
    titleEl.textContent = recipe.title;
    checked = loadChecked(recipeId, recipe.steps.length);
    currentStep = 0;
    render();
    cookModeEl.classList.remove("d-none");
  } catch (err) {
    if (err.status === 404) {
      renderAlert(alertContainer, "That recipe could not be found.");
    } else {
      renderAlert(alertContainer, "Could not load this recipe. Please try again.");
    }
  }
}

load();
