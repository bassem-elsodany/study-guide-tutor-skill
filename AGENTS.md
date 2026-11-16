# study-guide-tutor-skill: operating manual for coding agents

> One skill, two agents, six slash commands, seventeen scripts, a shared layout helper and an interactive study player. There is no router and there are no hooks: the skill is loaded when a user asks to study, learn, be quizzed or prepare for an exam.

## 1. When to load the skill

Load `skills/study-guide-tutor-skill/SKILL.md` when the user shares study material (slides, lecture notes, a PDF, textbook chapters, course content) or says: study this, teach me, go through these slides, quiz me, test me, prepare me for the exam, make flashcards, mind map this, cram mode, quiz me on what I missed, is this accurate to my slides.

## 2. Rules that never bend

| Rule | Why |
|---|---|
| **Intake before generating.** Ask the multiple-choice questions in `references/intake-analysis.md` first (skip if `learner-profile.md` exists and still holds). | The explanation layer adapts to the learner; facts never do. |
| **Read all of the material before teaching.** Extract once (`source_text.py`), build the fact ledger, then work from the cache. | A quiz written without the whole source contradicts it. |
| **Material-only by default.** Everything taught and keyed traces to the source. Your own links and analogies are labelled ("my analogy", "Outside the material"). | The exam tests the course's version. |
| **Teach, do not dump.** A lesson that re-words the slides fails `check_dump.py`. | The student can read the slides faster. |
| **Warn where students get confused.** 2-4 "Tricky part" callouts per lesson, and a closing "Traps to avoid" section. | `check_tricky.py` enforces it. |
| **Audit every quiz.** Four options, one correct, all equally long and plausible, key position randomised, every key traced to the ledger. | `audit_quiz.py` and `check_findable.py` enforce it. |
| **Folders mirror the material.** One folder per chapter, grouped only if the source is (flat course, or one group folder per module, week, part or domain, named with the source's own word); never invent a level; confirm the tree once. | Students navigate by the source's own structure. |
| **Adapt to the student's assets.** Look at the material first: its type, size, grouping, numbering unit and language. Read it with `source_text.py`, shape the folders from it (flat or grouped, never a level it lacks), cite its own units, and write in the student's language with a `course.json`. Nothing in your output may assume slides, English or `domain-N`. | The scripts discover chapters and units by content and read labels from `course.json`. |
| **Fix the method, not only the instance.** When the student says "too dense" or "too easy", change the profile and regenerate the affected files. | Re-profiling is part of the loop. |

## 3. The order of work

```
intake → learner-profile.md → extract + fact ledger → propose chapters → per chapter:
lesson (teacher-writer) → quiz + key → grade → review → recall check
→ exam → student-reviewer + fidelity review → wrap-up
```

After any generation or edit run, in order: `make_exam.py` (if quizzes changed) → `apply_banner.py` → `add_toc.py` → `audit_quiz.py` → `check_bundle.py` → `check_dump.py` → `check_tricky.py` → `check_findable.py` → `reading_load.py` → `make_player.py` (the interactive page, last, so it shows the final questions). Details: `skills/study-guide-tutor-skill/references/lifecycle.md`.

## 4. Where things are

| Path | Contents |
|---|---|
| `skills/study-guide-tutor-skill/SKILL.md` | the decision guide (under 500 lines) |
| `skills/study-guide-tutor-skill/references/` | depth, loaded on demand: intake, question design, source fidelity, teaching design, grading files, learning science, lifecycle, artifacts |
| `skills/study-guide-tutor-skill/scripts/` | the gates and builders (Python standard library only) |
| `skills/study-guide-tutor-skill/scripts/_notes.py` | the format of the student's notes file, `06-notes.md` (the player has the same two functions in JavaScript; a test compares them) |
| `skills/study-guide-tutor-skill/scripts/_md.py` | the small safe Markdown-to-HTML renderer behind the player's Lesson tab |
| `skills/study-guide-tutor-skill/assets/player.html` | the template of the interactive study player (filled by `make_player.py`) |
| `agents/` | `teacher-writer` (one chapter lesson), `student-reviewer` (plays the learner) |
| `commands/` | `/study`, `/study-quiz`, `/study-player`, `/study-cram`, `/study-weak`, `/study-check` |
| `templates/` | a learner-profile template and a course-layout example |
| `tests/` | a tiny sample course the gates run against in CI |

Skill text writes script paths as `${CLAUDE_SKILL_DIR}/scripts/...`; outside Claude Code read `${CLAUDE_SKILL_DIR}` as `skills/study-guide-tutor-skill` and `${CLAUDE_PLUGIN_ROOT}` as the repository root.

## 5. Working on this repository

- English only; tables over prose; one idea per file; no personal data, no absolute paths, no machine names (the validator checks).
- Scripts use only the Python standard library, work on macOS and Linux, and never write outside the folder they are pointed at.
- Run `scripts/quality-check.sh` and `python3 -I scripts/validate-plugin.py .` before a pull request; update `CHANGELOG.md` and `VERSION` for user-visible changes.
- No `CLAUDE.md` at the repository root (it is not loaded for a plugin); this file is imported by `.claude/CLAUDE.md`.
