# Tests

| What | How | Needs |
|---|---|---|
| Repository conventions (frontmatter, manifests, versions, links, no personal data or absolute paths) | `python3 -I scripts/validate-plugin.py .` (and `--self-test` proves its checks still fire) | Python 3 |
| Every script compiles and answers `--help`; every gate passes on the sample course | `scripts/quality-check.sh` | Python 3, bash |
| The interactive study player: builds it from the sample course with a scripted click-through appended and runs it in headless Chrome or Chromium (skips if none is installed) | `scripts/test-player.sh` | Chrome or Chromium |
| Every source reader (pdf, pptx, docx, md, txt, html, epub, srt, vtt, images, folder of images), changed-source detection and old manifests | `python3 -I tests/test-sources.py` (run by `quality-check.sh`; the PDF check is skipped without an extractor) | Python 3 |
| `course.json`: defaults, overrides, language and direction, the letter-reference pattern, and that the gates really read the labels | `python3 -I tests/test-labels.py` | Python 3 |
| The installer for other agents (link, copy, uninstall) | the `installer` step in `.github/workflows/ci.yml` | bash |

## The sample course

Three small courses invented from scratch for the tests (no third-party text), both about the water cycle:

| Fixture | Shape | What it proves |
|---|---|---|
| `fixtures/sample-spanish-course/` | flat, in **Spanish**, with a `course.json` (language, labels, footer wording, player text) | every gate and the player work with another language's markers; the same course fails the gates without its `course.json` |
| `fixtures/sample-course/` | **flat**: `chapter-01-the-water-cycle/` and `00-overview/` (with an exam) at the course root, no grouping folder | a course with no units works with every script, and the exam path of the player is covered |
| `fixtures/sample-grouped-course/` | **grouped**: `module-1/` and `module-2/`, each with its own chapter (module-1 also has an exam) | any group name works (not just `domain-N`), each group is its own unit |

Both follow the layout the skill generates and pass every gate: table of contents, quiz audit, bundle consistency, no slide dumps, tricky parts, findable answers.

To see a gate fail, break the fixture in a scratch copy: delete a `Hint:` line from a Tricky-part callout, or lengthen the correct option of a quiz question by 20 characters, and run the matching gate on the copy, for example `python3 skills/study-guide-tutor/scripts/check_tricky.py <copy>` or `.../audit_quiz.py <copy>`.

What is **not** covered: the quality of lessons an agent writes (that is what the `student-reviewer` agent and the fidelity review are for), other source formats than the sample, and other agents than Claude Code.
