# Changelog

All notable changes to study-guide-tutor. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow SemVer.

## [1.0.1] - 2026-11-16

- The plugin and marketplace are now named `study-guide-tutor-skill`, the same as the repository, so every install command uses one name: `/plugin marketplace add bassem-elsodany/study-guide-tutor-skill` then `/plugin install study-guide-tutor-skill@study-guide-tutor-skill`. Slash commands are now `/study-guide-tutor-skill:study`, and so on. The skill folder keeps its name, `study-guide-tutor`.
- The repository validator now checks that the plugin, the marketplace and its plugin entry share one name and one version.

## [1.0.0] - 2026-11-16

First public release.

- One skill (`study-guide-tutor`) with 12 reference files covering intake, ingestion, fact ledgers, teaching design, question design, grading, spaced revisits and domain exams.
- Two agents: `teacher-writer` (one chapter lesson) and `student-reviewer` (plays the learner), and six slash commands: `/study`, `/study-quiz`, `/study-player`, `/study-cram`, `/study-weak`, `/study-check`.
- An interactive study player (`make_player.py`): one self-contained HTML file with a click-through quiz (instant feedback, why every wrong option is wrong, optional hints, retake of misses), flashcards in spaced boxes, a timed exam with results by chapter, progress, and a downloadable results file; checked by a scripted browser self-test (`scripts/test-player.sh`).
- 17 scripts (Python standard library only), eight of them gates or checks: quiz audit, bundle consistency, no slide dumps, tricky-part callouts, quiz answers findable in the lesson, reading load, table of contents, audience footer note.
- Lessons carry 2-4 "Tricky part" callouts (confusion, hint, collapsed rule and anchor) and close with a "Traps to avoid" section; every generated file ends with one combined audience note.
- A sample course under `tests/fixtures/` that the gates run against in CI.
