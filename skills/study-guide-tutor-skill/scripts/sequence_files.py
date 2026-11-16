#!/usr/bin/env python3
"""Give every file in a study bundle a number that matches the order a student reads it.

Usage: sequence_files.py COURSE_ROOT [--dry-run]

Chapter folder (reading order):
  01-lesson.md           ONE file: at-a-glance block (diagrams, key facts, traps, words) then the explanation
  02-flashcards.csv      drill
  03-quiz.md             questions only
  04-answer-key.md       open after answering
  05-review.md           created after grading
  99-fact-ledger.md      reference for checking facts, not part of the reading flow
Unit 00-overview folder:
  01-concept-map.md  02-cram-sheet.md  03-final-quiz.md  04-final-quiz-key.md
  05-score-tracker.md  06-revisit-list.md

Renames the files and rewrites every reference to them (links, backticked names, Next lines)
in all markdown files under COURSE_ROOT. Run once; already-numbered files are left alone.
"""
import argparse, glob, os, re
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import _layout

CHAPTER = {'lesson.md': '01-lesson.md', 'flashcards.csv': '02-flashcards.csv', 'quiz.md': '03-quiz.md',
           'answer-key.md': '04-answer-key.md', 'review.md': '05-review.md', 'fact-ledger.md': '99-fact-ledger.md'}
OVERVIEW = {'concept-map.md': '01-concept-map.md', 'cram-sheet.md': '02-cram-sheet.md',
            'final-quiz.md': '03-final-quiz.md', 'final-quiz-key.md': '04-final-quiz-key.md',
            'score-tracker.md': '05-score-tracker.md', 'revisit-list.md': '06-revisit-list.md'}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('root'); ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    renames = {}
    for d in _layout.all_chapters(a.root):
        if os.path.isdir(d):
            for old, new in CHAPTER.items():
                if os.path.exists(os.path.join(d, old)):
                    renames[os.path.join(d, old)] = os.path.join(d, new)
    for d in glob.glob(os.path.join(a.root, '**', '00-overview'), recursive=True):
        for old, new in OVERVIEW.items():
            if os.path.exists(os.path.join(d, old)):
                renames[os.path.join(d, old)] = os.path.join(d, new)
    print(f'{len(renames)} files to rename')
    if a.dry_run:
        return
    for old, new in renames.items():
        os.rename(old, new)
    names = {**CHAPTER, **OVERVIEW}
    pats = [(re.compile(r'(?<![\w.-])' + re.escape(o) + r'(?![\w])'), n)
            for o, n in sorted(names.items(), key=lambda kv: -len(kv[0]))]
    changed = 0
    for f in glob.glob(os.path.join(a.root, '**', '*.md'), recursive=True):
        if os.sep + 'graphify-out' + os.sep in f:
            continue
        s = open(f).read(); t = s
        for rx, n in pats:
            t = rx.sub(n, t)
        if t != s:
            open(f, 'w').write(t); changed += 1
    print(f'rewrote references in {changed} markdown files')


if __name__ == '__main__':
    main()
