#!/usr/bin/env python3
"""Fail a lesson that dumps the source (slides, pages, notes) instead of teaching it.

Usage: check_dump.py ROOT_OR_LESSON [--source CACHE.txt] [--max-overlap 0.45] [--max-sentence-cells 0.35]

For every numbered section ("## N. ...") of a 01-lesson.md it measures
  overlap   share of the section's 6-word shingles that also occur in the source text (the chapter's
            99-fact-ledger.md by default, or --source with the extracted source text). A section that is
            mostly the source's own wording is a dump.
  sentence cells   share of the section's words that sit in table cells or list items of 14+ words
            (source sentences pasted into a table are still a dump).
  teaching  at least one of: a Predict check (<details>), an analogy ("my analogy"), a link or story
            marker ("my link", "my story", "my example", "my scenario"), a question-style heading or a
            "The problem" opening, and at least 25 words of explanatory prose (not table or list).
A section FAILS when overlap or sentence cells exceed the limits, or when it has no teaching element,
or has too little prose. Exact figures and lists are expected to overlap a little; the limits leave room
for them. Exit code 1 if any section fails. This is a gate: a lesson that fails is rewritten, not shipped.
"""
import argparse, glob, os, re, sys
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import _layout


def norm(t):
    t = re.sub(r'<[^>]+>|`|\*\*|\*|\||#+ ', ' ', t.lower())
    return re.findall(r"[a-z0-9][a-z0-9'%.-]*", t)


def shingles(words, n=6):
    return {tuple(words[i:i + n]) for i in range(max(0, len(words) - n + 1))}


def sections(text):
    text = re.sub(r'<!-- glance -->.*?<!-- /glance -->', '', text, flags=re.S)
    parts = re.split(r'(?m)^## (\d+\. .+)$', text)
    return [(parts[i], parts[i + 1]) for i in range(1, len(parts) - 1, 2)]


def analyse(body, src_sh, a, L=None):
    L = L or _layout.DEFAULT_LABELS
    lines = [l for l in body.split('\n')]
    prose, cells_long, cells_all, details = 0, 0, 0, 0
    for l in lines:
        s = l.strip()
        if not s or s.startswith(('```', '<!--', '---')): continue
        if s.startswith('<details') or s.startswith('<summary'): details += 1
        if s.startswith('|') and not re.match(r'^\|[-: |]+\|$', s):
            for c in s.strip('|').split('|'):
                w = len(norm(c)); cells_all += w
                if w >= 14: cells_long += w
        elif re.match(r'^\s*(?:[-*]|\d+\.)\s', l):
            w = len(norm(s)); cells_all += w
            if w >= 14: cells_long += w
        elif not s.startswith(('<', '>')) or s.startswith('> '):
            prose += len(norm(s))
    words = norm(body); sh = shingles(words)
    overlap = (len(sh & src_sh) / len(sh)) if sh else 0
    total = max(1, prose + cells_all)
    low = body.lower()
    teaching = [k for k, v in (('predict', (L['predict'].lower() + ':') in low), ('analogy', L['analogy'].lower() in low),
                               ('link/story', any(L[k].lower() in low for k in ('link', 'story', 'example', 'scenario', 'picture')))) if v]
    return overlap, cells_long / total, prose, teaching


def check(lesson, a):
    L = _layout.labels(lesson)
    ch = os.path.dirname(lesson)
    srcp = a.source or os.path.join(ch, '99-fact-ledger.md')
    src = open(srcp).read() if os.path.exists(srcp) else ''
    src = re.sub(r'(?m)^> .*$|<!--.*?-->', '', src)
    src_sh = shingles(norm(src))
    bad = 0
    for head, body in sections(open(lesson).read()):
        ov, sc, prose, teaching = analyse(body, src_sh, a, L)
        qhead = '?' in head or '\u061f' in head
        why = []
        if ov > a.max_overlap: why.append(f'{ov:.0%} of its wording is the source (max {a.max_overlap:.0%})')
        if sc > a.max_sentence_cells: why.append(f'{sc:.0%} is source sentences in tables/lists (max {a.max_sentence_cells:.0%})')
        if not teaching and not qhead: why.append('no Predict, analogy, story or link')
        if prose < 25: why.append(f'only {prose} words of explanation')
        if why:
            bad += 1; print(f'DUMP  {os.path.relpath(lesson)}  "{head[:60]}": ' + '; '.join(why))
    return bad


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('target'); ap.add_argument('--source')
    ap.add_argument('--max-overlap', type=float, default=0.45); ap.add_argument('--max-sentence-cells', type=float, default=0.35)
    a = ap.parse_args()
    files = [a.target] if a.target.endswith('.md') else sorted(glob.glob(os.path.join(a.target, '**', '01-lesson.md'), recursive=True))
    bad = sum(check(f, a) for f in files)
    print(f'RESULT: {"FAIL" if bad else "OK"} ({bad} dump sections in {len(files)} lessons)')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
