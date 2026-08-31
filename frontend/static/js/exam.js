/**
 * exam.js — Exam mode (exam.html). All answers are collected client-side;
 * submission is blocked until every question has an answer. No per-question
 * feedback is shown before submit (per 04-exam-mode.md).
 */

function getLessonId() {
  return new URLSearchParams(window.location.search).get("id");
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

let lessonId = null;
let questions = [];
const selectedAnswers = new Map();

async function startExam() {
  const statusEl = document.getElementById("status");
  lessonId = getLessonId();

  if (!lessonId) {
    statusEl.textContent = "No lesson selected.";
    return;
  }
  document.getElementById("back-link").href = `/lesson.html?id=${lessonId}`;
  document.getElementById("results-back-link").href = `/lesson.html?id=${lessonId}`;

  statusEl.textContent = "Loading exam…";
  document.getElementById("exam-content").classList.add("d-none");
  document.getElementById("results").classList.add("d-none");
  selectedAnswers.clear();

  try {
    const [lesson, examQuestions] = await Promise.all([
      api.getLesson(lessonId),
      api.getExam(lessonId),
    ]);
    document.getElementById("page-title").textContent = `Exam: ${lesson.title}`;
    questions = examQuestions;
    statusEl.textContent = "";

    if (questions.length === 0) {
      statusEl.textContent = "This lesson has no vocabulary yet.";
      return;
    }

    renderQuestions();
    document.getElementById("exam-content").classList.remove("d-none");
  } catch (err) {
    statusEl.textContent = `Could not load exam: ${err.message}`;
  }
}

function renderQuestions() {
  const container = document.getElementById("questions");
  container.innerHTML = "";

  questions.forEach((question, index) => {
    const card = document.createElement("div");
    card.className = "card";
    const groupName = `question-${question.vocabulary_id}`;

    const choicesHtml = question.choices
      .map(
        (choice, choiceIndex) => `
          <div class="form-check">
            <input class="form-check-input" type="radio" name="${groupName}"
                   id="${groupName}-${choiceIndex}" value="${escapeHtml(choice)}">
            <label class="form-check-label" for="${groupName}-${choiceIndex}">
              ${escapeHtml(choice)}
            </label>
          </div>
        `
      )
      .join("");

    card.innerHTML = `
      <div class="card-body">
        <div class="d-flex align-items-center gap-2 mb-2">
          <span class="text-muted">Question ${index + 1} of ${questions.length}</span>
        </div>
        <div class="d-flex align-items-center gap-2 mb-3">
          <span class="hebrew-text">${escapeHtml(question.prompt)}</span>
          <span class="speaker-slot"></span>
        </div>
        ${choicesHtml}
      </div>
    `;
    card.querySelector(".speaker-slot").appendChild(tts.createSpeakerButton(question.prompt));

    for (const input of card.querySelectorAll('input[type="radio"]')) {
      input.addEventListener("change", () => {
        selectedAnswers.set(question.vocabulary_id, input.value);
        updateSubmitState();
      });
    }

    container.appendChild(card);
  });
}

function updateSubmitState() {
  const submitBtn = document.getElementById("submit-btn");
  submitBtn.disabled = selectedAnswers.size < questions.length;
}

async function submitExam() {
  const submitBtn = document.getElementById("submit-btn");
  submitBtn.disabled = true;

  const answers = questions.map((q) => ({
    vocabulary_id: q.vocabulary_id,
    selected: selectedAnswers.get(q.vocabulary_id),
  }));

  try {
    const result = await api.submitExam(lessonId, answers);
    showResults(result);
  } catch (err) {
    document.getElementById("status").textContent = `Could not submit exam: ${err.message}`;
    submitBtn.disabled = false;
  }
}

function showResults(result) {
  document.getElementById("exam-content").classList.add("d-none");
  document.getElementById("results").classList.remove("d-none");
  document.getElementById("results-score").textContent =
    `Score: ${result.score} / ${result.total}`;

  const reviewEl = document.getElementById("review");
  reviewEl.innerHTML = "";
  for (const item of result.review) {
    const row = document.createElement("div");
    row.className = `p-2 review-item ${item.is_correct ? "is-correct" : "is-incorrect"}`;
    row.innerHTML = `
      <div class="hebrew-text">${escapeHtml(item.prompt)}</div>
      <div>Your answer: ${escapeHtml(item.selected)}</div>
      ${
        item.is_correct
          ? ""
          : `<div>Correct answer: ${escapeHtml(item.correct_answer)}</div>`
      }
    `;
    reviewEl.appendChild(row);
  }
}

document.getElementById("submit-btn").addEventListener("click", submitExam);
document.getElementById("retake-btn").addEventListener("click", startExam);

startExam();
