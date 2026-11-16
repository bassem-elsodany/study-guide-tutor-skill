# Grading files

Created only when the learner has actually answered a quiz.

## 05-review.md (per chapter)
Banner, then: score line (right / wrong / skipped / hinted, accuracy), a table per question (Q, learner's letter, key, result, slide), and for every miss: why the chosen option was the trap, a **new analogy**, a one-line **memory anchor**, and the slide. End with "Retake" listing the missed concepts and the date of the fresh-variant retake.

## 05-score-tracker.md (domain)
One row per chapter plus the domain exam and final quiz: taught, quiz written, questions, quiz taken (date), right, wrong, skipped, hinted, score, accuracy, cleared. "Cleared" means every miss was answered correctly on a fresh variant. Update the progress line ("N of M chapters cleared").

## 06-revisit-list.md (domain)
Table: chapter, concept missed, correct answer, memory anchor, slide, last revisited, cleared (date). Add a row on every miss and every hinted question; remove a row only after it clears on a fresh variant.

## Revisit deck
Append the anchors of missed concepts to the chapter's `02-flashcards.csv` (or create `revisit-deck.csv` in `00-overview/`) as question,answer rows. Include an everyday-picture card for each missed concept.

## Retakes
Fresh variants only: new scenario, new option order, same concept. Whatever still fails stays on the revisit list and is scheduled with `scripts/review_schedule.py`.
