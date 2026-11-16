# Changelog

All notable changes to study-guide-tutor-skill. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow SemVer.

## [Unreleased]

**A Lesson tab in the player.** The study player now opens on the lesson: every chapter's `01-lesson.md` rendered as a page (tables, the "Tricky part" and open-and-close boxes, Mermaid diagrams drawn as pictures), with a chapter picker, an "on this page" list, an estimated reading time, an "I have read this chapter" box (shown in Progress), buttons to the quiz and flashcards of that chapter, and an "Open the Markdown file" link. The Markdown files stay the source and still read on their own; the player is a view built from them. Diagrams are drawn at build time with mermaid-cli when it is installed (cached, about a second for a whole domain) and shown as their Mermaid text otherwise. A sticky bar of section tabs follows the student down the page and marks the current section. Selecting lesson text offers **Highlight** and **Add note** (also H and N); highlights are painted back on every visit, listed under the lesson and in a new **Notes** tab, downloadable as Markdown, and included in the results file so the tutor can see where the student got stuck. New `--no-lessons` and `--no-diagrams` options, a small safe renderer (`scripts/_md.py`) with its own unit test, and new player strings in `templates/course.json`.

## [1.0.0] - 2026-11-17

First release. (Builds published earlier the same day under the same name were withdrawn; this is the one release.)

**What it is.** One skill, two helper agents and six slash commands that turn study material into a source-checked tutoring course, plus an interactive study player. Licensed under Apache-2.0, with a `NOTICE` file that credits this repository.

**The tutor**
- Intake first: nine multiple-choice questions become a learner profile that shapes every file; every file ends with one audience note.
- A fact ledger with a source location per fact; lessons written as a teacher would (a 5-minute at-a-glance block, Predict checks, 2 to 4 "Tricky part" hints, a closing "Traps to avoid"); audited quizzes (equal-length options, a reason for every wrong option); grading with memory anchors; flashcards; exams; spaced revisits.

**It adapts to what the student provides**
- Folder layouts follow the material: a flat course, or groups named with the source's own word (`module-1`, `week-03`, `part-1`, `domain-1` ...), nested if needed. Chapters and units are found by content, not by folder name.
- `source_text.py` reads pdf, pptx, docx, md, txt, html, epub, srt and vtt files, an image, or a folder of images, one numbered unit per slide, page, section or time segment.
- An optional `course.json` carries the language, the structural words the gates look for, the audience note's wording and the player's text; Arabic, Hebrew, Persian and Urdu flip the player to right-to-left. English is the default.

**The interactive player.** `make_player.py` builds one self-contained HTML file: a click-through quiz (instant feedback, why every wrong option is wrong, optional hints, retake of misses), flashcards in spaced boxes, a timed exam with results by chapter, progress, and a downloadable results file. No install, no network.

**Checks.** 17 standard-library Python scripts, eight of them gates (contents, quiz audit, bundle consistency, no slide dumps, tricky parts, findable answers, reading load, source cache). The repository validator also fails if the README misses a command, agent or skill.

**Examples and tests.** `examples/water-cycle/` holds a 10-slide PDF and the full course made from it. Five differently structured test courses (flat; by module; by week with lecture folders; nested term/week/session; Spanish by unidad), tests for every source reader and for the language mechanism, and CI that runs it all, including the player in headless Chrome.
