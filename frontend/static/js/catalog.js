// catalog.js — Recipe Catalog screen (index.html). Fetches and renders
// GET /api/recipes (with the optional category filter as a query param) and
// links each recipe to recipe.html?id=... . Per docs/architecture.md §9/§3.

import { api, CATEGORIES, escapeHtml, renderAlert } from "./api.js";

const categoryFilterEl = document.getElementById("category-filter");
const listEl = document.getElementById("recipe-list");
const emptyStateEl = document.getElementById("empty-state");
const alertContainer = document.getElementById("alert-container");

// Build the "All" + one button per fixed category filter bar.
for (const category of CATEGORIES) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "btn btn-outline-primary";
  btn.dataset.category = category;
  btn.textContent = category;
  categoryFilterEl.appendChild(btn);
}

function setActiveButton(category) {
  for (const btn of categoryFilterEl.querySelectorAll("button")) {
    btn.classList.toggle("active", btn.dataset.category === (category || ""));
  }
}

function renderRecipes(recipes) {
  listEl.innerHTML = "";
  emptyStateEl.classList.toggle("d-none", recipes.length > 0);
  for (const recipe of recipes) {
    const col = document.createElement("div");
    col.className = "col";
    col.innerHTML = `
      <a class="card recipe-card text-decoration-none text-body" href="/recipe.html?id=${encodeURIComponent(recipe.id)}">
        <div class="card-body">
          <h2 class="h5 card-title">${escapeHtml(recipe.title)}</h2>
          <span class="badge text-bg-secondary">${escapeHtml(recipe.category)}</span>
        </div>
      </a>
    `;
    listEl.appendChild(col);
  }
}

async function loadRecipes(category) {
  try {
    const recipes = await api.listRecipes(category || undefined);
    renderAlert(alertContainer, "");
    renderRecipes(recipes);
  } catch (err) {
    renderAlert(alertContainer, "Could not load recipes. Please try again.");
  }
}

categoryFilterEl.addEventListener("click", (event) => {
  const btn = event.target.closest("button[data-category]");
  if (!btn) return;
  const category = btn.dataset.category;
  setActiveButton(category);
  loadRecipes(category);
});

loadRecipes("");
