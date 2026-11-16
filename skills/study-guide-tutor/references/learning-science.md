# Learning science layer

What turns generated material into retention. Apply it after the chapters exist.

## Spacing (do not skip)
- Misses come back the **next day**, **3 days later**, **a week later**, **two weeks later**, each time as a **fresh variant** (new scenario, new option order), never the same question.
- `scripts/review_schedule.py --start D --exam D --chapters N` prints a dated plan: study days walk the chapters, each chapter's revisit dates are added, and the last ten days are reserved for exams and the revisit list.
- Less than a week left: cram mode (cram sheet, flashcards of misses, one mock exam, revisit list).

## Interleaving
- Chapter quizzes are blocked practice; they build the first pass. After two or three chapters run a **cumulative mixed quiz** (questions from earlier chapters, unlabeled) so the student must recognize which concept applies, which is what the exam does.
- Confusable pairs are drilled together (the cram sheet has them in one table).

## The domain exam
- One timed exam per domain covering every chapter: `scripts/make_domain_exam.py DOMAIN --count N` (about 35-60 questions, about 1.5 minutes each, chapters mixed and unlabeled, every chapter at least 2 questions, proportional otherwise). Hints are off during the exam and offered in review.
- After it, use the key's chapter column to see weak chapters, add them to the revisit list, and schedule retakes. The short final quiz remains a checkpoint, not a substitute.
- Before the real exam, one **mock exam across all domains** at the real length and time limit.

## Exam blueprint
- Ask the learner (multiple choice) whether they have the official exam blueprint with domain weights. If yes, weight study time, domain-exam length and mock-exam mix by it; if no, weight by slide count and say so.

## Adaptive difficulty
- If a chapter score is above 85% on first attempt, shorten its review and move on; below 60%, reteach with a new analogy and a smaller step before the retake. Record the decision in `05-review.md`.
- Re-profile (Phase 0) when the learner says it is too easy or too hard, or when results show the level is wrong.

## Active recall
- Before each new chapter ask the learner to recite one list or distinction from the previous one from memory; fill the gaps, then continue.
