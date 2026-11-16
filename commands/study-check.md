---
description: Run every quality gate on a generated course - quiz audit, bundle consistency, no slide dumps, tricky parts, findable answers, contents, reading load
argument-hint: "[course folder, default .]"
allowed-tools: Read, Grep, Glob, Bash(python3:*)
---

# /study-check

Run the gates of the `study-guide-tutor-skill` skill on the course folder `${ARGUMENTS:-.}`, in this order, and report each result plainly (fix nothing unless asked):

```bash
S=${CLAUDE_PLUGIN_ROOT}/skills/study-guide-tutor-skill/scripts
python3 $S/add_toc.py <root> --check
python3 $S/audit_quiz.py <root>
python3 $S/check_bundle.py <root>
python3 $S/check_dump.py <root>
python3 $S/check_tricky.py <root>
python3 $S/check_findable.py <root>
python3 $S/reading_load.py <root>
```

Summarise: which gates failed, in which chapters, and the smallest fix for each. A gate marked GATE in the skill must pass before a lesson or quiz is delivered.
