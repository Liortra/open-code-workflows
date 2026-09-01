/**
 * dashboard.js — Progress Dashboard (dashboard.html).
 *
 * Fetches GET /api/dashboard fresh on every load (no caching — the backend
 * is the sole source of truth for mastery/history/streak; this module only
 * renders what it returns, per docs/architecture.md §11.4/§11.5,
 * features/briefs/03-progress-dashboard.md). Read-only: viewing the
 * dashboard never writes anything.
 */

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

async function renderDashboard() {
  const statusEl = document.getElementById("status");
  const contentEl = document.getElementById("dashboard-content");
  contentEl.classList.add("d-none");

  statusEl.textContent = "Loading dashboard…";
  try {
    const data = await api.getDashboard();
    statusEl.textContent = "";
    contentEl.classList.remove("d-none");

    renderStreak(data.streak_days);
    renderLessons(data.lessons);
    renderExamHistory(data.exam_history);
  } catch (err) {
    statusEl.textContent = `Could not load dashboard: ${err.message}`;
  }
}

function renderStreak(streakDays) {
  document.getElementById("streak-count").textContent = streakDays;
  document.getElementById("streak-label").textContent =
    streakDays === 1 ? "day" : "days";
}

function renderLessons(lessons) {
  const el = document.getElementById("lesson-mastery");
  if (lessons.length === 0) {
    el.innerHTML = '<p class="text-muted">No lessons yet.</p>';
    return;
  }

  el.innerHTML = lessons
    .map((lesson) => {
      const hasMastery = lesson.mastery_percent !== null;
      const barWidth = hasMastery ? lesson.mastery_percent : 0;
      const masteryLabel = hasMastery
        ? `${lesson.mastery_percent}%`
        : "Not yet attempted";
      return `
        <div class="mastery-row">
          <div class="d-flex justify-content-between">
            <a href="/lesson.html?id=${lesson.lesson_id}" class="text-decoration-none">
              ${escapeHtml(lesson.title)}
            </a>
            <span class="${hasMastery ? "" : "text-muted fst-italic"}">${masteryLabel}</span>
          </div>
          <div class="progress" role="progressbar" aria-valuenow="${barWidth}" aria-valuemin="0" aria-valuemax="100">
            <div class="progress-bar ${hasMastery ? "" : "bg-secondary"}" style="width: ${barWidth}%"></div>
          </div>
        </div>
      `;
    })
    .join("");
}

function renderExamHistory(examHistory) {
  const el = document.getElementById("exam-history");
  if (examHistory.length === 0) {
    el.innerHTML = '<p class="text-muted">No exam attempts yet.</p>';
    return;
  }

  const rows = examHistory
    .map(
      (attempt) => `
        <tr>
          <td><a href="/lesson.html?id=${attempt.lesson_id}" class="text-decoration-none">${escapeHtml(attempt.lesson_title)}</a></td>
          <td>${attempt.score} / ${attempt.total}</td>
          <td>${escapeHtml(attempt.taken_at)}</td>
        </tr>
      `
    )
    .join("");

  el.innerHTML = `
    <table class="table table-sm table-bordered bg-white">
      <thead><tr><th>Lesson</th><th>Score</th><th>Taken At</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

renderDashboard();
