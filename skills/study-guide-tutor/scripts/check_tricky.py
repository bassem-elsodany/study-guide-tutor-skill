#!/usr/bin/env python3
"""Gate: every lesson must warn the student, in place, where a confusion happens.

Usage: check_tricky.py ROOT_OR_LESSON [--min 2] [--max 4]

A "Tricky part" callout in the lesson body (below the at-a-glance block) has this exact shape:

    > **⚠ Tricky part: decay or drift?**
    > Both lower accuracy, so they get swapped.
    > **Hint:** ask where the change comes from.

    <details>
    <summary>Rule and anchor</summary>

    **Rule:** decay = old static data; drift = the world moved.
    **Anchor:** a short contrast or real case.
    </details>

Checks per lesson: a closing "## Traps to avoid" section (not in the glance block, before "## Next"); callout count between --min and --max; each callout has a one-line confusion,
a "**Hint:**" line (a test the student can run, not the answer) and, right after it, a
"Rule and anchor" box holding "**Rule:**" and "**Anchor:**"; titles are unique; callouts sit
inside numbered sections, not in the glance block. Exit 1 on any failure.
It cannot judge whether the confusions are the right ones: the student-persona reviewer does that.
"""
import argparse, glob, os, re, sys

HEAD = re.compile(r'^> \*\*⚠ Tricky part:\s*(.+?)\*\*\s*$')


def lessons(root):
    if os.path.isfile(root):
        return [root]
    return sorted(glob.glob(os.path.join(root, '**', '01-lesson.md'), recursive=True))


def check(path, lo, hi):
    text = open(path, encoding='utf-8').read()
    in_glance = re.findall(r'<!-- glance -->.*?<!-- /glance -->', text, flags=re.S)
    for g in in_glance:
        if '⚠ Tricky part' in g:
            return ['callout placed inside the at-a-glance block (it belongs in a numbered section)']
    body = re.sub(r'<!-- glance -->.*?<!-- /glance -->', '', text, flags=re.S)
    lines = body.split('\n')
    errs, titles = [], []
    if '### Traps to avoid' in text:
        errs.append('traps table is inside the at-a-glance block; it belongs in the closing "## Traps to avoid" section before "## Next"')
    elif '<!-- traps -->' not in body or not re.search(r'<!-- traps -->\n## Traps to avoid', body):
        errs.append('no closing "## Traps to avoid" section (between <!-- traps --> markers, before "## Next")')
    else:
        heads = re.findall(r'(?m)^## (Say it back|Traps to avoid|Next)\b', body)
        if 'Next' in heads and heads.index('Traps to avoid') > heads.index('Next'):
            errs.append('"## Traps to avoid" must come before "## Next"')
    idx = [i for i, l in enumerate(lines) if HEAD.match(l)]
    if len(idx) < lo:
        errs.append(f'{len(idx)} callouts, need at least {lo}')
    if len(idx) > hi:
        errs.append(f'{len(idx)} callouts, budget is {hi}: if everything is tricky nothing stands out')
    for i in idx:
        title = HEAD.match(lines[i]).group(1).strip()
        if title in titles:
            errs.append(f'duplicate callout title: {title}')
        titles.append(title)
        block = []
        j = i + 1
        while j < len(lines) and lines[j].startswith('>'):
            block.append(lines[j]); j += 1
        confusion = [b for b in block if not b.startswith('> **Hint:**') and b.strip('> ').strip()]
        if not confusion:
            errs.append(f'"{title}": no one-line confusion statement')
        if not any(b.startswith('> **Hint:**') and len(b) > 20 for b in block):
            errs.append(f'"{title}": missing a "> **Hint:**" line')
        tail = '\n'.join(lines[j:j + 14])
        if not ('<summary>Rule and anchor</summary>' in tail and '**Rule:**' in tail and '**Anchor:**' in tail):
            errs.append(f'"{title}": missing the "Rule and anchor" box with **Rule:** and **Anchor:**')
        # must sit under a numbered section
        prior = [l for l in lines[:i] if l.startswith('## ')]
        if not prior or not re.match(r'## \d+\.', prior[-1]):
            errs.append(f'"{title}": not inside a numbered section')
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root')
    ap.add_argument('--min', type=int, default=2)
    ap.add_argument('--max', type=int, default=4)
    a = ap.parse_args()
    bad = 0
    for p in lessons(a.root):
        errs = check(p, a.min, a.max)
        name = os.path.relpath(p, a.root if os.path.isdir(a.root) else os.path.dirname(a.root))
        if errs:
            bad += 1
            for e in errs:
                print(f'FAIL {name}: {e}')
        else:
            print(f'ok   {name}')
    print('RESULT: OK' if not bad else f'RESULT: {bad} lesson(s) failed')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
