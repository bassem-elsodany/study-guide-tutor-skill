# Intake Analysis (Phase 0)

Nothing is generated until the student's profile is known. A beginner needs plain words and everyday examples; an advanced student needs none of that. Guessing wrong wastes the student's time either way, so ask first.

## Rules

1. **Ask before generating**, every time a new course starts and no profile exists.
2. **Every question is multiple choice.** Use the structured question tool (up to 4 questions per call, 2-4 options each, a short description per option, the recommended option first). Never ask an open-ended question; the tool adds "Other" automatically for anything the options miss.
3. **Skip what is already known.** If `learner-profile.md` exists, show it in one line and ask only whether it still holds.
4. **If the tool is unavailable**, present numbered options and accept a letter or number as the reply.
5. **If the student declines or says "just start"**, use the balanced defaults (below), say so in one line, and mark the profile "defaulted, not confirmed".
6. **Save the answers** to `learner-profile.md` at the course root (the course folder, above any groups) before generating anything.
7. **Re-profile** when the student says it is too easy, too hard, too simple or too dense, or when graded results show the level is wrong. Update the profile, bump its version, and regenerate the affected files; list exactly which.

## Core question bank (ask all nine; two or three tool calls)

| # | Header | Question | Options |
|---|---|---|---|
| 1 | Knowledge | How well do you know this topic today? | **Beginner** (new to it) · **Some familiarity** (know the basic terms) · **Intermediate** (use it at work or study) · **Advanced** (practitioner, know most of it) |
| 2 | Background | What is your background relative to this topic? | **Non-technical** (legal, compliance, business) · **Technical** (engineering, data, IT) · **Mixed** |
| 3 | Goal | What are you studying for? | **Pass a certification exam** · **Apply it at work** · **General understanding** · **Teach or review others** |
| 4 | Time | How much time do you have? | **Under 2 weeks** (cram) · **2-6 weeks** · **2+ months** · **No deadline** |
| 5 | Explanations | How should I explain things? | **Simplified** (plain words, step by step) · **Balanced** · **Concise and advanced** (assume I know the basics) |
| 6 | Examples | What kind of examples help you most? | **Everyday analogies** · **Real-world cases and business scenarios** · **Both** · **Minimal** (only what the source uses) |
| 7 | Quiz level | How hard should the quizzes be? | **Gentle ramp** (mostly easy, building up) · **Mixed** (easy, medium, hard) · **Exam-level** (mostly medium and hard) |
| 8 | Pace | How big should each study step be? | **Small steps** (short sections, frequent checks) · **Standard** · **Large blocks** (fewer, longer) |
| 9 | Memory aids | Do you want memory aids? | **None** (only if I ask later) · **Analogies and anchors only** · **Mnemonics welcome** |

Optional follow-ups, also multiple choice, when they would change the output: weakest area (list the course's chapters), prior attempts at the exam, hours available per week, whether tables or diagrams help more.

## Balanced defaults (when the student declines)

Some familiarity · mixed background · exam goal · 2-6 weeks · balanced explanations · both example types · mixed quizzes · standard pace · analogies and anchors only.

## What each answer changes

### Knowledge level (the main switch)

| | Beginner | Some familiarity | Intermediate | Advanced |
|---|---|---|---|---|
| Terms | Every term defined in plain words on first use; a glossary closes each lesson | Defined briefly on first use | Terse definitions only where the source defines them | Basics listed as "assumed known" and skipped |
| Examples | One everyday analogy per core concept, then the source's own example | Analogy only for hard concepts | None unless asked | None; use edge cases and cross-links instead |
| Structure | Short steps; a one-sentence summary after each step; few new terms at once | Standard | Tables and distinctions first | Deltas, exact figures, exceptions, cross-chapter links |
| Exam traps | Each trap explained with why it fools people | Named with the separator | One-line separators | Only the subtle ones |
| Quiz mix (easy / medium / hard) | about 50 / 35 / 15 | about 30 / 50 / 20 | about 15 / 50 / 35 | about 0-10 / 40 / 50+ |
| Hints | Offered proactively on Medium and Hard | On request | On request | Withheld unless asked |
| Misses | Re-explained with a new analogy, then retaken | Re-explained once, then retaken | Anchor only, then retaken | Anchor only |
| Flashcards | Plain-language answers, short | Standard | Compressed | Traps, numbers and exceptions only |

### Background

- **Non-technical:** add plain-language bridges for technical material (algorithms, infrastructure, security attacks) using business or legal analogies; expand nothing in the non-technical material beyond what the source says.
- **Technical:** compress technical material; spend the saved space on the non-technical side of the subject (policy, law, business context) and "why it matters in practice" framing.
- **Mixed:** standard depth, with a one-line bridge in each direction where a term crosses the divide.

### Goal

- **Exam:** exact figures, traps, list membership, cram sheet, final cumulative quiz.
- **Work:** applied scenarios and "what would you do" framing; fewer memorize-the-number items.
- **General understanding:** concepts and examples over exact figures; shorter quizzes.
- **Teach or review:** add a short "how to explain this" note and common misunderstandings per chapter.

### Time

- **Under 2 weeks:** cram-first order (cram sheet, flashcards, quiz, misses); merged blocks; fewer questions per block.
- **2-6 weeks and beyond:** full teaching loop; spaced revisit of misses (next day, a few days later, the week after).
- **No deadline:** full loop, deeper examples, no compression.

### Pace

- **Small steps:** split each chapter into short sections with a 1-2 question check after each.
- **Standard:** chapter-level lessons and chapter-level quizzes.
- **Large blocks:** merge chapters where the source allows; add questions so coverage does not shrink.

### Memory aids

- **None:** no mnemonics (mention that the source has its own, if it does).
- **Analogies and anchors only:** memory anchors on misses; analogies where the level calls for them.
- **Mnemonics welcome:** create one per list or confusable pair, labeled "memory aid", never replacing the source wording.

## Learner profile file

Saved at `<course>/learner-profile.md`:

```markdown
# Learner Profile (version 1)

| Question | Answer |
|---|---|
| Knowledge | Beginner |
| Background | Non-technical |
| Goal | Pass a certification exam |
| Time | 2-6 weeks |
| Explanations | Simplified |
| Examples | Both |
| Quiz level | Gentle ramp |
| Pace | Standard |
| Memory aids | Analogies and anchors only |

Audience statement: <one sentence for the footer note, e.g. "a beginner to the topic with a technical background, preparing for an exam in 2-6 weeks">
Status: confirmed (or: defaulted, not confirmed)
Date: YYYY-MM-DD

## Adaptation rules derived from this profile
- (one line per rule that changes the output, taken from the tables above)
```

## Audience note on every generated document

Every generated file (lesson, ledger, quiz, key, cram sheet, flashcards notes, README, overview files) ends with **one combined audience note**, so a reader knows whom it was written for and what that changed. There is no banner at the top: the file opens with its title and contents. Markdown files use a blockquote after a `---` rule, between `<!-- audience-banner:end -->` markers; CSV files carry no note (their profile line goes in the chapter README or lesson).

```markdown
---

<!-- audience-banner:end -->
> **Audience:** written for a beginner to the topic with a technical background, preparing for an exam in 2-6 weeks. Adapted to the learner profile: pictures and tables first, definitions in plain words, an example per idea. Left out: only what the goal does not test; the fact ledger keeps every fact. Facts never change with the level, only the wording, examples, order and difficulty. Wrong level ("too simple", "too dense", "too easy", "too hard")? Tell me and I will regenerate. Profile: [`learner-profile.md`](../../learner-profile.md), version 1.
<!-- /audience-banner -->
```

`scripts/apply_banner.py` writes it (and migrates old two-part banners: the top block is removed and the footer is rebuilt from the old check text).

State plainly in the note what was simplified, what was added, what was skipped, and what is assumed known. Never imply the content is easier than the source: the facts and exam coverage stay identical across levels; only the explanation, examples, ordering and difficulty mix change.

## Regeneration rule

Changing the profile changes the explanation layer only. The fact ledgers are level-independent and stay as they are. Regenerate lessons, quizzes, answer keys, flashcards, cram sheet and overview files, and update the banners, tracker and README in the same pass.
