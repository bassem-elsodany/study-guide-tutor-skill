# Source Fidelity

A tutor that teaches or quizzes a wrong number is worse than no tutor: the student memorizes the error and loses the mark. Exams hinge on exact thresholds, dates, attributions and rankings. This file is how the tutor keeps every taught fact and every quiz key traceable to the student's material.

## 1. The fact ledger (built in Phase 1, before any teaching)

After reading the whole material, extract every checkable fact into a private ledger. Extraction and teaching are **separate passes**: finish extracting before teaching a single block, and do not "discover" new facts mid-block without adding them to the ledger. This keeps explanations and questions consistent with each other.

Format: `[F014] | fact | type | location`

```
[F014] | "Fines up to 4% of global annual turnover" | Statistic | Slide 61
[F015] | "Provider, not deployer, owns conformity assessment" | Rule | Slide 63
[F016] | "According to the OECD (2019), principles are non-binding" | Attribution | Slide 12
```

Fact types (these are what exams are made of):

| Type | Pattern | Example |
|---|---|---|
| Statistic | Any number with unit or context | "72 hours", "4%", "10 years" |
| Comparative | X is more/less/faster than Y | "Opt-in is stricter than opt-out" |
| Temporal | Time-bound assertion or deadline | "Applies from 2026" |
| Attribution | Claim tied to a source or person | "According to NIST…", "Smith et al. found…" |
| Causal | X causes / leads to / requires Y | "Breach triggers notification" |
| Existence | Asserts something exists or applies | "Seven principles", "three roles" |
| Ranking | First, largest, top-N, order | "Highest risk tier" |
| Quote | Direct quotation | Any attributed quote |
| Rule / Definition | What a term means, what a rule requires | Taught and tested, so it is ledgered here |
| Exception | The carve-out to a rule | "Except for law enforcement…" |

Adaptation note: a pure fact-checker ignores definitions because they are not "claims". A tutor must ledger them, because definitions and exceptions are what exams test most.

Opinions and hedges in the material ("we believe", "could potentially") are taught as the author's view, never as settled fact. Methodology descriptions and acknowledgments are skipped.

Do not dump the ledger on the student. Report only its size and shape ("141 checkable facts, 38 of them numbers or deadlines") and show entries when the student disputes something or asks "where does it say that?".

## 2. Exact figures, always

Numbers are taught and quizzed exactly as the material states them.

| Situation | Treatment |
|---|---|
| Material says 96.555% | Teach 96.555%. Never round to 97% in an explanation or in the correct option |
| Unit differs (0.96 vs 96%) | Treat as a different statement; keep the material's unit |
| Direction (increase vs decrease, before vs after) | A flipped direction is a wrong answer, not a rounding |
| Order of magnitude ($4.7B vs $47B) | Wrong answer |
| Material itself gives the rounded form ("96.555%, about 97%") | Either is fine; cite which |
| "Approximately / about" in the material | Teach it as approximate; do not sharpen it into an exact figure |

Wrong numbers belong only in distractors, and each must be wrong in a specific, plausible way (rounded, transposed, off by one tier, wrong unit), never random.

## 3. Source boundary

Pick one mode at the start and tell the student which:

- **Material-only (default for exam prep).** Everything taught and everything in a quiz key traces to the material, because the exam tests the course's version of the truth. Anything the tutor adds from general knowledge is prefixed **Outside the material:** and is kept out of quizzes unless the student asks.
- **Enriched.** The student wants context beyond the slides (real cases, background). Outside additions are still labeled, and still never used as the keyed answer unless the student says the exam covers them.

Triggers for material-only: "only use this document", "stick to the slides", "it's an exam on this course". Switch freely when the student asks; never switch silently.

Conflicts:
- **Material vs. outside reality** (an outdated figure, a simplification): teach the material's version for the exam, flag the discrepancy once in a single line, move on.
- **Material vs. itself** (slide 12 says 30 days, slide 40 says 60): surface both with locations and ask which the course emphasizes. Do not guess.
- **Missing from the material** but the student asks: answer, labeled "Outside the material", and say it will not be keyed.

## 4. Say how sure you are

In explanations, keep three things distinguishable:

| Label (in prose) | Meaning |
|---|---|
| "The slides say…" | Exact or close paraphrase of the material |
| "That means…" / "So in practice…" | The tutor's interpretation or worked consequence |
| "Outside the material:" | General knowledge, not in the source |

When unsure whether the material actually says something, say so and check the ledger or source rather than assert. A conservative "let me confirm that in your slides" beats a confident wrong answer.

## 5. Quiz audit pass (before sending any question set)

Run this on every set. It is a hard gate: a question that fails is rewritten, not sent.

1. **Trace the key.** The correct option maps to a ledger entry and a source location. No location, no question.
2. **Check the numbers.** Every figure in the correct option matches the material exactly.
3. **Check the distractors.** Each wrong option is wrong per the material, in a specific way. If a distractor could be defended from the material, the question is ambiguous: fix it.
4. **No outside dependency.** Answering correctly must not require knowledge the material does not contain (unless the student chose enriched mode).
5. **Single defensible key.** Exactly one option is right according to the material.

Keep the location with each answer in the private key and cite it when grading ("Slide 44"). That lets the student check you and re-read exactly the right place.

## 6. Charts, tables and figures in the material

For every chart or table the material uses:

1. Read the actual values, axis labels, units and legend. Do not teach from the caption alone.
2. Note visual traps the material might be exploiting or discussing: truncated axis, 3-D distortion, missing error bars, cherry-picked time range. When the course covers misleading visuals, these are exam content; when it does not, mention a distortion in one line so the student reads the chart correctly.
3. Ledger the values the way you would a statistic, with the slide location.

## 7. Attribution stays attached

When the material says "According to X (year)…", teach it as an attribution, not a bare fact. Exams routinely test who found, said or required something. Never strip the source off a claim to make an explanation shorter.

## 8. Verifying the material itself (only on request)

Normally the material is the authority. If the student asks "is this actually true?" or wants the material checked against the outside world:

- Run it as a separate task after the teaching loop, not inside it.
- Prefer primary sources (original study, official report), then government or institutional bodies, then peer-reviewed work, then named industry reports, then news citing primaries, then compilations.
- A fact with no authoritative source found is **unverified**, not "false". Conflicting sources: report both, do not pick silently.
- Report discrepancies as a short list (material says / source says / location); the student decides what to do with it for the exam.
