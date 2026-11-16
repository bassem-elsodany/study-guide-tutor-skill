---
description: Build the interactive study player for a unit - click-through quiz with feedback, spaced flashcards, timed exam, progress and a results file
argument-hint: "[unit folder, e.g. domain-1]"
allowed-tools: Read, Write, Grep, Glob, Bash(python3:*)
---

# /study-player

Build the interactive player for the unit folder at `$ARGUMENTS` with the `study-guide-tutor` skill:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/study-guide-tutor/scripts/make_player.py <unit folder>
```

It writes `<unit folder>/00-overview/09-study-player.html`: one file, opened by double-click, no install and no network. Run `audit_quiz.py` first and fix any error, because the player shows every question exactly as the quiz and key files state it. Tell the student what is in it (Quiz, Flashcards, Exam, Progress) and that "Download my results" produces a file they can send back, which you then turn into `05-review.md`, a score-tracker update and a revisit list.
