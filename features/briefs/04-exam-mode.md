# Brief: Exam Mode

## Purpose

Gives the user a formal, recorded assessment of their mastery of a lesson's
vocabulary, distinct from Quiz mode's low-stakes practice, so their result
becomes part of a lasting record they (and, per Admin scope, potentially an
Admin) can look back on.

## Expected behavior

1. The user enters Exam mode for a chosen lesson.
2. Exam mode presents the lesson's vocabulary as multiple-choice questions,
   covering all 10 vocabulary items of the lesson.
3. Unlike Quiz mode, the user is not told whether each answer was
   correct/incorrect while taking the exam — feedback is withheld until the
   exam is fully submitted.
4. Once the user has answered all questions, they submit the exam.
5. On submission, the user is shown their final score (e.g. "8/10 correct")
   and, for review, which questions they got right or wrong with the correct
   answers.
6. The exam result (lesson, score, and date/time taken) is saved as a
   permanent record for that lesson.
7. The user can take the exam for a lesson again later; a new attempt
   produces a new saved result (it does not require deleting the old one).
8. The user can view past exam results for a lesson (e.g. most recent score,
   or a history of attempts) from the lesson screen.

## Inputs / outputs

- **Input:** the user's selected answer for each multiple-choice question,
  and the final submit action.
- **Output:** a saved score record for the lesson, and an end-of-exam review
  showing which answers were right/wrong.

## User-visible behavior

- Questions are presented without per-question feedback (no immediate
  right/wrong indicator while answering).
- After submitting, the user sees their overall score and a review of each
  question's correct answer.
- The lesson screen shows that an exam result exists for that lesson (e.g.
  the saved score), once the user has taken it at least once.

## Constraints

- Exam mode must use multiple-choice questions only (per the concept) and
  must cover all 10 vocabulary items of the lesson.
- No feedback is given per question during the exam; only after submission.
- Exam results must be saved and remain viewable after the user leaves the
  exam (this is what distinguishes Exam from Quiz).
- The user must answer all questions before the exam can be submitted (an
  exam cannot be partially submitted).

## Basic acceptance expectations

- Entering Exam mode for a lesson presents multiple-choice questions over
  all 10 of that lesson's vocabulary items.
- No correct/incorrect feedback is shown while answering.
- Submitting the exam shows a final score and a review of answers.
- The exam result is saved and can be seen again later (e.g. by returning to
  the lesson).
- Retaking the exam produces a new saved result.
