# <Unit or course name>: Overview Files

This folder holds the files that cut across all <N> chapters of this unit (or of the whole course when it has no units). You do **not** need to read them in order, and most of them are used *after* the chapters, not before. This page tells you what each one is for.

## The short version

1. Want to **practise**? Open [09-study-player.html](09-study-player.html) (double-click it).
2. Want a **map** before you start? Read [01-concept-map.md](01-concept-map.md).
3. Done with the chapters and want a **quick revision**? Read [02-cram-sheet.md](02-cram-sheet.md).
4. Want to **test yourself** across everything? Take the [checkpoint](03-final-quiz.md) and then the [timed exam](07-exam.md).
5. After a session the tutor fills [05-score-tracker.md](05-score-tracker.md) and [06-revisit-list.md](06-revisit-list.md); you only read them.

## What each file is for

| File | What it is | Use it when | Contains answers? |
|---|---|---|---|
| [01-concept-map.md](01-concept-map.md) | heading-only outline of every chapter | before you start | no |
| [02-cram-sheet.md](02-cram-sheet.md) | counts, exact numbers, look-alikes, lists and traps in one place | in your last days, after the chapters | facts only |
| [03-final-quiz.md](03-final-quiz.md) | a cumulative checkpoint mixing all chapters | when the chapters are done | no |
| [04-final-quiz-key.md](04-final-quiz-key.md) | its key with the reason each wrong option is wrong | only after you answered | **yes** |
| [05-score-tracker.md](05-score-tracker.md) | your results per chapter | to see progress | no |
| [06-revisit-list.md](06-revisit-list.md) | missed concepts with memory anchors | every day or two, then a few days later, then the week after | facts only |
| [07-exam.md](07-exam.md) | one timed exam over every chapter (<N> questions, <M> minutes) | once, in one sitting, no notes | no |
| [08-exam-key.md](08-exam-key.md) | its key with chapter and source of each question | only after the exam | **yes** |
| [09-study-player.html](09-study-player.html) | the interactive player: quiz, flashcards, exam, progress, results download | any time you want to practise | answers show after you choose |

## Which files you can leave alone

- The answer keys until you have answered the matching quiz or exam.
- The score tracker and revisit list until your first graded session.
- Nothing here should be deleted: the quiz, key and flashcard files are the source the player is built from.

## About the player

Built from the lesson, quiz, key and flashcard files (the first tab shows the lessons, the same text as the `01-lesson.md` files); do not edit the HTML by hand (rebuild with `make_player.py`). Progress is saved in that browser only; In the Lesson tab you can select text to highlight it or add a note; the Notes tab lists them. They are saved as `06-notes.md` in the chapter folder (connect your course folder in Chrome or Edge, or download the file), and are yours: nothing regenerates them. "Download my results" saves a file (scores and notes) for your tutor. It works offline.

Back to the [README](../README.md).
