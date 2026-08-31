// api.js — the sole place that knows endpoint URLs/payload shapes, per
// docs/architecture.md §3. Every other frontend module calls the backend
// only through the functions exported here.

const API_BASE = "/api";

// The four fixed recipe categories. Defined once here so every screen that
// needs the list (catalog filter, admin form, etc.) stays in sync.
export const CATEGORIES = ["Breakfast", "Main", "Side", "Dessert"];

/**
 * Low-level fetch wrapper. Resolves with the parsed JSON body on any 2xx
 * response (or `null` for an empty body, e.g. a 204). Rejects with an Error
 * carrying `.status` (HTTP status code) and `.body` (parsed JSON error body,
 * when present) on any non-2xx response, so callers can branch on status
 * codes (404, 422, 400) exactly as docs/architecture.md §7 defines them.
 */
async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  const text = await response.text();
  let body = null;
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      body = text;
    }
  }

  if (!response.ok) {
    const error = new Error(
      `Request to ${path} failed with status ${response.status}`
    );
    error.status = response.status;
    error.body = body;
    throw error;
  }

  return body;
}

export const api = {
  // ---- Recipes / Catalog ------------------------------------------------

  /** GET /api/recipes[?category=...] -> RecipeSummary[] */
  listRecipes(category) {
    const qs = category ? `?category=${encodeURIComponent(category)}` : "";
    return request(`/recipes${qs}`);
  },

  /** GET /api/recipes/{id} -> RecipeDetail */
  getRecipe(id) {
    return request(`/recipes/${encodeURIComponent(id)}`);
  },

  // ---- Admin (create-only) ----------------------------------------------

  /** POST /api/recipes -> RecipeDetail (201) */
  createRecipe(payload) {
    return request("/recipes", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  // ---- Meal Planner -------------------------------------------------------

  /** GET /api/meal-plan -> { days: MealPlanDay[] } */
  getMealPlan() {
    return request("/meal-plan");
  },

  /** POST /api/meal-plan -> { id, recipe_id, date } (201) */
  createMealPlanEntry(recipeId, date) {
    return request("/meal-plan", {
      method: "POST",
      body: JSON.stringify({ recipe_id: recipeId, date }),
    });
  },

  /** DELETE /api/meal-plan/{id} -> no body (204) */
  deleteMealPlanEntry(entryId) {
    return request(`/meal-plan/${encodeURIComponent(entryId)}`, {
      method: "DELETE",
    });
  },

  // ---- Shopping List --------------------------------------------------------

  /** GET /api/shopping-list -> ShoppingListItem[] */
  getShoppingList() {
    return request("/shopping-list");
  },

  /** PATCH /api/shopping-list/{ingredient} -> { ingredient, checked } */
  setShoppingListItemChecked(ingredient, checked) {
    return request(`/shopping-list/${encodeURIComponent(ingredient)}`, {
      method: "PATCH",
      body: JSON.stringify({ checked }),
    });
  },
};

/** Small shared helper: escape text being inserted as HTML. */
export function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value == null ? "" : String(value);
  return div.innerHTML;
}

/** Small shared helper: render a Bootstrap alert with a message. */
export function renderAlert(container, message, kind = "danger") {
  container.innerHTML = "";
  if (!message) return;
  const alert = document.createElement("div");
  alert.className = `alert alert-${kind}`;
  alert.setAttribute("role", "alert");
  alert.textContent = message;
  container.appendChild(alert);
}

/** Turn a FastAPI 422 validation error body into readable lines. */
export function formatValidationErrors(errorBody) {
  if (!errorBody || !Array.isArray(errorBody.detail)) {
    return ["The recipe could not be created. Please check your input."];
  }
  return errorBody.detail.map((item) => {
    const loc = Array.isArray(item.loc)
      ? item.loc.filter((part) => part !== "body").join(" > ")
      : "";
    return loc ? `${loc}: ${item.msg}` : item.msg;
  });
}
