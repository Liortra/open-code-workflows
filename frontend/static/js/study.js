/** study.js — Study mode (study.html). Word + meaning always shown together. */

function getLessonId() {
  return new URLSearchParams(window.location.search).get("id");
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

async function renderStudy() {
  const statusEl = document.getElementById("status");
  const listEl = document.getElementById("vocab-list");
  const lessonId = getLessonId();

  if (!lessonId) {
    statusEl.textContent = "No lesson selected.";
    return;
  }
  document.getElementById("back-link").href = `/lesson.html?id=${lessonId}`;

  statusEl.textContent = "Loading vocabulary…";
  try {
    const [lesson, vocabulary] = await Promise.all([
      api.getLesson(lessonId),
      api.getVocabulary(lessonId),
    ]);

    document.getElementById("page-title").textContent = `Study: ${lesson.title}`;
    statusEl.textContent = "";

    for (const item of vocabulary) {
      const card = document.createElement("div");
      card.className = "card vocab-card";
      card.innerHTML = `
        <div class="card-body">
          <div>
            <div class="hebrew-text">${escapeHtml(item.hebrew)}</div>
            <div class="text-muted">${escapeHtml(item.meaning)}</div>
          </div>
        </div>
      `;
      card.querySelector(".card-body").appendChild(tts.createSpeakerButton(item.hebrew));
      listEl.appendChild(card);
    }
  } catch (err) {
    statusEl.textContent = `Could not load vocabulary: ${err.message}`;
  }
}

renderStudy();
