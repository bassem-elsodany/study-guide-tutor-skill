# Lifecycle: from raw material to a finished tutoring bundle

The complete sequence an agent follows to generate (or regenerate, or extend) a study bundle. Each step names the agent or script, what it reads, and the gate that must pass before moving on. `SKILL.md` gives the rules behind each step.

## Read the source once, then work from the cache

Re-reading the original files every time wastes tokens and time. Extract once, index, and work from the extraction:

1. `scripts/source_text.py extract SOURCE.pdf --out assets/SOURCE.slides.txt` writes one line per slide (`[N] text | text`) and records the file's hash, slide count and the slides that have no text layer in `assets/sources.json`. Slides that are only images are read visually once, and their transcription is written into the cache line, so no later step opens the image again.
2. At the start of every session run `scripts/source_text.py check assets`. `fresh` means use the cache; `CHANGED` means the original changed: re-extract, then rebuild whatever depends on it.
3. Read in this order and stop at the first level that answers the question: the chapter's **fact ledger** (every checkable fact with its slide) -> the cache slice for the chapter (`source_text.py slice CACHE START END`) -> the original file (only for a changed hash or an image-only slide).
4. Never paste a whole source into an agent prompt. Give agents paths and a slide range. A chapter slice is a few thousand tokens; the whole deck is about a hundred thousand.

## The steps

| # | Step | Who / what | Reads | Produces | Gate before the next step |
|---|---|---|---|---|---|
| 0 | Intake | the tutor, `references/intake-analysis.md` | the student | `learner-profile.md` | profile saved |
| 1 | Ingest once | `source_text.py extract` | the original files | `assets/*.slides.txt`, `sources.json` | `check` says fresh; image-only slides transcribed |
| 2 | Outline and size chapters | the tutor (teacher persona) | the cache | chapter list with slide ranges; merges/splits recorded | chapters fit the reading budget |
| 3 | Fact ledger | one agent per chapter | the cache slice | `99-fact-ledger.md` | every fact has a slide; contradictions flagged |
| 4 | Teach: write the lesson | `agents/teacher-writer.md`, one agent per chapter | profile, ledger, cache slice, the quiz (for coverage only) | `01-lesson.md` | `check_dump.py`, `check_tricky.py` and `check_findable.py` pass; Mermaid validates |
| 5 | Quiz, key, flashcards | `build_chapter.py` and `references/question-design.md` | ledger, lesson | `03-quiz.md`, `04-answer-key.md`, `02-flashcards.csv` | `audit_quiz.py` passes |
| 6 | Stamp | `apply_banner.py`, `add_toc.py` | the files | banners, contents | `add_toc.py --check` |
| 7 | Unit files | tutor, `make_exam.py` | all chapters | `00-overview/` files, exam, README | `check_bundle.py` passes |
| 8 | Independent fidelity review | `references/fidelity-review.md`, read-only agents | ledger, cache slice, keys | list of wrong keys/facts | all fixed |
| 9 | Student-persona review | `agents/student-reviewer.md`, read-only agents | lesson, quiz, cache slice | cuts and fixes | cuts applied; dump gate and reading load re-run |
| 10 | Teach and grade with the student | the tutor | lesson, quiz | `05-review.md`, tracker, revisit list | student's pace |
| 11 | Wrap up | the tutor | all | readiness summary, take-away artifacts | |

After any change run, in order: `make_exam.py` (if quizzes changed), `apply_banner.py`, `add_toc.py`, `audit_quiz.py`, `check_bundle.py`, `check_dump.py`, `check_tricky.py`, `check_findable.py`, `reading_load.py` -> `make_player.py` (the interactive player, last, so it shows the final questions), then `graphify update .` where a graph exists.

## Standing rules every step obeys

Slide dumps are never allowed. The teacher may merge or split chapters. Files are numbered in reading order and a chapter is one lesson file. Folders mirror the material; helper files do not go in the bundle. Every generated markdown file has a banner and a contents list. Mermaid only, never SVG, ASCII art or screenshots. Material-only unless marked "Outside the material".
