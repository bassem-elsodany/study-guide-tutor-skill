# Independent fidelity review

The author of a bundle cannot be its only checker. Before a domain is called done, run a second agent that did not write it.

## When
After the chapters, overview files and domain exam exist and `audit_quiz.py` and `check_bundle.py` pass.

## How (one reviewer per about 8-10 chapters, run in parallel, read-only)
Give each reviewer: the domain folder, the source text extracted per slide, the rule "material-only" and this task:
1. For each chapter pick 3 quiz questions (at least one Hard and one that tests a number or list). Check that the key is supported by the cited slide, each wrong option is actually wrong per the slides (not accidentally also correct), the why-wrong bullet is accurate, and numbers and list items match exactly.
2. Pick 5 ledger entries (numbers, dates, lists, attributions) and compare them with the slide text word for word, including the slide number.
3. Check 4-6 questions from the final quiz or domain exam and 6-8 rows of the cram sheet counts.
4. Report under 450 words: counts checked, then every problem with file, question or ID, the slide quote as evidence, and severity: HIGH (a key or fact is wrong, or a wrong option is also correct), MEDIUM (misleading or imprecise), LOW (cosmetic or an explanation that goes beyond the slide).

## What to do with findings
- Fix every HIGH and MEDIUM before delivery; fix LOW when cheap. Typical LOW findings: a why-wrong bullet that uses outside knowledge, an inference stated as slide text, "taught next" glosses, an abbreviation the slide never expands.
- Re-run the audits after fixes. Record the review and its results in the domain README status table.
- A reviewer that fails (rate limit, error) leaves the domain unreviewed: say so plainly.
