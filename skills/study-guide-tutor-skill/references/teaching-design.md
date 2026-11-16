# Teaching design: teach, do not dump

## The writer is a teacher, not a copier

Never write a lesson by walking through the slides and rephrasing them. That adds no value: the student could read the PDF faster. Before writing a word of the lesson, work as a teacher in five steps. The first four happen in working notes (the "teaching brief"); the brief is not delivered.

1. **Understand.** Read every slide of the chapter and its ledger entries. For each core idea (usually 3 to 6) write what it *is for*: the problem it exists to solve, in one plain sentence. If you cannot say why it exists, you do not understand it yet; reread.
2. **Reason about the structure.** Which ideas depend on which? What must be known first? Which ideas look alike and get confused (the exam traps)? Which slides are lists that need no teaching, and which hide the real idea? Where does the chapter connect to earlier chapters and to the next section?
3. **Reason about the learner.** Read the learner profile and decide the approach from it: level (what to define, what to skip because they already know it), goal (exam: what is asked and how it is asked), time (how much depth is affordable), style (analogy first, real case, tables, pictures). Write down the three or four concrete choices you made because of this learner.
4. **Plan the lesson in the brief:** the running scenario; the order of questions the sections answer; the decision diagrams; the predict checks (scenario plus answer plus reason); the links between sections; what you will deliberately leave short.
5. **Write from the brief, in a teacher's voice** (direct, concrete, explaining why), then verify every fact, figure and list against the ledger and cut anything that fails the value test below.

## Value test (apply to every paragraph)

For each paragraph name what it adds beyond the slide: a *why*, a *link* to another idea, a concrete *example*, a *check* the student answers, or a *decision aid* (diagram or table of "if this problem, then that tool"). If it adds none, delete it. The exam facts must still appear, exactly as printed, but inside the explanation, not as a pasted list.

A lesson that re-formats the slides into tables is a dump. The student can read the slides faster. A lesson earns its place only by doing what the slides do not: explaining why, connecting the ideas, and making the student check themselves. Student reviews consistently rejected dump-style lessons.

## Every lesson must

1. **Run on one thread.** Pick a single running scenario (prefer one the material itself uses, such as its own flight-delay or hiring example) and follow it through the chapter. Label anything that is your own story or analogy ("my analogy", "my link").
2. **Organise by the question each section answers**, not by the slide titles. Open each section with the problem ("Can we trust and use the data?"), then the idea, then the exam facts. End it with the question that leads into the next section.
3. **Link the ideas.** Say how a concept connects to earlier ones (drift leads to regeneration of features; localization leads to federated learning). Links that are on the slides are stated plainly; links that are your inference are prefixed "Outside the material (my link):".
4. **Make the student predict.** After each core idea, add a "Predict" check in a collapsible `<details>` box: a short scenario, the student commits to an answer, then opens the box for the answer and the reason. Close the lesson with "Say it back" recall prompts. This is the interactive part inside the file; in chat, the tutor asks the same prompts one at a time.
5. **Draw the decision, not the list.** Use a Mermaid decision or flow diagram for choices the exam asks ("what kind of drift?", "which PET solves which problem?"). Plain lists become tables. No chapter-map diagrams.
6. **Keep the at-a-glance block short** (about 3 minutes): the story picture, the decision pictures, the words, and a short "Look-alikes to keep apart" table only for facts the quiz tests that no other table holds. **Traps are not in this block**: they close the lesson (see below). Do not paste the flashcards into it. Mark a hand-written block with `<!-- authored -->` right after `<!-- glance -->` so `make_glance.py` never overwrites it.
7. **State each fact once** and keep every figure and list exactly as the material prints it.
8. **Warn where the confusion happens: "Tricky part" callouts** (see the next section). Two to four per chapter, placed in the numbered section right after the idea that causes the mix-up.

## Traps to avoid is the closing section

The teacher warns about the traps last, after the student has understood the chapter and practised it, not before: a list of mix-ups means little to someone who has not met the ideas yet. Put `## Traps to avoid` (markers `<!-- traps -->` ... `<!-- /traps -->`) after `## Say it back` and before `## Next`: one sentence ("The last warning before the quiz..."), then the table (trap | why it fools people). It is the index of the "Tricky part" callouts above it, one row per mix-up, in one line each. The top block must still let the student pass the quiz, so any quiz fact that only the traps table states is also written in the top block's "Look-alikes to keep apart" table.

## Tricky-part callouts (hints where students get confused)

The closing traps table is the index of confusions; it is far from the paragraph where the student actually gets confused and it does not say how to tell the two things apart. A callout fixes that. Exact shape (the gate `scripts/check_tricky.py` checks it):

```
> **⚠ Tricky part: decay or drift?**
> Both lower accuracy, so they get swapped.
> **Hint:** ask where the change comes from.

<details>
<summary>Rule and anchor</summary>

**Rule:** decay = old static data; drift = the world moved.
**Anchor:** a short contrast or real case (label your own as "my anchor").
</details>
```

Rules:
- **Pick from evidence, not feeling.** A confusion qualifies when it is (a) the pair or list the quiz distractors lean on (open `03-quiz.md` and look at the wrong options), (b) a look-alike pair in the ledger, (c) a misleading name, an exception to a rule, a number that is easy to transpose, or (d) a place the slides contradict themselves or the student-reviewer got confused. Budget: 2 to 4 per chapter (1 only for a very short chapter, recorded in the report). If everything is tricky, nothing stands out.
- **The hint is a test, not the answer.** One line the student can run on a new case ("ask who holds the data", "look for the word *before*"). The answer sits in the collapsed Rule box so the student tries first; this is the same commit-then-reveal habit as the Predict boxes.
- **Fresh wording.** Never reuse a quiz scenario or an option's wording in the callout (`check_findable.py` stays green); the callout teaches the distinction, the quiz tests it.
- **Source boundary.** The Rule holds only what the material says; an anchor of your own is labelled "my anchor". Exact figures stay exact.
- **Index, not duplicate.** Each callout's confusion should also appear as one row of the closing `## Traps to avoid` table, but that row stays one line and the callout carries the hint and rule. State the same fact in at most those two places.
- **Placement.** Inside a numbered section, directly after the explanation it protects and before that section's Predict box when both apply. Never in the glance block, never as a heading (no TOC entry).
- Reading cost: about 40 to 60 words each; it counts toward the 12-minute budget.

## Test before delivery

Run `scripts/check_tricky.py` as well: every chapter needs its callouts, each with a hint and a rule.

The student-persona reviewer must answer without elimination tricks and must say whether it could explain the chapter back in two sentences. A lesson that scores high on exam readiness but low on understanding is a dump in disguise; rewrite it.

## The teacher may merge or split chapters

Chapter boundaries follow the source's headings, but the teacher's job is to deliver the knowledge, not to mirror the table of contents. When teaching a chapter shows that two neighbouring chapters are one story (one problem and its remedy, one list and its classification, a chapter too short to stand alone), merge them; when one chapter holds two stories that each need their own thread, split it. This is a standing permission of the skill: do not ask first, but record the reason in the unit README and tell the student in the wrap-up message.

Signs to merge: the second chapter only makes sense after the first and answers the question the first leaves open; the combined slide range is under about 90 slides and the lesson still fits the reading budget; one running scenario can carry both; the quizzes share concepts and distractors. Signs to split: two unrelated scenarios, or a lesson that cannot fit the budget.

A merge or split keeps the source map intact (the lesson names every slide range), renumbers folders, headings, ledger IDs, flashcards, quiz and key questions, the unit README, concept map, cram sheet, score tracker, revisit list, final quiz and exam together, then runs `check_bundle.py`, `audit_quiz.py` and `make_exam.py`. Never lose a ledger fact or a quiz question in a merge.

## Failures seen in first drafts (check for them)

Student reviews of teacher-written lessons found: confusions the lesson never warned about (the reviewer picked a distractor with no callout nearby); hints that give the answer away; every item marked tricky;  Predict boxes copied from the quiz (the quiz then tests memory of an answer just seen); the same fact in the glance, a table, a Predict answer and "Say it back"; sections that still list slide sentences; terms used before they are defined; fans of seven or eight diagram leaves; a story that is dropped halfway; unlinked "Next" lines. `agents/teacher-writer.md` lists the matching rules.

## The dump gate

Slide dumps are never allowed. `scripts/check_dump.py` fails any numbered section whose wording is mostly the source's, whose tables or lists are mostly slide-length sentences, or that has no teaching element (a Predict check, an analogy, a story or link marker) or under 25 words of explanation. Writers run it on their own lesson and fix every flagged section before reporting done.
