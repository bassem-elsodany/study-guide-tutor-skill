#!/usr/bin/env python3
"""Remove the repeated blocks from a lesson so each fact is stated once.

Usage: trim_lesson.py ROOT_OR_CHAPTER [--dry-run]

Student-persona reviews found the same sentence up to five times in one chapter. This keeps the
"At a glance" block (made by make_glance.py) and the explanation, and removes from the explanation:
  * "**In one sentence:**" and "**One-line summary:**" lines
  * "> **Exam trap:**" quotes (the traps table in the glance block holds them)
  * the sections "Side-by-side recap", "Chapter summary", "How to read this chapter", "Glossary"
    (the glance block's "Words used" table holds the definitions)
  * ledger tags such as [L04-001] or [L04-001 to L04-008] (they stay in the ledger and the keys)
It refuses to touch a lesson whose glance block has no traps/words table while the body still has
trap quotes or a glossary: run make_glance.py first so nothing is lost.
Idempotent. Re-run make_glance.py, add_toc.py and check_bundle.py afterwards.
"""
import argparse, glob, os, re, sys

REGION = re.compile(r'<!-- glance -->.*?<!-- /glance -->\n*', re.S)
DROP_SECTIONS = ('side-by-side recap', 'chapter summary', 'how to read this chapter', 'glossary')


def trim(text):
    if '<!-- glance -->\n<!-- authored -->' in text: return text
    m = REGION.search(text)
    region = m.group(0) if m else ''
    body = text.replace(region, '@@GLANCE@@\n') if m else text
    has_trap_quotes = bool(re.search(r'^> \*\*Exam traps?:', body, re.M))
    has_glossary = bool(re.search(r'^## Glossary', body, re.M))
    if (has_trap_quotes and '### Traps to avoid' not in region) or (has_glossary and '### Words used' not in region):
        return None
    out, skip, fence = [], False, False
    lines = body.split('\n'); i = 0
    while i < len(lines):
        l = lines[i]
        if l.startswith('```'): fence = not fence
        if not fence and l.startswith('## '):
            skip = l[3:].strip().lower().startswith(DROP_SECTIONS)
        if skip: i += 1; continue
        if not fence and re.match(r'^\*\*(In one sentence|One-line summary):\*\*', l): i += 1; continue
        if not fence and re.match(r'^> \*\*Exam traps?:', l):
            while i < len(lines) and lines[i].startswith('>'): i += 1
            continue
        out.append(re.sub(r'\s*\[[A-Z]+\d+-\d+(?: (?:to|and) [A-Z]+\d+-\d+)?(?:, [A-Z]+\d+-\d+)*\]', '', l))
        i += 1
    t = '\n'.join(out).replace('@@GLANCE@@\n', region)
    return re.sub(r'\n{3,}', '\n\n', t).rstrip('\n') + '\n'


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('root'); ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    files = sorted(glob.glob(os.path.join(a.root, '**', '01-lesson.md'), recursive=True)) or [os.path.join(a.root, '01-lesson.md')]
    changed = refused = 0
    for f in files:
        s = open(f).read(); t = trim(s)
        if t is None:
            print('REFUSED (run make_glance.py first):', f); refused += 1; continue
        if t != s:
            changed += 1
            if not a.dry_run: open(f, 'w').write(t)
    print(f'{"would trim" if a.dry_run else "trimmed"} {changed} lessons; {refused} refused')
    sys.exit(1 if refused else 0)


if __name__ == '__main__':
    main()
