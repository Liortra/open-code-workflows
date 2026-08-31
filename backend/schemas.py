"""Pydantic request/response models for the API, per docs/architecture.md §6."""

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
