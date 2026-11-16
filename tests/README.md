# Tests

| What | How | Needs |
|---|---|---|
| Repository conventions (frontmatter, manifests, versions, links, no personal data or absolute paths) | `python3 -I scripts/validate-plugin.py .` (and `--self-test` proves its checks still fire) | Python 3 |
| Every script compiles and answers `--help`; every gate passes on every example and fixture course | `scripts/quality-check.sh` | Python 3, bash |
| The player reads a course whatever order its files were built in, and the example's counts | `python3 -I tests/test-player-data.py` (run by `quality-check.sh`) | Python 3 |
| The interactive study player: builds it for one unit of every course with a scripted click-through appended and runs it in headless Chrome or Chromium (skips if none is installed) | `scripts/test-player.sh` | Chrome or Chromium |
| Every source reader (pdf, pptx, docx, md, txt, html, epub, srt, vtt, images, folder of images), changed-source detection and old manifests | `python3 -I tests/test-sources.py` (run by `quality-check.sh`; the PDF check is skipped without an extractor) | Python 3 |
| `course.json`: defaults, overrides, language and direction, the letter-reference pattern, and that the gates really read the labels | `python3 -I tests/test-labels.py` | Python 3 |
| The installer for other agents (link, copy, uninstall) | the `installer` step in `.github/workflows/ci.yml` | bash |

## The example and the fixture courses

Five small courses, all invented from scratch (no third-party text), all about the water cycle. The two chapters ("The four stages", "Where the water goes") are the same in every course, but the **folder structures differ on purpose**, because the skill adapts to the material it is given:

| Course | Structure | What it proves |
|---|---|---|
| `examples/water-cycle/course/` | **flat**: `chapter-01-…`, `chapter-02-…` and one `00-overview/` at the course root; also keeps the source `assets/water-cycle.pdf` with its text cache | a course with no groups; the showcase used by the README; the exam and the player work from the course root |
| `tests/fixtures/by-module/` | **grouped by module**: `module-1/chapter-01-…`, `module-2/chapter-01-…` | each group is its own unit with chapter numbers restarting |
| `tests/fixtures/by-week-and-lecture/` | **grouped by week**, with **lecture** folders: `week-01/lecture-01-…` | any group word and any block word, with "Lecture 1" titles |
| `tests/fixtures/nested-terms/` | **nested**: `term-1/week-01/session-1-…` | two grouping levels, "Session" blocks |
| `tests/fixtures/spanish-course/` | **grouped by unidad**, in **Spanish**, with a `course.json` (language, labels, footer wording, player text) | every gate and the player work with another language's markers; the same course fails the gates without its `course.json` |

Every course passes every gate (table of contents, quiz audit, bundle consistency, no slide dumps, tricky parts, findable answers). `scripts/quality-check.sh` also asserts, for each course, exactly which units and chapter folders discovery finds.

To see a gate fail, break a scratch copy of one course: delete a `Hint:` line from a Tricky-part callout, or lengthen the correct option of a quiz question by 20 characters, and run the matching gate on the copy, for example `python3 skills/study-guide-tutor-skill/scripts/check_tricky.py <copy>`.

What is **not** covered: the quality of lessons an agent writes (that is what the `student-reviewer` agent and the fidelity review are for), other agents than Claude Code, and the PDF reader without `pdftotext` or `pypdf`.
