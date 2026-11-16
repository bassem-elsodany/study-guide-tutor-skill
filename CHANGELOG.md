# Changelog

All notable changes to study-guide-tutor. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow SemVer.

## [1.1.0] - 2026-11-17

- **The output layout no longer assumes domains.** A course can be flat (`chapter-NN-slug/` at the course root, one `00-overview/`) or grouped under any folder name the material uses (`module-1`, `week-03`, `part-1`, `domain-1` ...). A *unit* is any folder that directly holds `chapter-*/` folders, and every script finds units on its own through a shared helper (`scripts/_layout.py`). Phase 2 of the skill now decides the shape from the material and asks you to confirm the tree once.
- The exam files are `07-exam.md` and `08-exam-key.md`; the builder is `make_exam.py`. Courses made earlier (`07-domain-exam.md`, `make_domain_exam.py`, `domain-N` folders) keep working: every script reads the older names.
- `apply_banner.py` now re-points the footer's profile link on every run, because the link goes stale when files move.
- **Source readers.** `source_text.py` now reads pdf, pptx, docx, md, txt, html, epub, srt and vtt files, an image, or a folder of images, one numbered unit per slide, page, section or time segment, and records the unit word (slide, page, section, segment). Cache manifests written by earlier versions still work.
- **Chapters are found by content, not by folder name** (`chapter-03-x`, `lecture-3-x`, `capitulo-01-x` all work), and `build_chapter.py` takes `--source`, `--unit-word` and `--block-word`.
- **Language.** An optional `course.json` carries `language`, `labels` (the structural words the gates look for), `footer_checks` and `ui` (the player's text). The tricky-parts, dump, findable, quiz-audit and bundle gates, the exam builder, the contents builder, the audience note and the player all read it; Arabic, Hebrew, Persian and Urdu flip the player to right-to-left. English is the default, so existing courses are unchanged. `templates/course.json` lists every key.
- The sample course is now three fixtures (flat, module-grouped, Spanish), each with its gates run in CI, plus tests for every source reader, for the label mechanism and for right-to-left direction.

## [1.0.1] - 2026-11-16

- The plugin and marketplace are now named `study-guide-tutor-skill`, the same as the repository, so every install command uses one name: `/plugin marketplace add bassem-elsodany/study-guide-tutor-skill` then `/plugin install study-guide-tutor-skill@study-guide-tutor-skill`. Slash commands are now `/study-guide-tutor-skill:study`, and so on. The skill folder keeps its name, `study-guide-tutor`.
- The repository validator now checks that the plugin, the marketplace and its plugin entry share one name and one version.

## [1.0.0] - 2026-11-16

First public release.

- One skill (`study-guide-tutor`) with 12 reference files covering intake, ingestion, fact ledgers, teaching design, question design, grading, spaced revisits and exams.
- Two agents: `teacher-writer` (one chapter lesson) and `student-reviewer` (plays the learner), and six slash commands: `/study`, `/study-quiz`, `/study-player`, `/study-cram`, `/study-weak`, `/study-check`.
- An interactive study player (`make_player.py`): one self-contained HTML file with a click-through quiz (instant feedback, why every wrong option is wrong, optional hints, retake of misses), flashcards in spaced boxes, a timed exam with results by chapter, progress, and a downloadable results file; checked by a scripted browser self-test (`scripts/test-player.sh`).
- 17 scripts (Python standard library only), eight of them gates or checks: quiz audit, bundle consistency, no slide dumps, tricky-part callouts, quiz answers findable in the lesson, reading load, table of contents, audience footer note.
- Lessons carry 2-4 "Tricky part" callouts (confusion, hint, collapsed rule and anchor) and close with a "Traps to avoid" section; every generated file ends with one combined audience note.
- A sample course under `tests/fixtures/` that the gates run against in CI.
