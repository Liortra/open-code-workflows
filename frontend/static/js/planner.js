// planner.js — Meal Planner screen (planner.html). Fetches GET
// /api/meal-plan, renders the 7 day slots exactly as returned (only those 7
// dates are ever offered for assignment), POST/DELETE against
// /api/meal-plan for add/remove, and re-fetches after each change. Per
// docs/architecture.md §9/§3.

import { api, escapeHtml, renderAlert } from "./api.js";

const daysContainer = document.getElementById("planner-days");
const dayTemplate = document.getElementById("day-template");
const alertContainer = document.getElementById("alert-container");

// If the user arrived from a recipe's detail page ("Add to Meal Planner"),
// preselect that recipe in every day's dropdown as a convenience.
const params = new URLSearchParams(window.location.search);
const preselectRecipeId = params.get("recipe");

let allRecipes = [];

function buildRecipeOptions(select) {
  select.innerHTML = "";
  for (const recipe of allRecipes) {
    const option = document.createElement("option");
    option.value = String(recipe.id);
    option.textContent = `${recipe.title} (${recipe.category})`;
    if (preselectRecipeId && String(recipe.id) === preselectRecipeId) {
      option.selected = true;
    }
    select.appendChild(option);
  }
}

function renderDay(day) {
  const node = dayTemplate.content.firstElementChild.cloneNode(true);
  node.querySelector(".day-weekday").textContent = day.weekday;
  node.querySelector(".day-date").textContent = day.date;

  const entriesEl = node.querySelector(".day-entries");
  if (day.entries.length === 0) {
    const li = document.createElement("li");
    li.className = "list-group-item text-muted";
    li.textContent = "Nothing planned yet.";
    entriesEl.appendChild(li);
  } else {
    for (const entry of day.entries) {
      const li = document.createElement("li");
      li.className = "list-group-item";
      li.innerHTML = `
        <span>${escapeHtml(entry.title)} <span class="badge text-bg-secondary">${escapeHtml(entry.category)}</span></span>
        <button type="button" class="btn btn-sm btn-outline-danger remove-entry" aria-label="Remove">&times;</button>
      `;
      li.querySelector(".remove-entry").addEventListener("click", () =>
        removeEntry(entry.id)
      );
      entriesEl.appendChild(li);
    }
  }

  const select = node.querySelector(".recipe-select");
  buildRecipeOptions(select);

  const form = node.querySelector(".assign-form");
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const recipeId = Number(select.value);
    if (!recipeId) return;
    assignRecipe(recipeId, day.date);
  });

  return node;
}

async function loadPlan() {
  try {
    // Fetched sequentially rather than with Promise.all: the backend's
    // per-request SQLite connection (backend/database.py's get_db
    // dependency) is not safe under concurrent requests from the same
    // client (observed as a 500 "SQLite objects created in a thread can
    // only be used in that same thread" error when both calls raced). This
    // is a request-sequencing choice only, not a backend fix — see
    // summaries/07-frontend.md.
    const plan = await api.getMealPlan();
    const recipes = allRecipes.length ? allRecipes : await api.listRecipes();
    allRecipes = recipes;
    renderAlert(alertContainer, "");
    daysContainer.innerHTML = "";
    for (const day of plan.days) {
      daysContainer.appendChild(renderDay(day));
    }
  } catch (err) {
    renderAlert(alertContainer, "Could not load the meal plan. Please try again.");
  }
}

async function assignRecipe(recipeId, date) {
  try {
    await api.createMealPlanEntry(recipeId, date);
    await loadPlan();
  } catch (err) {
    if (err.status === 400) {
      renderAlert(alertContainer, "That date is outside the current planning window.");
    } else if (err.status === 404) {
      renderAlert(alertContainer, "That recipe could not be found.");
    } else {
      renderAlert(alertContainer, "Could not add that recipe to the plan. Please try again.");
    }
  }
}

async function removeEntry(entryId) {
  try {
    await api.deleteMealPlanEntry(entryId);
    await loadPlan();
  } catch (err) {
    renderAlert(alertContainer, "Could not remove that entry. Please try again.");
  }
}

loadPlan();
