# Tests

| What | How | Needs |
|---|---|---|
| Repository conventions (frontmatter, manifests, versions, links, no personal data or absolute paths) | `python3 -I scripts/validate-plugin.py .` (and `--self-test` proves its checks still fire) | Python 3 |
| Every script compiles and answers `--help`; every gate passes on the sample course | `scripts/quality-check.sh` | Python 3, bash |
| The interactive study player: builds it from the sample course with a scripted click-through appended and runs it in headless Chrome or Chromium (skips if none is installed) | `scripts/test-player.sh` | Chrome or Chromium |
| The installer for other agents (link, copy, uninstall) | the `installer` step in `.github/workflows/ci.yml` | bash |

## The sample course

`fixtures/sample-course/` is a one-chapter course about the water cycle, written for the tests and invented from scratch (no third-party text). It follows the layout the skill generates (`domain-1/chapter-01-the-water-cycle/` with lesson, flashcards, quiz, key and fact ledger) and passes every gate: table of contents, quiz audit, bundle consistency, no slide dumps, tricky parts, findable answers.

To see a gate fail, break the fixture in a scratch copy: delete a `Hint:` line from a Tricky-part callout, or lengthen the correct option of a quiz question by 20 characters, and run the matching gate on the copy, for example `python3 skills/study-guide-tutor/scripts/check_tricky.py <copy>` or `.../audit_quiz.py <copy>`.

What is **not** covered: the quality of lessons an agent writes (that is what the `student-reviewer` agent and the fidelity review are for), other source formats than the sample, and other agents than Claude Code.
