# Course layout (what the skill generates)

The folder tree mirrors the structure of the material. Example for a course with two units:

```
my-course/
├── README.md                      index of the units, status, schedule
├── learner-profile.md             written after the intake
├── assets/                        the original material (slides, notes) + the extracted text cache
├── unit-1/
│   ├── README.md
│   ├── 00-overview/
│   │   ├── README.md                  what each overview file is for and when to use it
│   │   ├── 01-concept-map.md
│   │   ├── 02-cram-sheet.md
│   │   ├── 03-final-quiz.md · 04-final-quiz-key.md
│   │   ├── 05-score-tracker.md · 06-revisit-list.md
│   │   ├── 07-domain-exam.md · 08-domain-exam-key.md
│   │   └── 09-study-player.html       interactive player built from the files above
│   ├── chapter-01-short-slug/
│   │   ├── 01-lesson.md           at a glance, numbered sections, tricky parts, say it back, traps, next
│   │   ├── 02-flashcards.csv
│   │   ├── 03-quiz.md
│   │   ├── 04-answer-key.md       separate so the student can quiz without spoilers
│   │   ├── 05-review.md           created only after grading
│   │   └── 99-fact-ledger.md      every checkable fact with its source location
│   └── chapter-02-short-slug/
└── unit-2/
```

Rules: one folder per chapter named `chapter-NN-slug`; every file carries a number that is its reading order; every markdown file ends with one audience note; the layout is confirmed with the student once and never invented.
