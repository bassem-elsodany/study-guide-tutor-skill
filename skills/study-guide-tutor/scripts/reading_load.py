#!/usr/bin/env python3
"""Measure how much a student has to read, per chapter and per domain.

Usage: reading_load.py ROOT [--wpm 200] [--glance-max 5] [--lesson-max 12]

Counts words in 01-lesson.md (Mermaid code, banners and contents blocks excluded), split into the
"At a glance" block (between <!-- glance --> and <!-- /glance -->) and the whole file, converts to minutes
at --wpm (plus 20 s per Mermaid diagram in the glance block), and flags chapters whose glance block takes
more than --glance-max minutes or whose whole lesson takes more than --lesson-max minutes. Prints a table and domain totals. Exit code 1 if any flag.
The point: the bundle exists to save reading time. If a chapter's lesson takes longer than reading its slides,
cut it.
"""
import argparse, glob, os, re, sys


def words_of(s):
    s = re.sub(r'<!-- audience-banner:top -->.*?<!-- /audience-banner -->', '', s, flags=re.S)
    s = re.sub(r'<!-- audience-banner:end -->.*?<!-- /audience-banner -->', '', s, flags=re.S)
    s = re.sub(r'<!-- toc -->.*?<!-- /toc -->', '', s, flags=re.S)
    s = re.sub(r'```mermaid.*?```', '', s, flags=re.S)
    s = re.sub(r'<a id="[^"]*"></a>|<[^>]+>', '', s)
    s = re.sub(r'\|[-: |]+\|', ' ', s)
    return len(re.findall(r"[A-Za-z0-9][\w'/%.-]*", s))


def slides(lesson):
    m = re.search(r'slides (\d+)-(\d+)', open(lesson).read()) if os.path.exists(lesson) else None
    return int(m.group(2)) - int(m.group(1)) + 1 if m else 0


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('root'); ap.add_argument('--wpm', type=int, default=200)
    ap.add_argument('--glance-max', type=float, default=5.0); ap.add_argument('--lesson-max', type=float, default=12.0)
    a = ap.parse_args(); flagged = 0
    root = os.path.abspath(a.root)
    for dom in sorted(glob.glob(os.path.join(root, 'domain-*/'))) or [root + '/']:
        tot_s = tot_l = 0
        print(f'\n{os.path.relpath(dom, root)}\n| Ch | Slides | Glance min | Lesson min | Words per slide | Flag |\n|---|---|---|---|---|---|')
        for ch in sorted(glob.glob(os.path.join(dom, 'chapter-*/'))):
            n = int(os.path.basename(ch.rstrip('/')).split('-')[1])
            txt = open(ch + '01-lesson.md').read() if os.path.exists(ch + '01-lesson.md') else ''
            g = re.search(r'<!-- glance -->.*?<!-- /glance -->', txt, re.S); gt = g.group(0) if g else ''
            ws = words_of(gt) + 0; wl = words_of(txt); sl = slides(ch + '01-lesson.md')
            nd = len(re.findall(r'```mermaid', gt))
            ms, ml = ws / a.wpm + nd / 3, wl / a.wpm + nd / 3; tot_s += ms; tot_l += ml
            flag = []
            if ms > a.glance_max: flag.append('glance block long')
            if ml > a.lesson_max: flag.append('lesson long')
            flagged += bool(flag)
            print(f'| {n} | {sl} | {ms:.1f} | {ml:.1f} | {wl / sl:.0f} | {", ".join(flag)} |' if sl else f'| {n} | ? | {ms:.1f} | {ml:.1f} | | {", ".join(flag)} |')
        print(f'\nDomain totals: at-a-glance blocks {tot_s:.0f} min, lessons {tot_l:.0f} min')
    sys.exit(1 if flagged else 0)


if __name__ == '__main__':
    main()
