# Student-persona review and reading budget

The whole point of the bundle is that the learner gains knowledge and understanding **fast**, without reading a lot. Measure it; do not assume it.

## Reading budget (enforced by `scripts/reading_load.py`)
- the at-a-glance block of `01-lesson.md`: about **4 minutes** to read (pictures, key facts, look-alikes, words).
- `01-lesson.md`: at most **12 minutes**, and never more words than reading the slides of that chapter would take. A lesson that is slower than its source has failed.
- Lessons use tables, short sentences and diagrams; one example per concept; no restating slides word for word; no filler sections ("How to read this chapter" stays to two sentences).
- Run `reading_load.py ROOT` after generating. Fix every flag by cutting, not by adding.

## The student reviewer
- Template: `agents/student-reviewer.md`. Spawn one read-only general-purpose agent per unit (3 chapters each: the longest, one list-heavy, one process-heavy) before calling a unit done.
- It plays the learner from the profile: reads only the at-a-glance block and answers 5 quiz questions (**summary-only score**), skims the lesson for cuts, checks every diagram at a glance, compares with reading the slides, and scores speed, clarity, visuals, padding and exam readiness 1-5.
- **Pass bar:** summary-only score at least 3 of 5 on average, no chapter below 2; every "speed" and "no padding" score at least 4; no diagram marked unreadable.
- Apply the cuts it lists (largest time saving first), regenerate the at-a-glance block (`make_glance.py`) if the lesson changed, re-run `apply_banner.py`, `add_toc.py`, `audit_quiz.py`, `check_bundle.py` and `reading_load.py`, and re-run the reviewer on any chapter that failed.
- This review is separate from the fidelity review (`fidelity-review.md`): fidelity asks "is it true to the source", the student review asks "is it fast to learn".
