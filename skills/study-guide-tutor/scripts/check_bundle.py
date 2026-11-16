#!/usr/bin/env python3
"""Check that a study bundle is internally consistent.

Usage: check_bundle.py ROOT     (a course folder, or any unit folder; chapters and units are found by their content, not by folder names)

Per chapter folder (for example chapter-NN-slug, lecture-NN-slug, week-N-slug: any name with a number):
  files        01-lesson.md (the at-a-glance block and the explanation are ONE file), 02-flashcards.csv, 03-quiz.md, 04-answer-key.md, 99-fact-ledger.md exist
  headings     the H1 of lesson, quiz, key and ledger carries the folder's chapter number
  ledger IDs   every ledger ID is [<letters><chapter number>-NNN] and every ID cited in the lesson, quiz and key exists
  banners      exactly one audience note, at the END of every markdown file (no top banner)
  mermaid      every lesson has an at-a-glance block (<!-- glance -->) with at least one picture (a ```mermaid block or a table)
  csv          flashcards parse with two columns
  toc          lessons, visual summaries and ledgers have a table of contents
  links        relative markdown links resolve
Exit code 1 if any problem is found.
"""
import csv, glob, os, re, sys
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import _layout

NEEDED = ['01-lesson.md', '02-flashcards.csv', '03-quiz.md', '04-answer-key.md', '99-fact-ledger.md']


def main():
    root = os.path.abspath(sys.argv[1]); bad = []
    bases = [u + '/' for u in _layout.find_units(root)] or [root + '/']
    for b in bases:
        for ch in [x + '/' for x in _layout.chapters_of(b.rstrip('/'))]:
            n = _layout.chapter_number(ch); rel = os.path.relpath(ch, root)
            for f in NEEDED:
                if not os.path.exists(ch + f): bad.append((rel, 'missing', f))
            led = open(ch + '99-fact-ledger.md').read() if os.path.exists(ch + '99-fact-ledger.md') else ''
            have = set(re.findall(r'^- \[([A-Z]+\d+-\d{3})\]', led, re.M))
            for pre in {re.match(r'([A-Z]+)(\d+)', i).groups() for i in have}:
                if int(pre[1]) != n: bad.append((rel, 'ledger id prefix', ''.join(pre)))
            for f in NEEDED:
                p = ch + f
                if not os.path.exists(p) or not f.endswith('.md'): continue
                t = open(p).read()
                h = re.match(r'# (?:' + re.escape(_layout.labels(root)['fact_ledger']) + r': )?(?:[^\W\d_]+[ \t]+)?(\d+)', t)
                if not h or int(h.group(1)) != n: bad.append((rel, f, 'H1 chapter number'))
                if t.count('audience-banner:top') != 0 or t.count('audience-banner:end') != 1: bad.append((rel, f, 'banner count (want exactly one footer note, no top banner)'))
                if f == '01-lesson.md' and '<!-- glance -->' not in t: bad.append((rel, f, 'no at-a-glance block'))
                if f == '01-lesson.md' and '<!-- glance -->' in t and not re.search(r'```mermaid|### Picture \d+', t): bad.append((rel, f, 'at-a-glance block has no picture'))
                if f == '01-lesson.md' and os.path.exists(ch + '01-visual-summary.md'): bad.append((rel, '01-visual-summary.md', 'separate summary file: merge it into 01-lesson.md (merge_summary.py)'))
                if f in ('01-lesson.md', '99-fact-ledger.md') and len(re.findall(r'^## ', t, re.M)) >= 2 and '<!-- toc -->' not in t: bad.append((rel, f, 'no table of contents'))
                if f in ('01-lesson.md', '03-quiz.md', '04-answer-key.md'):
                    t2 = re.sub(r'IDs like \[[^\]]+\]', '', t)
                    for ref in set(re.findall(r'\b([A-Z]+\d+-\d{3})\b', t2)):
                        if ref not in have: bad.append((rel, f, 'cites missing ledger id', ref))
            if os.path.exists(ch + '02-flashcards.csv'):
                for i, r in enumerate(csv.reader(open(ch + '02-flashcards.csv'))):
                    if len(r) != 2: bad.append((rel, '02-flashcards.csv', f'row {i + 1} has {len(r)} columns')); break
    for f in glob.glob(os.path.join(root, '**', '*.md'), recursive=True):
        if 'graphify-out' in f: continue
        for m in re.findall(r'\]\(([^)#\s]+)\)', open(f).read()):
            if m.startswith(('http', 'mailto')): continue
            if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(f), m))):
                bad.append((os.path.relpath(f, root), 'broken link', m))
    for b in bad: print('PROBLEM', *b)
    print('RESULT:', 'FAIL' if bad else 'OK', f'({len(bad)} problems)')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
