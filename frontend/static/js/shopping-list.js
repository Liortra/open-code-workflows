// shopping-list.js — Shopping List screen (shopping-list.html). Fetches GET
// /api/shopping-list and renders it; PATCH per item on check/uncheck. Since
// the list is always server-derived, the page simply re-fetches on load /
// on request rather than tracking derivation itself. Per
// docs/architecture.md §9/§3.

import { api, escapeHtml, renderAlert } from "./api.js";

const listEl = document.getElementById("shopping-list");
const emptyStateEl = document.getElementById("empty-state");
const alertContainer = document.getElementById("alert-container");
const refreshBtn = document.getElementById("refresh-btn");

function renderItems(items) {
  listEl.innerHTML = "";
  emptyStateEl.classList.toggle("d-none", items.length > 0);
  for (const item of items) {
    const li = document.createElement("li");
    li.className = `list-group-item shopping-item${item.checked ? " checked" : ""}`;
    const checkboxId = `item-${encodeURIComponent(item.ingredient)}`;
    li.innerHTML = `
      <div class="form-check">
        <input class="form-check-input item-checkbox" type="checkbox" id="${checkboxId}" ${item.checked ? "checked" : ""} />
        <label class="form-check-label" for="${checkboxId}">
          ${escapeHtml(item.ingredient)} — <span class="text-muted">${escapeHtml(item.quantity)}</span>
        </label>
      </div>
    `;
    const checkbox = li.querySelector(".item-checkbox");
    checkbox.addEventListener("change", () => toggleItem(item.ingredient, checkbox, li));
    listEl.appendChild(li);
  }
}

async function loadList() {
  try {
    const items = await api.getShoppingList();
    renderAlert(alertContainer, "");
    renderItems(items);
  } catch (err) {
    renderAlert(alertContainer, "Could not load the shopping list. Please try again.");
  }
}

async function toggleItem(ingredient, checkbox, li) {
  const desired = checkbox.checked;
  checkbox.disabled = true;
  try {
    await api.setShoppingListItemChecked(ingredient, desired);
    li.classList.toggle("checked", desired);
  } catch (err) {
    // Revert the checkbox on failure (e.g. the ingredient dropped off the
    // list because it was just unplanned elsewhere) and refresh from the
    // server so the page reflects real state.
    checkbox.checked = !desired;
    renderAlert(alertContainer, "Could not update that item. Refreshing the list.");
    await loadList();
    return;
  } finally {
    checkbox.disabled = false;
  }
}

refreshBtn.addEventListener("click", loadList);

loadList();
