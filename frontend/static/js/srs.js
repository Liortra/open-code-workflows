/**
 * srs.js — Spaced Repetition "Due for Review" queue (srs.html).
 *
 * Fetches GET /api/srs/due once and steps through the returned batch one
 * item at a time client-side (same UX shape as quiz.js), posting each
 * answer to POST /api/srs/{vocabulary_id}/answer and showing immediate
 * correct/incorrect feedback (docs/architecture.md §11.4/§11.5,
 * features/briefs/02-spaced-repetition.md).
 *
 * This is a single fixed batch per session: an incorrectly-answered word
 * becomes due again immediately server-side, but it is not re-fetched
 * within the same pass — it will reappear the next time the learner opens
 * the queue. The queue itself never computes "due-ness" or scheduling; it
 * only renders what the backend returns.
 */

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

let items = [];
let currentIndex = 0;
let correctCount = 0;
let answered = false;

async function startReview() {
  const statusEl = document.getElementById("status");
  document.getElementById("review-content").classList.add("d-none");
  document.getElementById("summary").classList.add("d-none");
  document.getElementById("empty-state").classList.add("d-none");

  statusEl.textContent = "Loading due items…";
  try {
    items = await api.getSrsDue();
    currentIndex = 0;
    correctCount = 0;
    statusEl.textContent = "";

    if (items.length === 0) {
      document.getElementById("empty-state").classList.remove("d-none");
      return;
    }

    document.getElementById("review-content").classList.remove("d-none");
    renderItem();
  } catch (err) {
    statusEl.textContent = `Could not load due items: ${err.message}`;
  }
}

function renderItem() {
  const item = items[currentIndex];
  answered = false;

  document.getElementById("progress").textContent =
    `Item ${currentIndex + 1} of ${items.length}`;
  nikud.render(document.getElementById("prompt"), item.prompt);

  const speakerSlot = document.getElementById("speaker-slot");
  speakerSlot.innerHTML = "";
  speakerSlot.appendChild(tts.createSpeakerButton(item.prompt, "he-IL", "Hebrew"));

  const choicesEl = document.getElementById("choices");
  choicesEl.innerHTML = "";
  for (const choice of item.choices) {
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

  const item = items[currentIndex];
  const choicesEl = document.getElementById("choices");
  for (const btn of choicesEl.querySelectorAll("button")) {
    btn.disabled = true;
  }

  try {
    const result = await api.answerSrsItem(item.vocabulary_id, selected);
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
      <div class="alert alert-warning mb-0">Could not record answer: ${escapeHtml(err.message)}</div>
    `;
    answered = false;
    for (const btn of choicesEl.querySelectorAll("button")) {
      btn.disabled = false;
    }
  }
}

function nextItem() {
  currentIndex += 1;
  if (currentIndex >= items.length) {
    showSummary();
  } else {
    renderItem();
  }
}

function showSummary() {
  document.getElementById("review-content").classList.add("d-none");
  document.getElementById("summary").classList.remove("d-none");
  document.getElementById("summary-score").textContent =
    `You reviewed ${items.length} item${items.length === 1 ? "" : "s"}, ${correctCount} correct.`;
}

document.getElementById("next-btn").addEventListener("click", nextItem);
document.getElementById("restart-btn").addEventListener("click", startReview);
document.getElementById("refresh-btn").addEventListener("click", startReview);

startReview();
