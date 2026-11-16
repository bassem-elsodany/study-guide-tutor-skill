# Notices

`study-guide-tutor-skill` is released under the MIT licence (see `LICENSE`).

## Third-party content

None. The skill, references, scripts, agents, commands and the sample course under `tests/fixtures/` are original work.

## Methods the skill draws on

The ideas below are well-known learning-science findings, cited as ideas and not as copied text: retrieval practice (active recall), spaced repetition, interleaving, and worked-example teaching. See `skills/study-guide-tutor-skill/references/learning-science.md`.

## Optional tools the scripts can call (not bundled)

| Tool | Licence | Used by |
|---|---|---|
| `pdftotext` (poppler) | GPL-2.0-or-later | `source_text.py`, when installed |
| `mmdc` (Mermaid CLI) | MIT | `make_glance.py`, to validate diagrams, when installed |
| `pypdf` / `PyPDF2` / PyMuPDF | BSD / BSD / AGPL-3.0 | `source_text.py` fallback, when installed |

They are invoked as separate programs or optional imports and are not distributed with this repository.

## Study material you add

Slides, notes and books you study with belong to their owners. A generated course can contain their text in its fact ledger and cache: keep it private unless you have the right to share it.
