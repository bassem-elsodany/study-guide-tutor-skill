# study-guide-tutor-skill

**Hand your AI assistant a PDF, a slide deck or your notes. It teaches you what is in them, quizzes you until it sticks, and shows you exactly what to revisit.**

![The practice page the tutor builds for you: you picked the wrong answer, the right one is green, and every option comes with the reason it is wrong and the slide it comes from](docs/images/player-quiz.png)

*The practice page the tutor builds for you (a real screenshot). Here: a 10-slide PDF about the water cycle.*

[![CI](https://github.com/bassem-elsodany/study-guide-tutor-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/bassem-elsodany/study-guide-tutor-skill/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [![Release](https://img.shields.io/github/v/release/bassem-elsodany/study-guide-tutor-skill)](https://github.com/bassem-elsodany/study-guide-tutor-skill/releases)

## What you get

- **A tutor that asks about you first.** Your level, your goal, how much time you have. Everything it writes is written for you.
- **Lessons that teach.** Short and clear, with a "tricky part" warning wherever people usually get confused, not slides re-typed into bullet points.
- **Practice that gives the reason.** Click an answer and see at once why each wrong option is wrong and which slide the fact came from.
- **Flashcards and a mock exam.** Cards come back just when you are about to forget them; a timed exam shows which chapters to go back to.
- **It works with what you have.** PDFs, PowerPoint, Word, notes, web pages, lecture transcripts, scanned pages; in any language; however your material is organised.

## See it in action: a 10-slide PDF about the water cycle

Say you have a short PDF about the water cycle. (A copy is in [`examples/water-cycle/`](examples/water-cycle/water-cycle.pdf), so you can follow along.) This is what happens, step by step. The tutor's wording below is illustrative; the questions, lesson text and practice page are real.

### 1. You hand it the file

```text
you    > Teach me this PDF.        [water-cycle.pdf]
```

### 2. It reads everything first, then asks about you

```text
tutor  > I read all 10 slides and found 10 facts worth teaching, one of them a number (97%).
         Before I write a word, nine quick questions so this fits you. Tap one answer each time:
```

| # | The tutor asks | You choose from |
|---|---|---|
| 1 | How well do you know this topic today? | Beginner · Some familiarity · Intermediate · Advanced |
| 2 | What is your background? | Non-technical · Technical · Mixed |
| 3 | What are you studying for? | A certification exam · Work · General understanding · Teaching others |
| 4 | How much time do you have? | Under 2 weeks · 2-6 weeks · 2+ months · No deadline |
| 5 | How should I explain things? | Simplified · Balanced · Concise and advanced |
| 6 | What kind of examples help you most? | Everyday analogies · Real-world cases · Both · Minimal |
| 7 | How hard should the quizzes be? | Gentle ramp · Mixed · Exam-level |
| 8 | How big should each study step be? | Small steps · Standard · Large blocks |
| 9 | Do you want memory aids? | None · Analogies and anchors · Mnemonics too |

Your answers become a one-page profile that shapes every file. Pick *Beginner, Non-technical, Simplified, Everyday analogies* and every idea comes with plain words and a picture from daily life. Pick *Advanced, Concise, Exam-level* and the basics are skipped and the questions get harder. Change your mind any time: say **"too dense"** or **"too easy"** and the tutor rewrites the affected files.

### 3. It shows you the plan before it writes anything

```text
tutor  > Two chapters:
           1. The four stages           (slides 2-6)
           2. Where the water goes      (slides 7-10)
         Every fact keeps its slide number, so you can always find the source.
         Start with chapter 1?
```

If your material comes in modules, weeks or parts, the tutor mirrors that instead; a plain book or a single deck stays a simple list of chapters. You confirm the layout once.

### 4. Each chapter is a lesson written like a teacher would

A three-minute summary comes first, then the story, with a warning wherever people usually slip. This is real text from chapter 1:

> *Everyday picture:* a wet towel on a washing line. The towel dries because the water leaves it as vapour, and the line is not even hot.
>
> **⚠ Tricky part: evaporation or condensation?**
> Both involve water vapour, so they get swapped.
> **Hint:** ask which way the water is changing: from liquid up into vapour, or from vapour back into droplets.

Try the hint first. Then open the box for the rule and a memory hook. Each chapter ends with the traps people fall into.

### 5. Then you practise

That is the page in the picture at the top: one file you open by double-clicking it, no install needed.

| Tab | What it does |
|---|---|
| **Quiz** | click an answer; the right one turns green at once, and you see why every wrong option is wrong. Hints are optional and shown only when you ask. |
| **Flashcards** | flip, then "knew it" or "missed it". A card you miss comes back today; one you know comes back after 1, 3, 7, then 14 days. |
| **Exam** | a timed mock exam with no feedback until you finish, then a list of the chapters to revisit. |
| **Progress** | your scores, the questions you still miss, and a button to save your results. |

### 6. Afterwards

Save your results and send the file to the tutor. It writes a short review of what you missed, adds those points to your revisit list, and plans when to come back to them.

**Want to see the real thing?** Open [`examples/water-cycle/course/`](examples/water-cycle/course/README.md): the whole course the tutor made from that PDF. Download `00-overview/09-study-player.html` and double-click it to try the practice page yourself.

## Install (two minutes)

In Claude Code:

```
/plugin marketplace add bassem-elsodany/study-guide-tutor-skill
/plugin install study-guide-tutor-skill@study-guide-tutor-skill
```

Then run `/reload-plugins`, put your PDF in a folder, and say **"Teach me this PDF."** (Or type `/study-guide-tutor-skill:study my-notes.pdf`.)

Using another AI tool, a team setup, or something not working? See [docs/installation.md](docs/installation.md). The same plugin is also available from the [bassem-elsodany-agent-skills](https://github.com/bassem-elsodany/bassem-elsodany-agent-skills) catalog, together with the Rust skills.

## Things you can say

| You say | What happens |
|---|---|
| "Teach me this PDF" | intake, plan, then lessons one chapter at a time |
| "Quiz me on chapter 2" | questions with instant reasons, saved results |
| "Make me the practice page" | the clickable page: quiz, flashcards, exam, progress |
| "I only have an hour before the exam" | a short recap of what matters, flashcards, one quiz on the weak spots |
| "Quiz me on what I missed" | fresh questions on your misses until they clear |
| "Check everything" | the tutor checks the course for mistakes and tells you what it found |

## Questions

**Does my material leave my computer?** The skill itself makes no network calls and keeps everything in your folder. Like any AI assistant, the text you give it is processed by the AI service you use, under that service's terms.

**Do I need to be technical?** You need an AI assistant that supports plugins, such as Claude Code, and two commands to paste. After that it is a conversation and a web page.

**Which files can it read?** PDF, PowerPoint (`.pptx`), Word (`.docx`), Markdown and plain text, web pages, e-books (`.epub`), subtitle and transcript files, images, or a folder of scanned pages. Spreadsheets, audio and video need a transcript first.

**My notes are not in English.** Fine. The tutor writes in your language. For a language other than English it also uses a small settings file for the wording; the sample course in `tests/fixtures/spanish-course` shows how, and Arabic, Hebrew, Persian and Urdu flip the page to right-to-left.

**Is it only for exams?** No. Pick "General understanding" or "Apply it at work" at the intake and the tutor adjusts what it asks of you.

**What does it cost?** The skill is free and open source. You pay for your AI assistant as usual.

## Good to know

- It has been built and tested on one real 43-chapter course and on small invented examples (including a Spanish one). It has not been tried on every kind of material.
- Word and PowerPoint files are read as text only: tables, charts and pictures inside them are not understood. A scanned page needs the tutor to look at it.
- The quizzes check facts that are in your material. They do not bring in outside knowledge, on purpose, because exams test the course's version.
- The checks behind the scenes are automatic but not perfect; a careful reader still beats them.

## For the curious

- [How it works](docs/how-it-works.md): the teaching loop, the checks that keep it honest, the folder layouts, the settings file.
- [Installation](docs/installation.md): every way to install, other AI tools, fixes for common problems.
- [Contributing](CONTRIBUTING.md) · [Changelog](CHANGELOG.md) · [Security](SECURITY.md)

## Licence

MIT: see [LICENSE](LICENSE). Notes on optional tools and on the study material you add are in [NOTICE.md](NOTICE.md).
