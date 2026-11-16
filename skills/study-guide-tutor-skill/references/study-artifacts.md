# Study Artifacts

Take-away formats the tutor produces on request, so work done in the session outlives the session. All are plain files the tutor writes itself (Markdown, CSV, JSON) and work in any viewer or import tool. Offer them at block boundaries or at wrap-up; never push them mid-block.

## 1. Concept map (heading-only outline)

A visual-ready summary of how the material fits together. Use it in two places:
- **Orientation (Phase 2):** a level-1/2 map of the proposed blocks, so the student sees the whole territory before committing to a path.
- **Wrap-up:** a regrouped map by theme (see memorization technique 5), including the student's weak branches.

Format (Markdown headings only, which any mind-map viewer can render):

```markdown
# Data Governance
## Roles and accountability
### Data owner vs. steward
#### Owner decides, steward executes
## Lifecycle controls
### Retention
#### Documents 10 years, logs 6 months
```

Rules:
- Headings only: no bullets, no numbering, no prose paragraphs.
- 3–8 words per heading; the heading is the idea, not a sentence.
- Max 4 levels. Level 1 = topic, level 2 = blocks/themes (the "collapsed" overview), level 3 = concepts, level 4 = the detail worth memorizing.
- One idea per node; siblings are the same kind of thing.
- Math in headings uses `$...$` inline or `$$...$$` block; escape a literal dollar sign as `\$`.
- Mark weak areas by appending a flag to the heading text only if the student wants the map to double as a revision map.
- Keep source locations out of headings; supply them in a separate table if the student wants them.

**Discuss-this-node drill.** The student names any node. Respond in this shape: explain it in the context of its parent and siblings (what larger idea it belongs to, what it is easily confused with), give its concrete example, then ask one active-recall question on it. This is how the map becomes interactive in a plain chat.

## 2. Flashcards

Cards for fast recall after the session. Principles:

- **One concept per card.** A card that needs two facts becomes two cards.
- **Front** is a concise question or prompt. **Back** is 1–3 sentences, or a list where every point sits on its own line (`•` bullets, or `1.` `2.` `3.` for steps and ordered processes).
- Prioritize what exams reward: key concepts, definitions, formulas and exact thresholds, step-by-step processes, compare-and-contrast pairs, and common exam questions with their answers.
- **Trap cards:** for each confusable pair, a card whose front names the pair and whose back states the one thing that separates them.
- **Number cards:** exact figures from the fact ledger, with units and the location.
- Set size: 20–50 cards. Larger material becomes several sets by block.
- Math uses LaTeX delimiters (`$...$`, `$$...$$`).

**Revisit deck.** The most valuable deck is built from the student's misses: one card per missed concept, front = the underlying question (not the original quiz stem), back = correct answer + the memory anchor from grading. This is the final pre-exam pass.

**CSV export** (imports into Anki, Quizlet, spreadsheets):

```csv
question,answer
"What separates a data owner from a data steward?","Owner decides policy and access; steward executes it day to day."
"List the retention periods.","• Documents: 10 years
• Logs: 6 months"
```

Quote every field, double any inner double quotes, keep embedded newlines inside quotes.

## 3. Standalone quiz file

When the student wants a re-takeable quiz beyond the live session, write it as JSON so any quiz tool can load it:

```json
{
  "title": "Data Governance, Blocks 1-3",
  "questions": [
    {
      "question": "A retailer's analyst can approve who sees customer records and also runs the daily access job. Which role split is violated?",
      "options": ["...", "...", "...", "..."],
      "correctIndex": 2,
      "hint": "Think about who decides versus who executes.",
      "correctExplanation": "Why the key is right, citing the material (Slide 44).",
      "wrongExplanation": "The trap: the adjacent concept most often confused with the key."
    }
  ]
}
```

Rules: exactly 4 options, `correctIndex` 0–3 (answer key randomized across the set), separate explanations for right and wrong answers, hint optional but recommended on Medium and Hard questions. Run the quiz audit pass (see `source-fidelity.md`) first. Standalone set length: 10–20 questions, mixed difficulty, one concept per question.

## 4. Orchestration and modes

| Student need | Order |
|---|---|
| Full study (default) | Ingest → structure (concept map) → per block: teach → quiz → grade → recall → wrap-up |
| Cram (short on time) | High-yield recap from the ledger (traps, numbers, comparisons) → flashcards → quiz → misses |
| Weak-area loop | Revisit list → fresh-variant questions on missed concepts only → regrade → repeat until a clean sweep |
| Orientation only | Concept map of the whole material → pick where to start |

For factual or number-heavy material, run the quiz audit pass first in every mode.

## 5. Next actions menu

End each major output (block teach, graded block, wrap-up, any artifact) with a single short line offering what logically follows, for example:

`Next: next block · active recall · concept map · flashcards of misses · re-quiz misses · cram mode`

Offer only the options that make sense at that point (e.g., "re-quiz misses" only after a graded block with misses). The student chooses; never auto-advance.

## 6. Folder layout for saved work

The tree mirrors the material, so folders and content always line up. The grouping level is optional: use the shape the material has, and never invent a level it does not have. A *unit* below means any folder that directly holds `chapter-*/` folders.

**Shape A: flat** (a book, one deck, a single course with no higher level)

```
<course>/
├─ learner-profile.md              from the intake analysis; read before generating anything
├─ README.md                       index: chapters, page ranges, status of each
├─ 00-overview/                    cross-chapter artifacts only (the unit is the whole course)
├─ chapter-01-<slug>/              one self-contained folder per chapter
└─ chapter-02-<slug>/ ...
```

**Shape B: grouped** (modules, weeks, parts, volumes, domains: the source's own word)

```
<course>/
├─ learner-profile.md
├─ <group>-1/                      for example module-1, week-01, part-1, domain-1
│  ├─ README.md
│  ├─ 00-overview/                 cross-chapter artifacts of this group only
│  ├─ chapter-01-<slug>/
│  └─ chapter-02-<slug>/ ...
└─ <group>-2/ ...                  chapter numbers restart in each group
```

Inside every unit:

```
00-overview/   README.md, 01-concept-map.md, 02-cram-sheet.md, 03-final-quiz.md (+ key), 05-score-tracker.md,
               06-revisit-list.md, 07-exam.md (+ 08-exam-key.md), 09-study-player.html
chapter-NN-<slug>/   01-lesson.md, 02-flashcards.csv, 03-quiz.md, 04-answer-key.md, 05-review.md (after grading), 99-fact-ledger.md
```

Rules: never group all quizzes, or all lessons, into one folder across chapters; keep keys out of quiz files; relative links only, so the tree can be moved; when chapters are merged, split or renamed, move files and fix links, the README and the tracker in the same pass; ask before creating any folder the student did not point at.

Every markdown file in the tree closes with ONE audience note from `intake-analysis.md` (written for whom, what that changed, how to ask for another level); there is no banner at the top. CSV files carry no banner.


## File order and diagrams (added in v0.4.0)
- Files are numbered in reading order: chapter folder `01-lesson.md` (the at-a-glance block with the Mermaid pictures first, then the explanation: ONE file), `02-flashcards.csv`, `03-quiz.md`, `04-answer-key.md`, `05-review.md`, `99-fact-ledger.md`; a unit's `00-overview/` `01-concept-map.md` to `09-study-player.html` (see SKILL.md).
- The concept map stays a heading-only outline; the at-a-glance block of the lesson holds the pictures. Every diagram is Mermaid and is validated with mermaid-cli by `scripts/make_glance.py`.
- The exam (`07-exam.md` and `08-exam-key.md`; older courses may use `07-unit-exam.md` or `07-domain-exam.md`, which every script still reads) covers every chapter of the unit; the final quiz is a short cumulative checkpoint.

## Overview guide and "Start here" (every course)

Students open a folder full of numbered files and do not know where to begin. Two small documents fix that; generate both with every course.

- **`00-overview/README.md`** (unnumbered, one per unit): a "short version" of five steps (practise, map, revise, test, read the trackers), then a table with one row per file in the folder: *what it is, use it when, contains answers?* Mark every key file as "only after you have answered". Add "which files you can leave alone" and a note that the quiz, key and flashcard files are the source of the player and must not be deleted. Counts (chapters, exam questions, suggested minutes) come from the actual files.
- **A "Start here" section** at the top of the course README and of every unit README: link the interactive player, give the per-chapter loop (read the lesson, practise in the player, retake misses, take the exam, send the results file), say where progress is stored (that browser only) and how to navigate (the chapters table, the contents at the top of every file, reading-order numbers).

Keep both in step with the folder: adding, renaming or removing a file means updating the table in the same pass.

## course.json: language and wording (optional)

A `course.json` at the course root adapts the generated files to the student's language without changing any script. Every key is optional and falls back to English, so a course without one behaves exactly as before. `templates/course.json` (in the plugin) lists every key with its English default.

| Key | Holds | Read by |
|---|---|---|
| `language` | a BCP-47 code (`es`, `fr`, `ar` ...); right-to-left languages (`ar`, `he`, `fa`, `ur` ...) flip the player's direction | `make_player.py` (page `lang` and `dir`) |
| `labels` | the structural words: the hint, rule and anchor words, the trap, say-it-back and next headings, Predict and analogy markers, difficulty words, the contents heading, the exam wording, the footer words, and a letter-reference regex for the course language | `check_tricky.py`, `check_dump.py`, `check_findable.py`, `audit_quiz.py`, `check_bundle.py`, `add_toc.py`, `make_exam.py`, `make_player.py`, `apply_banner.py` |
| `footer_checks` | the per-file-type sentence of the audience note, keyed like `references/banner-texts.json` | `apply_banner.py` |
| `ui` | every string of the interactive player | `make_player.py` |

Question headers keep the letter `Q` (`**Q1 (Media).**`) and options keep `A.` to `D.` in every language: those are format markers, not words. The profile line is read through the `audience_statement` label.
