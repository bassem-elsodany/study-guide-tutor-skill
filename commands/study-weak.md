---
description: Weak-area loop - take the revisit list, re-quiz it with fresh variants until it clears, then schedule spaced revisits
argument-hint: "[course folder]"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(python3:*)
---

# /study-weak

Run the **weak-area loop** of the `study-guide-tutor` skill on the course at `$ARGUMENTS`: read `06-revisit-list.md` and the score tracker, write fresh-variant questions (new scenario, new option order) for each missed concept, regrade, and repeat to a clean sweep. Then print a dated spaced-review plan: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/study-guide-tutor/scripts/review_schedule.py --help` shows the options.
