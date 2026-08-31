/** catalog.js — Lesson Catalog (index.html). Owns only this page's DOM/API calls. */

async function renderCatalog() {
  const statusEl = document.getElementById("status");
  const listEl = document.getElementById("lesson-list");

  statusEl.textContent = "Loading lessons…";
  try {
    const lessons = await api.getLessons();
    statusEl.textContent = "";
    listEl.innerHTML = "";

    if (lessons.length === 0) {
      statusEl.textContent = "No lessons yet.";
      return;
    }

    for (const lesson of lessons) {
      const col = document.createElement("div");
      col.className = "col";
      col.innerHTML = `
        <a href="/lesson.html?id=${lesson.id}" class="text-decoration-none">
          <div class="card h-100 shadow-sm">
            <div class="card-body">
              <h5 class="card-title text-dark">${escapeHtml(lesson.title)}</h5>
              <p class="card-text text-muted mb-0">${lesson.vocabulary_count} vocabulary items</p>
            </div>
          </div>
        </a>
      `;
      listEl.appendChild(col);
    }
  } catch (err) {
    statusEl.textContent = `Could not load lessons: ${err.message}`;
  }
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

renderCatalog();
