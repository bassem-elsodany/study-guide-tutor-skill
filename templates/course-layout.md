# Course layout (what the skill generates)

The folder tree mirrors the structure of the material itself, and the **grouping level is optional**. The skill decides the shape from the material and confirms it with the student once. A *unit* is any folder that directly holds `chapter-*/` folders (the whole course when flat, one group otherwise); the scripts find units on their own.

## Shape A: flat (a book, one deck, a single course)

```
my-course/
├── README.md                      start here: the player, the loop, the chapter table
├── learner-profile.md             written after the intake
├── assets/                        the original material + the extracted text cache
├── 00-overview/
│   ├── README.md                  what each overview file is for and when to use it
│   ├── 01-concept-map.md
│   ├── 02-cram-sheet.md
│   ├── 03-final-quiz.md · 04-final-quiz-key.md
│   ├── 05-score-tracker.md · 06-revisit-list.md
│   ├── 07-exam.md · 08-exam-key.md
│   └── 09-study-player.html       interactive player built from the files above
├── chapter-01-short-slug/
│   ├── 01-lesson.md               at a glance, numbered sections, tricky parts, say it back, traps, next
│   ├── 02-flashcards.csv
│   ├── 03-quiz.md
│   ├── 04-answer-key.md           separate so the student can quiz without spoilers
│   ├── 05-review.md               created only after grading
│   ├── 06-notes.md                the student's own highlights and notes (written by the study player, never regenerated)
│   └── 99-fact-ledger.md          every checkable fact with its source location
└── chapter-02-short-slug/
```

## Shape B: grouped (modules, weeks, parts, volumes, domains)

Name each group folder with the source's own word and number. Chapter numbers restart in each group, and each group has its own `00-overview/` and its own player.

```
my-course/
├── learner-profile.md
├── assets/
├── module-1/                      or week-01, part-1, domain-1 ...
│   ├── README.md
│   ├── 00-overview/               same files as above
│   ├── chapter-01-short-slug/
│   └── chapter-02-short-slug/
└── module-2/
    ├── README.md
    ├── 00-overview/
    └── chapter-01-short-slug/
```

If the source nests deeper than one grouping level, keep the top level as the group and fold the lower level into the chapters. Do not add a level the source does not have.

## Rules

One folder per chapter named `chapter-NN-slug` (even when the source says lecture or lesson, so the tools find it); every file carries a number that is its reading order; every markdown file ends with one audience note; the layout is confirmed with the student once and never invented.
