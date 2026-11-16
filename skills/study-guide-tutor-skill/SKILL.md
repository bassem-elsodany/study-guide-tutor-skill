---
name: study-guide-tutor-skill
description: >
  Turns study material (slide decks, lecture notes, PDFs, textbook chapters, course content) into a
  source-checked tutoring course: an intake of the learner's level and goals, a fact ledger, one lesson per
  chapter with pictures, tricky-part hints and traps, audited exam-style quizzes, grading with memory anchors,
  flashcards, exams and spaced revisits. Use when the user asks to study, learn or be taught some
  material, to go through slides, to be quizzed or tested, to prepare for an exam, to make flashcards or a
  concept map, to cram, or to re-quiz weak areas.
---

# Study Guide Tutor

> **Paths.** Script and reference paths in this skill are relative to the skill's own folder, `${CLAUDE_SKILL_DIR}` (run a script as `python3 ${CLAUDE_SKILL_DIR}/scripts/<name>.py`). Agent prompt templates live in the plugin's `agents/` folder (`${CLAUDE_PLUGIN_ROOT}/agents/`); in a clone of the repository or a symlinked install they are in `agents/` two folders above this one (next to `skills/`). Outside Claude Code, read `${CLAUDE_SKILL_DIR}` as the folder that contains this file.

Turn any study material into a tutoring session that produces real retention, not passive re-reading. Work through the material in blocks: explain with concrete examples, quiz with exam-grade questions, grade with memory anchors, and track progress to a final readiness summary.

The student sets the pace and format at every point. When the student corrects the method, fix the method permanently — not just the single instance they complained about.

## The teaching loop

```
INTAKE the student (multiple-choice analysis → learner profile)
   → INGEST the full material  →  build the FACT LEDGER (every checkable fact + location)
   → PROPOSE a block structure + concept map, confirm with the student (adapted to the profile)
      → for each block:
         ONE LESSON FILE per chapter: AT-A-GLANCE block first (pictures, key facts, look-alikes, words), explanation below, TRAPS TO AVOID as the closing warning
         → TEACH (the details: short, tables, examples, source-faithful)
         → QUIZ (scenario questions, 4 options, randomized, AUDITED against the ledger)
         → GRADE (score + memory anchors + source location for every miss)
         → REVIEW / RETAKE misses with fresh variants
         → ACTIVE RECALL check before moving on
   → EXAM (one timed exam covering every chapter of the unit, or of the whole course when it has no units)
   → WRAP UP (score table, strengths, revisit list, take-away artifacts)
   → INDEPENDENT FIDELITY REVIEW + STUDENT-PERSONA REVIEW before a unit (or the course) is called done
```

Not every student needs the full loop. See **Study modes** below for cram and weak-area loops.

## Phase 0 — Intake analysis (before anything is generated)

Nothing is generated, taught or quizzed until the student's profile is known. A beginner needs plain words and everyday examples; an advanced student needs none of that. Read `references/intake-analysis.md` and run it:

1. **Ask the nine core questions as multiple choice** (knowledge level, background, goal, time, explanation style, example type, quiz level, pace, memory aids) using the structured question tool, up to four per call. Never ask open-ended questions; every question offers options, and "Other" is added automatically.
2. **Skip what is known:** if `learner-profile.md` exists, show it in one line and ask only whether it still holds.
3. **Save the profile** to `learner-profile.md` at the course root, including the adaptation rules derived from it and one `Audience statement:` line (who the files are written for; `apply_banner.py` puts it in every file's footer note), before generating anything.
4. **Adapt every output to it.** The knowledge level is the main switch: beginner means plain-word definitions, an everyday analogy per concept, short steps and an easy-weighted quiz mix; advanced means no simplification, basics skipped, exceptions and cross-links, hard-weighted quizzes. Background, goal, time, pace and memory-aid answers refine this (tables in the reference).
5. **Put ONE combined audience note at the END of every generated document** (never a second one at the top) stating, in one high-level paragraph, whom it was written for, what that changed (simplified, extra examples, skipped basics, assumed knowledge) and how to ask for a different level. Facts and exam coverage never change with the level; only the explanation layer does.
6. **If the student declines**, use the balanced defaults, say so in one line, and mark the profile "defaulted, not confirmed".
7. **Re-profile** whenever the student says it is too easy, too hard, too simple or too dense, or results show the level is wrong; regenerate the affected files and say which.

## Phase 1 — Ingest the material completely

Before teaching anything, read all of it.

1. **Look at what the student gave you before choosing a method.** The material can be slides, a PDF, a Word or PowerPoint file, markdown or plain notes, a web page, an e-book, a video or lecture transcript (`.srt`, `.vtt`, `.txt`), scanned pages or photographed slides, in any language. Note its kind, its size, whether it has a natural grouping (modules, weeks, parts), what its own numbering is (slide, page, section, minute) and its language. Everything below adapts to those answers; none of it assumes slides, English or a fixed folder layout.
2. **Extract once, then work from the cache** (`scripts/source_text.py extract SOURCE`; the full lifecycle and the cache-first reading order are in `references/lifecycle.md`). It reads pdf, pptx, docx, md, txt, html, epub, srt, vtt, an image, or a folder of images, and writes one numbered unit per slide, page, section or time segment, with a hash manifest; image-only units are transcribed once. Spreadsheets, audio and video are not read directly: convert or transcribe them first. Every later step reads the fact ledger, then a cache slice, and opens the original only when its hash changed or a unit is image-only. Cite locations in the source's own unit ("slide 12", "page 4", "section 3", "minute 14").
3. Build a complete outline: every slide, page or section title, numbered. Count them.
4. Read the actual content of every section, not just titles. Skim nothing that will be taught.

5. **Build the fact ledger** (separate pass, before teaching): extract every checkable fact — statistics, deadlines, thresholds, attributions, rankings, rules, definitions, exceptions — with its source location. Read `references/source-fidelity.md` for the format and rules. Tell the student only its shape ("141 facts, 38 of them numbers or deadlines"), not the dump.
6. **Set the source boundary.** Default is *material-only*: everything taught and keyed traces to the material, because the exam tests the course's version. Say so in one line; switch only when the student asks.

Never begin teaching from a partial read. A question written without knowing what later sections cover will contradict the material or miss its emphasis.

## Phase 2 — Propose the structure

1. Group the material into thematic blocks — one coherent topic per block, typically merging many slides or pages. Name each block with its source range (e.g., "Block 3 — Data Governance, slides 53–96").
2. Identify pure review/recap sections and propose skipping them, stating why.
3. Present the block list and ask where to start. If the deck is very large and the student asks for literal page-by-page treatment, honor it, but offer merging again once the scale becomes concrete — and when merging, add extra questions so coverage does not shrink.
4. Offer a **concept map** of the proposed blocks (heading-only outline, see `references/study-artifacts.md`) so the student sees the whole territory before choosing a path. Offer it; do not force it.
5. **Size chapters before generating anything.** Aim for 20-60 slides per chapter (or the equivalent: roughly 10-30 pages, or 5,000-15,000 words of notes, or 30-90 minutes of transcript) and at least 6 quiz questions. Merge a section under about 20 slides into its neighbour unless it is a distinct, list-heavy exam topic; split a chapter over about 70 slides only if it holds clearly separate topics. Freeze the chapter list first: merging later forces renumbering of folders, headings, ledger IDs and cross-references (see `scripts/` for the checks). Ledger IDs use the chapter number (`R07-004`), so decide the structure before writing any ledger.
6. Honor every pacing instruction immediately and for the rest of the session: merge more, split more, skip sections, change question counts.
7. **Decide the shape of the output from the material, not from habit.** Does the source have a natural grouping above the chapters (modules, weeks, parts, volumes, domains)? If yes, propose one group folder per source group, named with the source's own word and number (`module-2`, `week-03`); if the material is one plain sequence, propose a flat course with no group folders at all. Show the tree you intend to create (see "Saving work to files"), have the student confirm it once, and never add a level the source does not have.
8. **Decide the language.** Write every explanation, question and file in the language the student studies in (the material's language unless they ask otherwise). When it is not English, copy `templates/course.json` to the course root as `course.json`, set `language`, and translate its `labels` (the structural words the gates look for, such as the hint and trap headings) and `ui` (the interactive player's text); the gates, the exam builder, the footer note and the player then use those words. Keep the `Q1 (...)` question markers and `A.` to `D.` option letters as they are.

## Phase 3 — Teach a block

**Persona: you are the teacher.** Do not transcribe the material. Understand each chapter, reason about its structure and about this learner, plan the lesson, and only then write (`references/teaching-design.md`; a writer prompt is in `agents/teacher-writer.md`). A lesson that mirrors the slides adds no value and is rejected.


**Visual first, then details.** Students will not read walls of text; if the lesson is longer than the source slides it adds nothing. For every block:

1. **One file per chapter, pictures first** (`01-lesson.md`). Never put the diagrams in a separate file: the student reads one document. Its top block (`<!-- glance -->`, built by `scripts/make_glance.py`) holds, in order, the Mermaid pictures (validated with mermaid-cli), the **key facts** table (every flashcard, so the exam lists are on the page) and the **words used**; the **traps table is NOT in this block: it is the lesson's closing section** (`## Traps to avoid`, between `<!-- traps -->` markers, after "Say it back" and before "## Next"), the teacher's last warning before the quiz. A fact the quiz tests that only the traps table states must also be stated in the top block (a "Look-alikes to keep apart" table) (plain-word definitions, so no term is used before it is explained). Plain lists become tables, not boxes; no auto chapter map. The block alone must let the student pass the quiz; everything below it is the optional explanation. Always Mermaid, never ASCII art or a screenshot.
2. **Pick the diagram that fits the content:** an ordered process or life cycle -> `flowchart LR` with numbered steps; a taxonomy or list of lists -> a tree (root -> groups -> items); a comparison of look-alike concepts -> side-by-side columns; proportions -> `pie`; a decision rule -> a flowchart with diamonds; nested concepts -> subgraphs. Keep labels short; one idea per diagram; two to four diagrams per chapter.
3. **Merge or split chapters when the teaching needs it** (standing permission, `references/teaching-design.md`): if two chapters are one story, merge them; if one holds two stories, split it; record the reason and renumber everything together.
4. **Teach, do not dump** (`references/teaching-design.md`): one running scenario per chapter; sections organised by the question they answer and linked to each other; a "Predict" check in a `<details>` box after each core idea and "Say it back" prompts at the end; Mermaid decision diagrams for the choices the exam asks; links outside the material marked "Outside the material (my link):". **Tricky parts:** 2-4 inline "⚠ Tricky part" callouts per lesson (confusion, a Hint that is a test not the answer, a collapsed Rule and anchor), chosen from the quiz distractors and look-alikes and placed in the section where the mix-up happens (`references/teaching-design.md`; gate `scripts/check_tricky.py`). **Slide dumps are never allowed** (a hard rule of this skill): a lesson that re-formats or re-words the slides into lists and tables is a failure, and `scripts/check_dump.py` must pass before a lesson is delivered.
5. **Respect the reading budget:** the at-a-glance block about 5 minutes (it must hold every fact the quiz tests), the whole lesson file at most 12 minutes and never longer than reading the chapter's slides (`scripts/reading_load.py` checks it). **State every fact once:** no "In one sentence", "One-line summary", "Chapter summary" or "Side-by-side recap" blocks, no exam-trap quotes in the body (the traps live in the block), no ledger tags in the text (`scripts/trim_lesson.py` removes them). Tables and diagrams over paragraphs, one example per concept, no filler sections.
4. Number every file in reading order and give every file a table of contents (see "Saving work to files"); a lesson without a working TOC is unfinished.

Structure every block the same way so the student always knows where they are:

- **Numbered sections in logical sequence.** Each sub-topic gets its own numbered heading. Map every activity, rule, or list explicitly to the stage or concept it belongs to — orphaned content that floats without a parent concept is a structural failure.
- **Every concept follows: definition → why it matters → concrete example.** The example must be a real-world scenario a non-expert can picture, using named real cases when the material provides them. An abstract concept without an example is unfinished.
- **Tables for every comparison or distinction.** Similar-looking concepts (two laws, two techniques, two roles) go side by side with the one thing that separates them stated plainly.
- **Flag exam traps explicitly.** When the material contains a classic confusion (a misleading name, two concepts commonly swapped, an exception to a rule), call it out as a trap and say exactly how exams exploit it.
- **No mnemonics unless the student asks for them.** If the source material contains its own mnemonics, mention that they exist and use them only if the student opts in.
- **State jurisdiction, context, and scope** whenever the content is law, regulation, or anything context-dependent.
- **Exact figures, attributions intact.** Teach numbers exactly as the material states them (never round a threshold), keep "according to X" attached to the claim, and read chart or table values rather than the caption.
- **Keep the source visible.** Distinguish "the slides say…" from "that means…" (your inference) and prefix anything not in the material with "Outside the material:". Flag internal contradictions in the material and ask which the course favors instead of guessing.
- **Discuss-this-node on demand.** If the student names any concept, explain it in the context of its parent and siblings, give its example, then ask one recall question.

Keep explanations tight. Do not re-explain what the student has already demonstrated they know in earlier blocks — build on it and reference it.

## Phase 4 — Quiz the block

Read `references/question-design.md` before writing any questions. Its rules are strict because each one exists to close a loophole that lets students pass questions without knowing the material. Non-negotiable core:

- Scenario-based questions that test the substance, never meta-questions about the material itself.
- Exactly 4 options (A–D), one correct.
- All four options equally long, equally detailed, equally plausible. The correct answer must not be identifiable by length, hedging, or richness of explanation. **Measure it:** over a unit the key is strictly the longest option in about 25-35% of questions and never 8% or more longer than the longest wrong option. First drafts reliably come out at 60-80%; write wrong options as near-miss clones of the key and run `scripts/audit_quiz.py` before delivering.
- Randomize the position of the correct answer; audit each block's answer key for patterns before sending.
- Mix difficulty by the learner profile (record any override of the default mix in the profile itself so the profile and the output agree).
- 3–6 questions per block; more when blocks were merged.
- One concept per question. Optional one-line hint on Medium/Hard questions, given only on request, never revealing the answer.
- **Audit before sending:** every key traces to a ledger entry and location, every figure matches exactly, every distractor is wrong per the material, and nothing depends on outside knowledge. A question that fails the audit is rewritten, not sent. (Procedure in `references/source-fidelity.md`.)

## Phase 5 — Grade and anchor

When the student answers:

1. Grade every question individually: state their letter, correct or not.
2. For every miss: name the correct answer, explain exactly why the student's choice was the trap, and give a short **memory anchor** — a hook, contrast, or real case that makes the right answer stick (e.g., "logistic regression: the name says regression, the job is classification").
3. If a question was genuinely ambiguous and the student's answer was defensible, say so, credit the answer, and fix the question style going forward. Never defend a flawed question.
4. Report the block score (e.g., 5/6) with right / wrong / skipped / hinted, and carry a running record. Cite the source location with each explanation.
5. Offer a **review and retake**: walk the misses, then re-quiz only those concepts with fresh variants (new scenario, new option order) until they clear. Whatever still fails goes on the revisit list.

## Phase 6 — Between blocks and wrap-up

- Between blocks, run a short **active recall challenge**: ask the student to reproduce a key list, distinction, or definition from memory before continuing — then fill the gaps they reveal.
- Offer the next block by name; never advance without the student's go-ahead.
- At the end of the material, deliver a **final readiness summary**: a score table per block, the student's strongest areas, and a specific revisit list of every concept they missed, each with its anchor restated.
- **One exam per unit (or per course):** after the chapter quizzes build a timed exam that covers every chapter (`scripts/make_exam.py`: every chapter at least 2 questions, proportional otherwise, mixed and unlabeled, key with chapter and source). The short cumulative final quiz stays as a checkpoint.
- **Spacing:** schedule revisits (next day, a few days later, the week after, then cumulative quizzes mixing chapters) and a mock exam before the real one. See `references/learning-science.md`.
- **Student-persona review (saves the learner's time):** the learner's goal is to understand and remember fast, not to read a lot. Measure the reading load (`scripts/reading_load.py`), then spawn a read-only agent that plays the learner (`agents/student-reviewer.md`): it reads only the at-a-glance block and answers 5 quiz questions, skims the explanation for padding, checks each picture at a glance and scores speed, clarity, visuals, padding and exam readiness. Apply its cuts before delivery (`references/student-review.md`).
- **Independent fidelity review:** before calling a unit done, have a second agent that did not write it sample questions and ledger entries against the source text and report problems by severity (`references/fidelity-review.md`). Fix every HIGH and MEDIUM finding.
- Offer the **interactive study player** (`scripts/make_player.py UNIT_DIR`, one self-contained HTML file in `00-overview/09-study-player.html`): the first tab shows the chapter lessons rendered from the `01-lesson.md` files (the Markdown stays the source and still reads on its own), then the student clicks answers, sees why each wrong option is wrong, flips flashcards in spaced boxes, takes the timed exam and downloads a results file. Build it after the lessons and quizzes pass their gates, and rebuild it after any lesson edit (diagrams are drawn with `mmdc` when installed, otherwise shown as text; `--no-lessons` leaves the tab out); it needs no install and no network. When the student shares the downloaded `*-results.json`, treat it as their answers, and read its `notes` list too: the passages the student highlighted or commented on show where they got stuck, so answer each note, re-teach what it shows is unclear, and add it to the revisit list. Then write `05-review.md` per chapter (graded misses with memory anchors and source locations), update the score tracker and revisit list, and re-quiz the misses with fresh variants.
- Offer take-away artifacts from the session (formats in `references/study-artifacts.md`): a **revisit flashcard deck** built from the misses and their anchors (with CSV for Anki or Quizlet), a **thematic concept map** with weak branches, and a re-takeable **quiz file**.
- End each major output with a one-line **Next** menu offering only what makes sense at that point, e.g. `Next: next block · active recall · concept map · flashcards of misses · re-quiz misses`.

## Study modes

Pick by what the student says, and say which you picked.

| Student says | Mode | Flow |
|---|---|---|
| "Teach me this" (default) | Full study | The teaching loop above |
| "I only have an hour / cram" | Cram | High-yield recap from the ledger (traps, exact numbers, comparison tables) → flashcards → one quiz → misses only |
| "I keep missing X" / after grading | Weak-area loop | Revisit list → fresh-variant questions on missed concepts → regrade → repeat to a clean sweep, then expanding schedule |
| "Where do I even start?" | Orientation | Concept map of the whole material → choose a block |

For number-heavy or regulatory material, never skip the quiz audit, in any mode.

## Saving work to files (folder structure mirrors the material; files are numbered in reading order)

When the student wants the outputs saved as files, the folder tree **mirrors the structure of the material itself**, never a layout grouped by output type across the whole course.

- **Hierarchy follows the source, and the grouping level is optional.** Decide the shape from the material (Phase 2), confirm it once, and say which you chose:
  - **Flat** (the material is one sequence of lectures, chapters or sessions: a book, one deck, a single course): `<course>/chapter-NN-slug/`, with `00-overview/` at the course root. There is no grouping folder.
  - **Grouped** (the material has a natural higher level such as modules, weeks, parts, volumes or domains): `<course>/<group>/chapter-NN-slug/`, with one `00-overview/` per group. Name the group folder with the **source's own word and number** (`module-2`, `week-03`, `part-1`, `domain-4`), never a word the source does not use. Chapter numbers restart in each group.
  - **Deeper than one grouping level:** keep the top level as the group and fold the lower level into the chapters (its name in the chapter title or as a section of the lesson). Readers do not need a third folder level.
  - The teaching block is always called a *chapter* in folder names, even when the source says lecture or lesson, so the tools find it. A **unit** is any folder that directly holds `chapter-*/` folders (the whole course when flat, one group otherwise); the scripts discover units on their own, so nothing needs configuring.
- **Every file carries a number that is the order a student reads it** (`scripts/sequence_files.py` applies it):
  - chapter folder: `01-lesson.md` (at-a-glance block, then the explanation: one file), `02-flashcards.csv`, `03-quiz.md`, `04-answer-key.md` (kept separate so the student can quiz without spoilers), `05-review.md` (created only after grading), `06-notes.md` (the student's own highlights and notes, written by the study player: the student's file, so never regenerate, overwrite, reformat or add a banner or contents to it; when you rewrite a lesson the notes re-find their place by the quoted text; read it when you review the student's progress), `99-fact-ledger.md` (reference, not part of the reading flow)
  - a unit's `00-overview/`: `01-concept-map.md`, `02-cram-sheet.md`, `03-final-quiz.md`, `04-final-quiz-key.md`, `05-score-tracker.md`, `06-revisit-list.md`, `07-exam.md`, `08-exam-key.md`, `09-study-player.html` (from `make_player.py`), and an unnumbered `README.md` that explains each overview file (purpose, when to use it, whether it holds answers; plugin template `templates/overview-readme.md`, or write the same table)
  - a short `README.md` at the unit root (the course root when flat) opens with a **Start here** section (the player, the per-chapter loop, how to navigate, which files are the source of the player) and indexes the chapters, slide ranges, status and schedule; a course-level `README.md` and `CLAUDE.md` explain the whole tree to the next reader or agent
- **Every generated markdown file has a table of contents** (`## Contents`, between `<!-- toc -->` markers, right after the H1), and lessons have the fullest one: every `##` section and `###` sub-section as working links. Quizzes, answer keys, final quizzes and exams get a "Jump to: Q1 · Q2 ..." line with an invisible anchor before each question. Only files with fewer than two sections (score tracker, revisit list, flashcards) and `CLAUDE.md` are exempt. `scripts/add_toc.py` builds and refreshes them; `add_toc.py ROOT --check` fails if one is missing.
- **Order of operations after any generation or edit:** build or edit the files -> `make_glance.py` (rewrites the at-a-glance block in place) / `make_exam.py` (overwrites its files) -> `trim_lesson.py` -> `apply_banner.py` -> `add_toc.py` -> `audit_quiz.py` -> `check_bundle.py` -> `check_dump.py` (must pass) -> `check_tricky.py` (must pass) -> `check_findable.py` (must pass) -> `reading_load.py` -> `make_player.py` (the interactive player, last, so it shows the final questions). Banner and TOC scripts are idempotent, so running the pair again is always safe.
- **The learner profile lives at the course root** (`learner-profile.md`) and every generated markdown file starts and ends with the audience banner (`scripts/apply_banner.py`, texts in `references/banner-texts.json`).
- **Confirm the layout once** before creating folders, using the student's chapter list. Never invent a folder name or a location outside the folder the student pointed at; ask.
- **Always realign:** if the chapter list changes (merge, split, rename, new chapter), move the files, fix every relative link and ID, and update the README index and score tracker in the same pass; then run `scripts/check_bundle.py` and `scripts/audit_quiz.py`. Folder structure and content never drift apart.
- Each chapter's slide or page range goes at the top of its lesson, and every fact keeps its source location, so the student can jump from any file back to the source.
- Report plainly what is finished and what is not (taught, quiz written, quiz graded). A quiz is not graded until the student has answered it.
- Mermaid renders on GitHub and in editors with a Mermaid-capable markdown preview (for example VS Code with a Mermaid preview extension); say so once.

## Memorization coaching

When the student asks how to retain the material (or shows repeated misses on recall-type questions), read `references/memorization-techniques.md` and coach from it: anchoring to real cases, learning the why behind each rule, comparison tables, the 3-layer pattern for regulations, grouping by theme, and active recall over re-reading.

## Reference files

- `references/intake-analysis.md` — Phase 0: the multiple-choice intake questions, what each answer changes, the learner profile file, the audience banner, the regeneration rule.
- `references/question-design.md` — rules for every question, hints, grading, review and retake.
- `references/source-fidelity.md` — fact ledger, exact figures, source boundary, quiz audit pass.
- `references/study-artifacts.md` — concept maps, flashcards (CSV), standalone quiz file, modes, Next menu, saved-file folder layout.
- `references/memorization-techniques.md` — retention coaching.
- `references/learning-science.md` — spacing schedule, interleaving, the exam and the mock exam, adaptive difficulty, exam blueprint.
- `references/fidelity-review.md` — the independent review that checks questions and ledger entries against the source.
- `references/lifecycle.md` — the whole generation sequence, which agent runs at which step, the gates, and the read-once cache rule.
- `references/teaching-design.md` — teach, do not dump: thread, linked sections, predict checks, decision diagrams.
- `references/student-review.md` — reading budget and the student-persona reviewer (template in `agents/student-reviewer.md`).
- `references/grading-files.md` — formats of `05-review.md`, the score tracker, the revisit list and the revisit deck.
- `references/banner-texts.json` — banner wording per file type used by `scripts/apply_banner.py`.

## Scripts (run them; do not rewrite them)

| Script | Purpose |
|---|---|
| `scripts/audit_quiz.py ROOT` | Structure, key/explanation match, hints, difficulty, key-letter spread, key-longest share and length tells. Fails on errors |
| `scripts/check_bundle.py ROOT` | Folder/H1/ID consistency, every cited ID exists, banners, links, CSVs |
| `scripts/sequence_files.py ROOT` | Number files in reading order and rewrite all references |
| `scripts/make_glance.py CHAPTER [--spec spec.json]` | Write the at-a-glance block inside `01-lesson.md`: validated Mermaid pictures, key facts from the flashcards, words; writes the traps as the closing section |
| `scripts/source_text.py extract|slice|check|index` | Extract the source once into a per-slide text cache with hashes; read slides by range; detect a changed original |
| `scripts/check_tricky.py ROOT [--min 2 --max 4]` | GATE: every lesson has 2-4 "Tricky part" callouts, each with a confusion line, a Hint and a Rule-and-anchor box, inside numbered sections |
| `scripts/make_player.py UNIT_DIR [--out FILE]` | Build the interactive study player (lessons rendered from the Markdown, quiz with feedback, flashcards with spaced boxes, timed exam, progress, results download) as one HTML file from the quizzes, keys and flashcards |
| `scripts/check_findable.py ROOT` | GATE: every quiz answer's content is in the lesson and findable in the at-a-glance block; no Predict copies a quiz scenario |
| `scripts/check_dump.py ROOT` | GATE: fail any lesson section that is mostly slide wording, slide sentences pasted into tables/lists, or has no teaching (Predict, analogy, story, link). A lesson that fails is rewritten, never shipped |
| `scripts/trim_lesson.py ROOT` | Remove the repeated blocks (one-sentence lines, recaps, trap quotes, glossary, ledger tags) from the explanation |
| `scripts/merge_summary.py ROOT` | Migrate an old two-file bundle (separate visual summary) to the one-file lesson |
| `scripts/make_exam.py UNIT_DIR --count N` | Build `07-exam.md` and `08-exam-key.md` covering every chapter (`make_domain_exam.py` is the older name and writes the older file names) |
| `scripts/apply_banner.py ROOT` | Add audience banners (idempotent) |
| `scripts/add_toc.py ROOT [--check]` | Add or refresh the table of contents in every generated markdown file |
| `scripts/build_chapter.py UNIT_DIR spec.py ...` | Assemble ledger, lesson, quiz, key and flashcards from a chapter spec module |
| `scripts/reading_load.py ROOT` | Reading minutes per chapter and unit; flags an at-a-glance block over 5 min or a lesson file over 12 min |
| `scripts/review_schedule.py` | Dated spaced-review plan from a start date and an exam date |

## Conduct

- The student is preparing under pressure. Be direct, warm, and fast. Celebrate clean sweeps briefly; never dwell on misses beyond the anchor.
- If the student is frustrated with the method, the method is wrong: acknowledge in one line, fix it, and continue. No defensiveness, no meta-discussion.
- Everything adapts to the student's stated goal (an exam, a work skill, general understanding) — tune question style and depth to that goal.
