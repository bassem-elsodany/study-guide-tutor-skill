# Question Design Rules

Every rule here exists because its violation lets a student pass the question without knowing the material — which defeats the entire purpose of quizzing. Apply all of them to every question.

## Rule 1 — Test substance, never the material itself

A question must test the concept, rule, or distinction the material teaches — never the material as an object.

**Banned question shapes:**
- "What is the purpose of this slide / section / chapter?"
- "What does the agenda say will be covered?"
- "Which topic comes next in the material?"

**Why:** these test attention to formatting, not knowledge. They waste the student's time and build false confidence.

**Bad:**
> What is the purpose of an "In this lecture" slide?

**Good:**
> A socio-technical view of an AI system means governance must consider: (A) only the algorithm's code … (C) both the technology and the human/organizational context around it …

## Rule 2 — Scenario-based by default

Wrap the concept in a realistic situation: a company, a decision, a failure, a regulator's question. The student must apply the knowledge, not just recognize a definition. Definition-recall questions are allowed sparingly for vocabulary-heavy blocks, but scenarios carry the weight.

**Pattern:** [Actor] does [action] in [context]. [Complication occurs]. Which [rule/concept/classification] applies, and why?

## Rule 3 — Four options, all equally dressed

Exactly 4 options (A–D), exactly one correct.

The correct answer must be **indistinguishable by form**:
- All four options approximately the same length.
- All four written with the same level of detail and the same confidence of tone.
- Never give the correct option extra explanation, justification, or qualifying clauses that the wrong options lack. If the correct answer needs three lines, write the distractors at three lines too.

**The tell to eliminate:** if someone who knows nothing could pick the correct answer because it is the longest, most carefully reasoned option, the question has failed. Rewrite the distractors up, or the correct answer down.

## Rule 4 — Randomize the answer key

Before sending a question set, audit the answer key. If a pattern exists (always B, alternating, clustered), reshuffle. Across a block of 4–6 questions, spread correct answers over at least three different letters.

## Rule 5 — Distractors must be plausible traps

Each wrong option should represent a specific, common misunderstanding:
- The adjacent concept (the thing most often confused with the right answer)
- The right concept at the wrong scope (too broad or too narrow)
- A true statement that does not answer the question asked
- A confident misreading of a detail (wrong threshold, wrong role, wrong jurisdiction)

A distractor that no one would ever pick is a wasted slot — effectively turning a 4-option question into a 3-option one.

## Rule 6 — State the context the answer depends on

If the correct answer depends on jurisdiction, time period, role, or any scope condition, state that condition in the scenario explicitly ("A **US** bank…", "Under the **EU** framework…", "The **deployer**, not the vendor…").

If the question is deliberately testing whether the student can identify which context applies, signal that this is the test rather than leaving it ambiguous.

If the student gives a wrong-but-defensible answer because the question omitted a needed condition, credit the answer, admit the flaw, and fix all future questions. Never grade a student down for an ambiguity the question created.

## Rule 7 — Label difficulty, mix difficulty

Tag each question (Easy), (Medium), or (Hard):
- **Easy** — direct application of one concept in a thin scenario.
- **Medium** — requires choosing between two adjacent concepts, or applying a rule plus its exception.
- **Hard** — multi-factor scenarios: several concepts interact, several harms or rules compound, or the student must map a full framework onto a messy situation.

Every block gets at least one of each. Merged blocks get proportionally more questions so coverage does not shrink.

## Rule 8 — Numbers and details must be internally consistent

When a question includes figures (thresholds, percentages, dates), make exactly one option consistent with the material, and make at least one distractor misstate the arithmetic or the threshold — that is a legitimate trap. But verify the correct option's numbers are actually right against the source before sending.

## Rule 9 — One concept per question

Each question tests exactly one concept, rule, or distinction. If it needs two facts to be right, it is two questions; a miss on a double-barreled question cannot be diagnosed.

## Rule 10 — Hints are optional, on request, and never give the answer

Offer a one-line hint on Medium and Hard questions, shown only if the student asks. A hint points at the *type of reasoning* ("think about who decides versus who executes"), never at the option or a keyword that appears in only one option. If the student uses a hint, note it in the running record: a hinted correct answer is a half-win and goes on the revisit list if the concept is high-yield.

## Rule 11 — Every question traces to the source

Before sending, run the quiz audit pass in `source-fidelity.md`: the key maps to a ledger entry and location, numbers match exactly, every distractor is wrong per the material, and no question depends on outside knowledge. No source location, no question.

## Rule 12 — Math in LaTeX

Use `$...$` inline and `$$...$$` for block formulas in questions, options, hints and explanations. Escape a literal dollar sign as `\$`.

## Grading protocol

For each answered question:
1. State the student's letter and verdict.
2. For a miss: give the correct letter, explain the specific trap their choice represented, and attach a one-line memory anchor.
3. Report the block score and keep the running tally for the final summary.

Track four numbers per block, not just the score: **right, wrong, skipped, hinted**. Report accuracy as right out of *answered* questions, and the score as right out of *total*, so a student who skips does not hide behind a high accuracy figure.

Cite the source location (e.g., "Slide 44") with each explanation so the student can re-read the exact spot.

### Review mode and retake

After a graded block, offer a **review pass**: walk the student's misses and hinted answers one by one (question, their pick, key, trap, anchor). Then offer a **retake of the misses only**, using *fresh variants*: same concept, new scenario and new option order, never the identical stem, so the student shows the concept rather than recalls the question. Repeat until the misses are cleared; whatever still fails goes on the final revisit list.

A memory anchor is short and concrete: a contrast ("documents 10 years, logs 6 months"), a name ("the misleading-name trap"), or a real case the material cited. Anchors are what the final revisit list is built from.


## Measured balance (added in v0.4.0)
- Key-longest share: about 25-35% of questions over a domain; never a key 8% or more longer than the longest wrong option. Write wrong options as near-miss clones of the key (same structure and length, one fact swapped), not as shorter statements. Run `scripts/audit_quiz.py`.
- Spread key letters across a domain (about equal A, B, C, D) and never three identical letters in a row.
- Every wrong option has its own why-wrong bullet, and every question has a hint line that does not reveal the answer.
- Why-wrong bullets must not rely on outside knowledge or add claims the slide does not make.
