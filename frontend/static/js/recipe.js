// recipe.js — Recipe detail screen (recipe.html). Fetches GET
// /api/recipes/{id}, shows full ingredients/steps, and links into Cook Mode
// and the Meal Planner for that recipe. Per docs/architecture.md §9/§3.

import { api, renderAlert } from "./api.js";

const alertContainer = document.getElementById("alert-container");
const detailEl = document.getElementById("recipe-detail");
const titleEl = document.getElementById("recipe-title");
const categoryEl = document.getElementById("recipe-category");
const ingredientListEl = document.getElementById("ingredient-list");
const stepListEl = document.getElementById("step-list");
const cookModeLink = document.getElementById("cook-mode-link");
const planLink = document.getElementById("plan-link");

const params = new URLSearchParams(window.location.search);
const recipeId = params.get("id");

function renderRecipe(recipe) {
  document.title = `Recipe Box — ${recipe.title}`;
  titleEl.textContent = recipe.title;
  categoryEl.textContent = recipe.category;

  ingredientListEl.innerHTML = "";
  for (const ingredient of recipe.ingredients) {
    const li = document.createElement("li");
    li.className = "list-group-item";
    const quantity = ingredient.quantity ? `${ingredient.quantity} ` : "";
    li.textContent = `${quantity}${ingredient.name}`;
    ingredientListEl.appendChild(li);
  }

  stepListEl.innerHTML = "";
  for (const step of recipe.steps) {
    const li = document.createElement("li");
    li.className = "list-group-item";
    li.textContent = step;
    stepListEl.appendChild(li);
  }

  cookModeLink.href = `/cook.html?id=${encodeURIComponent(recipe.id)}`;
  planLink.href = `/planner.html?recipe=${encodeURIComponent(recipe.id)}`;

  detailEl.classList.remove("d-none");
}

async function load() {
  if (!recipeId) {
    renderAlert(alertContainer, "No recipe was specified.");
    return;
  }
  try {
    const recipe = await api.getRecipe(recipeId);
    renderAlert(alertContainer, "");
    renderRecipe(recipe);
  } catch (err) {
    if (err.status === 404) {
      renderAlert(alertContainer, "That recipe could not be found.");
    } else {
      renderAlert(alertContainer, "Could not load this recipe. Please try again.");
    }
  }
}

load();
