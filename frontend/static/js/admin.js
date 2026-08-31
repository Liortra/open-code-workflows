// admin.js — Admin screen (admin.html). A form for title, category (select
// from the four fixed values), a repeatable ingredient row (quantity +
// name), and a repeatable step row (ordered text), posting to POST
// /api/recipes and surfacing 422 field errors inline. Per
// docs/architecture.md §9/§3. No edit/delete UI, per the Admin brief.

import { api, CATEGORIES, formatValidationErrors, renderAlert } from "./api.js";

const form = document.getElementById("recipe-form");
const titleInput = document.getElementById("title-input");
const categorySelect = document.getElementById("category-select");
const ingredientRowsEl = document.getElementById("ingredient-rows");
const stepRowsEl = document.getElementById("step-rows");
const ingredientRowTemplate = document.getElementById("ingredient-row-template");
const stepRowTemplate = document.getElementById("step-row-template");
const addIngredientBtn = document.getElementById("add-ingredient-btn");
const addStepBtn = document.getElementById("add-step-btn");
const submitBtn = document.getElementById("submit-btn");
const alertContainer = document.getElementById("alert-container");
const successPanel = document.getElementById("success-panel");
const successMessage = document.getElementById("success-message");
const viewRecipeLink = document.getElementById("view-recipe-link");
const addAnotherBtn = document.getElementById("add-another-btn");

for (const category of CATEGORIES) {
  const option = document.createElement("option");
  option.value = category;
  option.textContent = category;
  categorySelect.appendChild(option);
}

function addIngredientRow() {
  const node = ingredientRowTemplate.content.firstElementChild.cloneNode(true);
  node.querySelector(".remove-row").addEventListener("click", () => {
    node.remove();
    ensureMinimumRows();
  });
  ingredientRowsEl.appendChild(node);
}

function addStepRow() {
  const node = stepRowTemplate.content.firstElementChild.cloneNode(true);
  node.querySelector(".remove-row").addEventListener("click", () => {
    node.remove();
    ensureMinimumRows();
  });
  stepRowsEl.appendChild(node);
}

function ensureMinimumRows() {
  if (ingredientRowsEl.children.length === 0) addIngredientRow();
  if (stepRowsEl.children.length === 0) addStepRow();
}

addIngredientBtn.addEventListener("click", addIngredientRow);
addStepBtn.addEventListener("click", addStepRow);

// Start with one blank row of each, since at least one is required.
addIngredientRow();
addStepRow();

function collectIngredients() {
  const rows = [...ingredientRowsEl.querySelectorAll(".repeatable-row")];
  const ingredients = [];
  const errors = [];
  for (const row of rows) {
    const quantity = row.querySelector(".ingredient-quantity").value.trim();
    const name = row.querySelector(".ingredient-name").value.trim();
    if (!quantity && !name) continue; // fully blank row: ignore, not an error
    if (!name) {
      errors.push("Each ingredient needs a name (quantity alone is not enough).");
      continue;
    }
    ingredients.push({ quantity: quantity || null, name });
  }
  if (ingredients.length === 0) {
    errors.push("At least one ingredient is required.");
  }
  return { ingredients, errors };
}

function collectSteps() {
  const rows = [...stepRowsEl.querySelectorAll(".repeatable-row")];
  const steps = [];
  for (const row of rows) {
    const text = row.querySelector(".step-text").value.trim();
    if (text) steps.push(text);
  }
  const errors = [];
  if (steps.length === 0) {
    errors.push("At least one step is required.");
  }
  return { steps, errors };
}

function validateClientSide() {
  const errors = [];
  const title = titleInput.value.trim();
  if (!title) errors.push("Title is required.");
  if (!categorySelect.value) errors.push("Category is required.");

  const { ingredients, errors: ingredientErrors } = collectIngredients();
  const { steps, errors: stepErrors } = collectSteps();
  errors.push(...ingredientErrors, ...stepErrors);

  return { title, category: categorySelect.value, ingredients, steps, errors };
}

function resetForm() {
  form.reset();
  ingredientRowsEl.innerHTML = "";
  stepRowsEl.innerHTML = "";
  addIngredientRow();
  addStepRow();
  renderAlert(alertContainer, "");
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  renderAlert(alertContainer, "");
  successPanel.classList.add("d-none");

  const { title, category, ingredients, steps, errors } = validateClientSide();
  if (errors.length > 0) {
    renderErrors(errors);
    return;
  }

  submitBtn.disabled = true;
  try {
    const created = await api.createRecipe({ title, category, ingredients, steps });
    form.classList.add("d-none");
    successMessage.textContent = `"${created.title}" was created successfully.`;
    viewRecipeLink.href = `/recipe.html?id=${encodeURIComponent(created.id)}`;
    successPanel.classList.remove("d-none");
  } catch (err) {
    if (err.status === 422) {
      renderErrors(formatValidationErrors(err.body));
    } else {
      renderAlert(alertContainer, "Could not create the recipe. Please try again.");
    }
  } finally {
    submitBtn.disabled = false;
  }
});

addAnotherBtn.addEventListener("click", () => {
  successPanel.classList.add("d-none");
  form.classList.remove("d-none");
  resetForm();
});

function renderErrors(messages) {
  alertContainer.innerHTML = "";
  const alert = document.createElement("div");
  alert.className = "alert alert-danger";
  alert.setAttribute("role", "alert");
  const heading = document.createElement("p");
  heading.className = "mb-1 fw-semibold";
  heading.textContent = "Please fix the following before submitting:";
  alert.appendChild(heading);
  const list = document.createElement("ul");
  list.className = "mb-0";
  for (const message of messages) {
    const li = document.createElement("li");
    li.textContent = message;
    list.appendChild(li);
  }
  alert.appendChild(list);
  alertContainer.appendChild(alert);
}
