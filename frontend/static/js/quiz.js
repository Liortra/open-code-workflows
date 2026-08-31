/**
 * quiz.js — Quiz mode (quiz.html). Per-question POST /quiz/check with
 * immediate feedback; score is tallied client-side from those responses
 * (nothing is persisted server-side, per 03-quiz-mode.md).
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
let currentIndex = 0;
let correctCount = 0;
let answered = false;

async function startQuiz() {
  const statusEl = document.getElementById("status");
  lessonId = getLessonId();

  if (!lessonId) {
    statusEl.textContent = "No lesson selected.";
    return;
  }
  document.getElementById("back-link").href = `/lesson.html?id=${lessonId}`;
  document.getElementById("summary-back-link").href = `/lesson.html?id=${lessonId}`;

  statusEl.textContent = "Loading quiz…";
  document.getElementById("quiz-content").classList.add("d-none");
  document.getElementById("summary").classList.add("d-none");

  try {
    const [lesson, quizQuestions] = await Promise.all([
      api.getLesson(lessonId),
      api.getQuiz(lessonId),
    ]);
    document.getElementById("page-title").textContent = `Quiz: ${lesson.title}`;
    questions = quizQuestions;
    currentIndex = 0;
    correctCount = 0;
    statusEl.textContent = "";

    if (questions.length === 0) {
      statusEl.textContent = "This lesson has no vocabulary yet.";
      return;
    }

    document.getElementById("quiz-content").classList.remove("d-none");
    renderQuestion();
  } catch (err) {
    statusEl.textContent = `Could not load quiz: ${err.message}`;
  }
}

function renderQuestion() {
  const question = questions[currentIndex];
  answered = false;

  document.getElementById("progress").textContent =
    `Question ${currentIndex + 1} of ${questions.length}`;
  document.getElementById("prompt").textContent = question.prompt;

  const speakerSlot = document.getElementById("speaker-slot");
  speakerSlot.innerHTML = "";
  speakerSlot.appendChild(tts.createSpeakerButton(question.prompt));

  const choicesEl = document.getElementById("choices");
  choicesEl.innerHTML = "";
  for (const choice of question.choices) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "btn btn-outline-primary choice-btn text-start";
    btn.textContent = choice;
    btn.addEventListener("click", () => selectAnswer(choice, btn));
    choicesEl.appendChild(btn);
  }

  document.getElementById("feedback").innerHTML = "";
  document.getElementById("next-btn").classList.add("d-none");
}

async function selectAnswer(selected, clickedBtn) {
  if (answered) return;
  answered = true;

  const question = questions[currentIndex];
  const choicesEl = document.getElementById("choices");
  for (const btn of choicesEl.querySelectorAll("button")) {
    btn.disabled = true;
  }

  try {
    const result = await api.checkQuizAnswer(lessonId, question.vocabulary_id, selected);
    if (result.is_correct) {
      correctCount += 1;
      clickedBtn.classList.add("is-correct");
      document.getElementById("feedback").innerHTML =
        '<div class="alert alert-success mb-0">Correct!</div>';
    } else {
      clickedBtn.classList.add("is-incorrect");
      for (const btn of choicesEl.querySelectorAll("button")) {
        if (btn.textContent === result.correct_answer) {
          btn.classList.add("is-correct");
        }
      }
      document.getElementById("feedback").innerHTML = `
        <div class="alert alert-danger mb-0">
          Incorrect. Correct answer: ${escapeHtml(result.correct_answer)}
        </div>
      `;
    }
    document.getElementById("next-btn").classList.remove("d-none");
  } catch (err) {
    document.getElementById("feedback").innerHTML = `
      <div class="alert alert-warning mb-0">Could not check answer: ${escapeHtml(err.message)}</div>
    `;
    answered = false;
    for (const btn of choicesEl.querySelectorAll("button")) {
      btn.disabled = false;
    }
  }
}

function nextQuestion() {
  currentIndex += 1;
  if (currentIndex >= questions.length) {
    showSummary();
  } else {
    renderQuestion();
  }
}

function showSummary() {
  document.getElementById("quiz-content").classList.add("d-none");
  document.getElementById("summary").classList.remove("d-none");
  document.getElementById("summary-score").textContent =
    `You scored ${correctCount} / ${questions.length}`;
}

document.getElementById("next-btn").addEventListener("click", nextQuestion);
document.getElementById("retake-btn").addEventListener("click", startQuiz);

startQuiz();
