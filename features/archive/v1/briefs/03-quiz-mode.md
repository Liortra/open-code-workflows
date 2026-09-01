# Brief: Quiz Mode

## Purpose

Lets the user practice a lesson's vocabulary through low-stakes,
self-testing, multiple-choice questions, with immediate feedback and no
permanent consequence, as a step between Study mode and the formal Exam.

## Expected behavior

1. The user enters Quiz mode for a chosen lesson.
2. Quiz mode presents the lesson's vocabulary as multiple-choice questions:
   each question asks the user to identify the correct meaning (or word) for
   one vocabulary item, with one correct option and several incorrect
   options (distractors) drawn from other vocabulary.
3. After the user answers each question, they are immediately told whether
   they were correct, and shown the correct answer if they were wrong.
4. The user progresses through questions covering the lesson's vocabulary
   until the quiz is complete.
5. At the end, the user sees a summary of how many questions they answered
   correctly.
6. The user can retake the quiz for the same lesson as many times as they
   like, immediately or later.
7. Quiz attempts are not saved as a permanent record (see "Constraints" —
   this distinguishes Quiz from Exam, whose results are saved).

## Inputs / outputs

- **Input:** the user's selected answer for each multiple-choice question.
- **Output:** immediate correct/incorrect feedback per question, and an
  end-of-quiz summary score (e.g. "7/10 correct").

## User-visible behavior

- Each question shows a prompt (a vocabulary item) and a set of selectable
  answer choices.
- Selecting an answer immediately reveals whether it was right or wrong.
- A final score is shown at the end of the quiz.
- A "retake" option is available after finishing, or by re-entering Quiz
  mode from the lesson screen.

## Constraints

- Quiz mode must use multiple-choice questions only (per the concept).
- Feedback must be given per question (not withheld until the end), which is
  what distinguishes Quiz from Exam.
- Quiz results are not persisted/saved anywhere the user can view later;
  each attempt is self-contained and disappears once the user leaves.
- Quiz mode must be retakeable without limit.

## Basic acceptance expectations

- Entering Quiz mode for a lesson presents multiple-choice questions covering
  that lesson's vocabulary.
- Answering a question immediately shows correct/incorrect feedback.
- Finishing the quiz shows a summary score.
- The quiz can be retaken any number of times.
- No quiz attempt appears in any saved history or record after the user
  leaves the quiz.
