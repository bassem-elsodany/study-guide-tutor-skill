---
description: Quiz one chapter (or the whole domain), grade the answers with memory anchors, and queue the misses for a retake
argument-hint: "[chapter number | domain | grade 1B 2D 3A ...]"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(python3:*)
---

# /study-quiz

Run the quiz phase of the `study-guide-tutor` skill for `$ARGUMENTS`.

- **No answers given:** present the chapter's questions (4 options each, hints on request only, answer key kept separate).
- **Answers given** (for example `1B 2D 3A`): grade every question individually, name the correct option, explain why the student's choice was the trap, add a short memory anchor and the source location, report the block score, write `05-review.md`, update the score tracker and revisit list, and offer a retake of the misses with fresh variants.
- For hands-on practice, offer `/study-player`: the same questions as a clickable page with instant feedback, flashcards and a timed exam.
- Before presenting a newly written quiz, run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/study-guide-tutor/scripts/audit_quiz.py <course root>` and fix every error.
