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
            <div class="hebrew-text"></div>
            <div class="text-muted d-flex align-items-center gap-2 meaning-row">
              <span class="meaning-text">${escapeHtml(item.meaning)}</span>
            </div>
          </div>
        </div>
      `;
      nikud.render(card.querySelector(".hebrew-text"), item.hebrew);
      const cardBody = card.querySelector(".card-body");
      const controls = document.createElement("div");
      controls.className = "d-flex gap-1";
      controls.appendChild(tts.createSpeakerButton(item.hebrew, "he-IL", "Hebrew"));
      controls.appendChild(tts.createSpeakerButton(item.meaning, "en-US", "English"));
      cardBody.appendChild(controls);
      listEl.appendChild(card);
    }

    // Sprint 01 (docs/architecture.md §11.4/§11.5): Study has no other
    // durable completion signal, so it logs once, fire-and-forget, after
    // vocabulary finishes loading successfully.
    api.postActivity("study").catch(() => {
      // Non-fatal: the streak/dashboard just won't reflect this session.
    });
  } catch (err) {
    statusEl.textContent = `Could not load vocabulary: ${err.message}`;
  }
}

renderStudy();
