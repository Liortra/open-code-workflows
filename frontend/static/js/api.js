/**
 * api.js — the sole place that knows endpoint URLs/payload shapes.
 * Every function returns a Promise that resolves to parsed JSON, or rejects
 * with an Error whose message is the backend's `detail` (or a generic
 * fallback) on a non-2xx response.
 */

const API_BASE = "/api";

async function request(path, options) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (body && body.detail) {
        detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
      }
    } catch (_) {
      // response body wasn't JSON; keep the generic message
    }
    throw new Error(detail);
  }
  if (response.status === 204) return null;
  return response.json();
}

const api = {
  // Lessons / Catalog
  getLessons: () => request("/lessons"),
  getLesson: (lessonId) => request(`/lessons/${lessonId}`),

  // Study
  getVocabulary: (lessonId) => request(`/lessons/${lessonId}/vocabulary`),

  // Quiz (stateless)
  getQuiz: (lessonId) => request(`/lessons/${lessonId}/quiz`),
  checkQuizAnswer: (lessonId, vocabularyId, selected) =>
    request(`/lessons/${lessonId}/quiz/check`, {
      method: "POST",
      body: JSON.stringify({ vocabulary_id: vocabularyId, selected }),
    }),

  // Exam
  getExam: (lessonId) => request(`/lessons/${lessonId}/exam`),
  submitExam: (lessonId, answers) =>
    request(`/lessons/${lessonId}/exam/submit`, {
      method: "POST",
      body: JSON.stringify({ answers }),
    }),
  getExamHistory: (lessonId) => request(`/lessons/${lessonId}/exam/history`),

  // Admin
  createLesson: (title) =>
    request("/admin/lessons", {
      method: "POST",
      body: JSON.stringify({ title }),
    }),
  createVocabulary: (lessonId, hebrew, meaning) =>
    request("/admin/vocabulary", {
      method: "POST",
      body: JSON.stringify({ lesson_id: lessonId, hebrew, meaning }),
    }),
};
