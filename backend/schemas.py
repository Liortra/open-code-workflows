"""Pydantic request/response models for the API, per docs/architecture.md §6."""

from typing import Literal

from pydantic import BaseModel


class Lesson(BaseModel):
    id: int
    title: str
    vocabulary_count: int


class LessonDetail(Lesson):
    has_exam_history: bool


class VocabularyItem(BaseModel):
    id: int
    hebrew: str
    meaning: str


class Question(BaseModel):
    vocabulary_id: int
    prompt: str
    choices: list[str]


class QuizCheckRequest(BaseModel):
    vocabulary_id: int
    selected: str


class QuizCheckResponse(BaseModel):
    is_correct: bool
    correct_answer: str


class ExamAnswer(BaseModel):
    vocabulary_id: int
    selected: str


class ExamSubmitRequest(BaseModel):
    answers: list[ExamAnswer]


class ExamReviewItem(BaseModel):
    vocabulary_id: int
    prompt: str
    selected: str
    correct_answer: str
    is_correct: bool


class ExamSubmitResponse(BaseModel):
    score: int
    total: int
    taken_at: str
    review: list[ExamReviewItem]


class ExamHistoryItem(BaseModel):
    id: int
    score: int
    total: int
    taken_at: str


class CreateLessonRequest(BaseModel):
    title: str


class CreateVocabularyRequest(BaseModel):
    lesson_id: int
    hebrew: str
    meaning: str


class VocabularyCreated(BaseModel):
    id: int
    lesson_id: int
    hebrew: str
    meaning: str


# --- Sprint 01 enhancement, per docs/architecture.md §11.4 ---


class SrsDueItem(BaseModel):
    vocabulary_id: int
    lesson_id: int
    prompt: str
    choices: list[str]


class SrsAnswerRequest(BaseModel):
    selected: str


class SrsAnswerResponse(BaseModel):
    is_correct: bool
    correct_answer: str
    next_due_at: str


# `mode` restricted to the two values this endpoint accepts ("exam"/"srs" are
# valid *stored* activity_log values but are never accepted here — they log
# through their own endpoints per §11.4). An out-of-range value is rejected
# by FastAPI/Pydantic with 422 automatically.
class ActivityRequest(BaseModel):
    mode: Literal["study", "quiz"]


class ActivityResponse(BaseModel):
    mode: Literal["study", "quiz"]
    occurred_at: str


class DashboardLessonItem(BaseModel):
    lesson_id: int
    title: str
    mastery_percent: int | None


class DashboardExamHistoryItem(BaseModel):
    id: int
    lesson_id: int
    lesson_title: str
    score: int
    total: int
    taken_at: str


class DashboardResponse(BaseModel):
    lessons: list[DashboardLessonItem]
    exam_history: list[DashboardExamHistoryItem]
    streak_days: int
