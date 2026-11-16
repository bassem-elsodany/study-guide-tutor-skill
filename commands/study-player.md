---
description: Build the interactive study player for a unit - lessons as pages, click-through quiz with feedback, spaced flashcards, timed exam, progress and a results file
argument-hint: "[unit folder: the course folder if flat, or one module, week, part ...]"
allowed-tools: Read, Write, Grep, Glob, Bash(python3:*)
---

# /study-player

Build the interactive player for the unit folder at `$ARGUMENTS` with the `study-guide-tutor-skill` skill:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/study-guide-tutor-skill/scripts/make_player.py <unit folder>
```

It writes `<unit folder>/00-overview/09-study-player.html`: one file, opened by double-click, no install and no network. Run `audit_quiz.py` first and fix any error, because the player shows every question exactly as the quiz and key files state it. Tell the student what is in it (Lesson, Quiz, Flashcards, Exam, Progress; the Lesson tab is the chapter's Markdown as a page, so it must be rebuilt after a lesson edit) and that they can select lesson text to highlight it or add a note (saved as `06-notes.md` in the chapter folder: press "Connect my course folder" in Chrome or Edge, or download the file elsewhere), that "Download my results" produces a file (with their notes) they can send back, which you then turn into `05-review.md`, a score-tracker update and a revisit list.
