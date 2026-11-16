#!/usr/bin/env python3
"""Migrate a bundle from the old two-file layout (visual summary + lesson) to ONE lesson file.

Usage: merge_summary.py COURSE_ROOT [--dry-run]

Old chapter folder: 01-visual-summary.md, 02-lesson.md, 03-flashcards.csv, 04-quiz.md, 05-answer-key.md, 06-review.md
New chapter folder: 01-lesson.md (at-a-glance block + explanation), 02-flashcards.csv, 03-quiz.md,
                    04-answer-key.md, 05-review.md, 99-fact-ledger.md
Steps per chapter: rename the files, run make_glance.py (pictures come from the old summary, traps and
words from the old lesson body), run trim_lesson.py (drops the repeated blocks), delete the old summary.
Then rewrites every reference to the old file names in all markdown files under COURSE_ROOT.
Run apply_banner.py, add_toc.py, audit_quiz.py, check_bundle.py and reading_load.py afterwards.
"""
import argparse, glob, os, re, subprocess, sys
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import _layout

HERE = os.path.dirname(os.path.abspath(__file__))
RENAMES = [('02-lesson.md', '01-lesson.md'), ('03-flashcards.csv', '02-flashcards.csv'), ('04-quiz.md', '03-quiz.md'),
           ('05-answer-key.md', '04-answer-key.md'), ('06-review.md', '05-review.md')]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('root'); ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    chapters = [c + '/' for c in _layout.all_chapters(a.root) if os.path.exists(os.path.join(c, '01-visual-summary.md'))]
    print(f'{len(chapters)} chapters in the old layout')
    if a.dry_run: return
    for ch in chapters:
        seed = ch + '_legacy-summary.md'
        os.rename(ch + '01-visual-summary.md', seed)
        for old, new in RENAMES:
            if os.path.exists(ch + old): os.rename(ch + old, ch + new)
        r = subprocess.run([sys.executable, os.path.join(HERE, 'make_glance.py'), ch, '--seed', seed], capture_output=True, text=True)
        print(r.stdout.strip() or r.stderr.strip()[-300:])
        if r.returncode: sys.exit(f'make_glance failed in {ch}')
        os.remove(seed)
    r = subprocess.run([sys.executable, os.path.join(HERE, 'trim_lesson.py'), a.root], capture_output=True, text=True); print(r.stdout.strip())
    pats = [(re.compile(re.escape(o)), n) for o, n in RENAMES] + [(re.compile(re.escape('01-visual-summary.md')), '01-lesson.md')]
    changed = 0
    for f in glob.glob(os.path.join(a.root, '**', '*.md'), recursive=True):
        if os.sep + 'graphify-out' + os.sep in f: continue
        s = open(f).read(); t = s
        for rx, n in pats: t = rx.sub(n, t)
        t = t.replace('02-flashcards', '02-flashcards')
        if t != s: open(f, 'w').write(t); changed += 1
    print(f'rewrote references in {changed} markdown files')


if __name__ == '__main__':
    main()
