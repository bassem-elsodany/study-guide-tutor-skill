---
description: Start or continue a study course from your material - intake, ingest, propose chapters, then teach block by block
argument-hint: "[path to the material or the course folder]"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(python3:*)
---

# /study

Load the `study-guide-tutor` skill and follow its teaching loop for the material at `$ARGUMENTS` (or ask where it is).

1. If a `learner-profile.md` exists at the course root, show it in one line and ask only whether it still holds; otherwise run the multiple-choice intake from `references/intake-analysis.md` first. Generate nothing before the profile is saved.
2. Extract the source once: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/study-guide-tutor/scripts/source_text.py extract <material>`, read it all, build the fact ledger.
3. Propose the chapter list (with source ranges) and confirm the folder layout once.
4. Teach the first chapter: lesson, then quiz. Never advance without the student's go-ahead.

Say which study mode you picked (full, cram, weak-area, orientation). See `/study-cram`, `/study-weak`, `/study-quiz`, `/study-check`.
