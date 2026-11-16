#!/usr/bin/env python3
"""Assemble a chapter's files from one spec module, so formats never drift.

Usage: build_chapter.py DOMAIN_DIR SPEC.py [SPEC.py ...] --pdf assets/course-notes.pdf --id-prefix C

A spec is a Python file defining:
  NUM, SLUG, TITLE, SLIDES=(first, last)
  LEDGER   markdown body: numbered sections ("## 1. Name (slides)"), entries "- [C02-001] | fact | type | slide",
           then "## Flags on the material (do not quiz on these)"
  LESSON   markdown body after the Source line: "**How to read this chapter:**", numbered sections ("## 1. ..."),
           side-by-side recap, glossary, chapter summary, "## Next"
  QUIZ     list of tuples (difficulty, stem, correct_option, [3 wrong options], key_letter, source,
           fact_line, [3 why-wrong lines in the order of the wrong options], hint)
  CARDS    list of (question, answer)
Writes 99-fact-ledger.md, 01-lesson.md, 03-quiz.md, 04-answer-key.md, 02-flashcards.csv in
DOMAIN_DIR/chapter-NN-SLUG/. The correct option is placed at key_letter and the wrong options fill the
other letters in order; why-wrong lines follow the same letters. Banners, the at-a-glance block and the audit
are separate steps (apply_banner.py, make_glance.py, audit_quiz.py).
"""
import argparse, csv, importlib.util, io, os


def load(path):
    spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def build(m, domain, pdf, prefix):
    N = m.NUM; d = f'{domain}/chapter-{N:02d}-{m.SLUG}'; os.makedirs(d, exist_ok=True); a, z = m.SLIDES
    open(d + '/99-fact-ledger.md', 'w').write(
        f"# Fact Ledger: Chapter {N} ({m.TITLE}), slides {a}-{z}\n\nSource: `{pdf}` (PDF page numbers). Source boundary: **material-only**. "
        "Every fact below is stated on the cited slide; nothing is added from outside. \"img\" marks facts read from a diagram or table image.\n"
        "Format: `[ID] | fact | type | slide`\n\n" + m.LEDGER.strip('\n') + '\n')
    open(d + '/01-lesson.md', 'w').write(
        f"# Chapter {N}: {m.TITLE}\n\n**Source:** `{pdf}`, slides {a}-{z}. Facts are the same as in [99-fact-ledger.md](99-fact-ledger.md); "
        f"IDs like [{prefix}{N:02d}-006] point to the ledger entry.\n\n" + m.LESSON.strip('\n') + '\n')
    Q = []
    for diff, stem, corr, wrong, key, src, fact, whys, hint in m.QUIZ:
        assert len(wrong) == 3 and len(whys) == 3 and key in 'ABCD' and diff in ('Medium', 'Hard'), stem[:40]
        opts = {key: corr}; wd = {}
        for L, t, w in zip([x for x in 'ABCD' if x != key], wrong, whys): opts[L] = t; wd[L] = w
        Q.append((diff, stem, opts, key, src, fact, wd, hint))
    ex = ' '.join(f'{i + 1}{q[3]}' for i, q in enumerate(Q[:3]))
    quiz = (f"# Chapter {N} Quiz: {m.TITLE}\n\n{len(Q)} questions. Answer in chat as e.g. `{ex} ...`, or mark `skip`. Hints are available on request. "
            "The key is in `04-answer-key.md`; open it only after you answer.\n\n---\n")
    key = (f"# Chapter {N} Answer Key (open after answering)\n\nLedger IDs refer to `99-fact-ledger.md`. Every key traces to a ledger entry and slide; "
           "every distractor is wrong per the lecture; no question needs outside knowledge.\n\n| Q | Key | Difficulty | Source |\n|---|---|---|---|\n")
    expl = ''
    for i, (diff, stem, opts, k, src, fact, wd, hint) in enumerate(Q, 1):
        quiz += f"\n**Q{i} ({diff}).** {stem}\n\n" + '\n'.join(f'- {L}. {opts[L]}' for L in 'ABCD') + '\n\n---\n'
        key += f'| {i} | **{k}** | {diff} | {src} |\n'
        expl += f"\n**Q{i}: {k}.** {fact}\n" + ''.join(f'- {x}: {wd[x]}\n' for x in 'ABCD' if x != k) + f'- Hint: {hint}\n'
    open(d + '/03-quiz.md', 'w').write(quiz); open(d + '/04-answer-key.md', 'w').write(key + '\n---\n' + expl)
    buf = io.StringIO(); w = csv.writer(buf, quoting=csv.QUOTE_ALL, lineterminator='\n'); w.writerow(['question', 'answer'])
    for q, ans in m.CARDS: w.writerow([q, ans])
    open(d + '/02-flashcards.csv', 'w').write(buf.getvalue())
    print(d, 'Q', len(Q), 'cards', len(m.CARDS), 'keys', ''.join(q[3] for q in Q))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('domain'); ap.add_argument('specs', nargs='+')
    ap.add_argument('--pdf', required=True); ap.add_argument('--id-prefix', default='X')
    a = ap.parse_args()
    for s in a.specs: build(load(s), a.domain.rstrip('/'), a.pdf, a.id_prefix)
