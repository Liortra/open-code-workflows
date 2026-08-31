/**
 * admin.js — Admin (admin.html). Add-only: create a lesson, or add a
 * vocabulary item to an existing/just-created lesson. No edit/delete UI.
 */

function showFormStatus(elementId, message, isError) {
  const el = document.getElementById(elementId);
  el.className = isError ? "text-danger mt-2" : "text-success mt-2";
  el.textContent = message;
}

async function loadLessonOptions(selectedId) {
  const select = document.getElementById("vocab-lesson");
  const lessons = await api.getLessons();
  select.innerHTML = lessons
    .map((lesson) => `<option value="${lesson.id}">${escapeHtml(lesson.title)}</option>`)
    .join("");
  if (selectedId) {
    select.value = String(selectedId);
  }
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

async function handleCreateLesson(event) {
  event.preventDefault();
  const titleInput = document.getElementById("lesson-title");
  const title = titleInput.value.trim();
  if (!title) return;

  try {
    const lesson = await api.createLesson(title);
    showFormStatus("lesson-form-status", `Added lesson "${lesson.title}".`, false);
    titleInput.value = "";
    await loadLessonOptions(lesson.id);
  } catch (err) {
    showFormStatus("lesson-form-status", `Could not add lesson: ${err.message}`, true);
  }
}

async function handleCreateVocabulary(event) {
  event.preventDefault();
  const lessonSelect = document.getElementById("vocab-lesson");
  const hebrewInput = document.getElementById("vocab-hebrew");
  const meaningInput = document.getElementById("vocab-meaning");

  const lessonId = lessonSelect.value;
  const hebrew = hebrewInput.value.trim();
  const meaning = meaningInput.value.trim();
  if (!lessonId || !hebrew || !meaning) return;

  try {
    const vocab = await api.createVocabulary(Number(lessonId), hebrew, meaning);
    showFormStatus(
      "vocab-form-status",
      `Added "${vocab.hebrew}" (${vocab.meaning}) to the selected lesson.`,
      false
    );
    hebrewInput.value = "";
    meaningInput.value = "";
  } catch (err) {
    showFormStatus("vocab-form-status", `Could not add vocabulary: ${err.message}`, true);
  }
}

document.getElementById("lesson-form").addEventListener("submit", handleCreateLesson);
document.getElementById("vocab-form").addEventListener("submit", handleCreateVocabulary);

loadLessonOptions().catch((err) => {
  showFormStatus("vocab-form-status", `Could not load lessons: ${err.message}`, true);
});
