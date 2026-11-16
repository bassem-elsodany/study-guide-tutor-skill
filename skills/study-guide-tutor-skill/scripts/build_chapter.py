#!/usr/bin/env python3
"""Assemble a chapter's files from one spec module, so formats never drift.

Usage: build_chapter.py UNIT_DIR SPEC.py [SPEC.py ...] --source assets/course-notes.pdf --id-prefix C [--unit-word slide] [--block-word chapter]

A spec is a Python file defining:
  NUM, SLUG, TITLE, RANGE=(first, last)   (SLIDES is accepted as an older name for RANGE; the range is in the source's own
  units: slides, pages, sections, segments ...)
  LEDGER   markdown body: numbered sections ("## 1. Name (slides)"), entries "- [C02-001] | fact | type | slide",
           then "## Flags on the material (do not quiz on these)"
  LESSON   markdown body after the Source line: "**How to read this chapter:**", numbered sections ("## 1. ..."),
           side-by-side recap, glossary, chapter summary, "## Next"
  QUIZ     list of tuples (difficulty, stem, correct_option, [3 wrong options], key_letter, source,
           fact_line, [3 why-wrong lines in the order of the wrong options], hint)
  CARDS    list of (question, answer)
Writes 99-fact-ledger.md, 01-lesson.md, 03-quiz.md, 04-answer-key.md, 02-flashcards.csv in
UNIT_DIR/<block>-NN-SLUG/ (block word: chapter by default; --block-word lecture, week ...). The correct option is placed at key_letter and the wrong options fill the
other letters in order; why-wrong lines follow the same letters. Banners, the at-a-glance block and the audit
are separate steps (apply_banner.py, make_glance.py, audit_quiz.py).
"""
import argparse, csv, importlib.util, io, os


def load(path):
    spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def build(m, unit, pdf, prefix, word='slide', block='chapter'):
    N = m.NUM; d = f'{unit}/{block}-{N:02d}-{m.SLUG}'; os.makedirs(d, exist_ok=True); a, z = getattr(m, 'RANGE', None) or m.SLIDES
    B, W = block.capitalize(), word
    open(d + '/99-fact-ledger.md', 'w').write(
        f"# Fact Ledger: {B} {N} ({m.TITLE}), {W}s {a}-{z}\n\nSource: `{pdf}` ({W} numbers as in the source). Source boundary: **material-only**. "
        f"Every fact below is stated on the cited {W}; nothing is added from outside. \"img\" marks facts read from a diagram or table image.\n"
        f"Format: `[ID] | fact | type | {W}`\n\n" + m.LEDGER.strip('\n') + '\n')
    open(d + '/01-lesson.md', 'w').write(
        f"# {B} {N}: {m.TITLE}\n\n**Source:** `{pdf}`, {W}s {a}-{z}. Facts are the same as in [99-fact-ledger.md](99-fact-ledger.md); "
        f"IDs like [{prefix}{N:02d}-006] point to the ledger entry.\n\n" + m.LESSON.strip('\n') + '\n')
    Q = []
    for diff, stem, corr, wrong, key, src, fact, whys, hint in m.QUIZ:
        assert len(wrong) == 3 and len(whys) == 3 and key in 'ABCD' and diff in ('Medium', 'Hard'), stem[:40]
        opts = {key: corr}; wd = {}
        for L, t, w in zip([x for x in 'ABCD' if x != key], wrong, whys): opts[L] = t; wd[L] = w
        Q.append((diff, stem, opts, key, src, fact, wd, hint))
    ex = ' '.join(f'{i + 1}{q[3]}' for i, q in enumerate(Q[:3]))
    quiz = (f"# {B} {N} Quiz: {m.TITLE}\n\n{len(Q)} questions. Answer in chat as e.g. `{ex} ...`, or mark `skip`. Hints are available on request. "
            "The key is in `04-answer-key.md`; open it only after you answer.\n\n---\n")
    key = (f"# {B} {N} Answer Key (open after answering)\n\nLedger IDs refer to `99-fact-ledger.md`. Every key traces to a ledger entry and its source {W}; "
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
    ap = argparse.ArgumentParser(); ap.add_argument('unit'); ap.add_argument('specs', nargs='+')
    ap.add_argument('--source', '--pdf', dest='source', required=True, help='the source file the ledger cites (--pdf is the older name)')
    ap.add_argument('--id-prefix', default='X'); ap.add_argument('--unit-word', default='slide', help='what the source numbers its units: slide, page, section, segment ...')
    ap.add_argument('--block-word', default='chapter', help='folder and title word for a teaching block: chapter, lecture, week ...')
    a = ap.parse_args()
    for s in a.specs: build(load(s), a.unit.rstrip('/'), a.source, a.id_prefix, a.unit_word, a.block_word)
