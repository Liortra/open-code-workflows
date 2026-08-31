/** lesson.js — Lesson screen (lesson.html). Mode picker + exam history. */

function getLessonId() {
  return new URLSearchParams(window.location.search).get("id");
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

async function renderLesson() {
  const statusEl = document.getElementById("status");
  const contentEl = document.getElementById("lesson-content");
  const lessonId = getLessonId();

  if (!lessonId) {
    statusEl.textContent = "No lesson selected.";
    return;
  }

  statusEl.textContent = "Loading lesson…";
  try {
    const [lesson, history] = await Promise.all([
      api.getLesson(lessonId),
      api.getExamHistory(lessonId),
    ]);

    statusEl.textContent = "";
    contentEl.classList.remove("d-none");

    document.getElementById("lesson-title").textContent = lesson.title;
    document.getElementById(
      "lesson-vocab-count"
    ).textContent = `${lesson.vocabulary_count} vocabulary items`;

    document.getElementById("study-link").href = `/study.html?id=${lessonId}`;
    document.getElementById("quiz-link").href = `/quiz.html?id=${lessonId}`;
    document.getElementById("exam-link").href = `/exam.html?id=${lessonId}`;

    renderExamHistory(history);
  } catch (err) {
    statusEl.textContent = `Could not load lesson: ${err.message}`;
  }
}

function renderExamHistory(history) {
  const el = document.getElementById("exam-history");
  if (history.length === 0) {
    el.innerHTML = '<p class="text-muted">No exam attempts yet.</p>';
    return;
  }

  const rows = history
    .map(
      (attempt) => `
        <tr>
          <td>${attempt.score} / ${attempt.total}</td>
          <td>${escapeHtml(attempt.taken_at)}</td>
        </tr>
      `
    )
    .join("");

  el.innerHTML = `
    <table class="table table-sm table-bordered bg-white">
      <thead><tr><th>Score</th><th>Taken At</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

renderLesson();
