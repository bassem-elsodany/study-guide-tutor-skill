#!/usr/bin/env python3
"""Add (or refresh) a table of contents in every generated study markdown file.

Usage: add_toc.py ROOT [--check]

Rules
  * Lessons get a nested contents list (## sections and ### sub-sections).
  * Quizzes, answer keys, final quizzes and exams get a "Jump to" line of question links;
    an invisible anchor (<a id="q1"></a>) is placed before each question so the links work.
  * Every other file with two or more ## headings (visual summaries, ledgers, cram sheets, concept
    maps, READMEs) gets a list of its ## sections.
  * Files with fewer than two sections (score tracker, revisit list, flashcards) are exempt.
  * CLAUDE.md and graphify-out/ are skipped.
  * The TOC sits right after the H1 (after a legacy top banner, if a file still has one), between
    <!-- toc --> and <!-- /toc --> markers, so re-running replaces it instead of duplicating it.
  * Headings inside code fences (Mermaid blocks) are ignored. Anchors follow the GitHub slug rule.
--check lists files that should have a TOC but do not (exit code 1) without changing anything.
"""
import argparse, glob, os, re, sys
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import _layout


def slug(text, seen):
    t = re.sub(r'[*`_]', '', text).strip().lower()
    t = re.sub(r'[^\w\- ]', '', t, flags=re.U).replace(' ', '-')
    n = seen.get(t, 0); seen[t] = n + 1
    return t if n == 0 else f'{t}-{n}'


def headings(lines):
    out, fence = [], False
    seen = {}
    for i, l in enumerate(lines):
        if l.startswith('```'):
            fence = not fence; continue
        if fence: continue
        m = re.match(r'^(#{1,3}) (.+?)\s*$', l)
        if m and not (len(m.group(1)) == 1):
            out.append((len(m.group(1)), m.group(2), slug(m.group(2), seen), i))
        elif m:
            slug(m.group(2), seen)
    return out


def display(t):
    t = re.sub(r'\s*\[[A-Z]+\d+-\d+[^\]]*\]', '', t)
    return re.sub(r'[*`]', '', t).strip()


def kind(path):
    n = re.sub(r'^\d+-', '', os.path.basename(path))
    if n in ('quiz.md', 'answer-key.md', 'final-quiz.md', 'final-quiz-key.md', 'domain-exam.md', 'domain-exam-key.md', 'exam.md', 'exam-key.md', 'unit-exam.md', 'unit-exam-key.md') or n.startswith('mock-exam'):
        return 'questions'
    if n == 'lesson.md': return 'lesson'
    return 'sections'


def build(path):
    L = _layout.labels(path)
    s = open(path).read()
    s = re.sub(r'<!-- toc -->.*?<!-- /toc -->\n*', '', s, flags=re.S)
    lines = s.split('\n')
    k = kind(path)
    if k == 'questions':
        nums = []
        out = []
        for l in lines:
            m = re.match(r'^\*\*Q(\d+)[ :(]', l)
            if m:
                nums.append(int(m.group(1)))
                if not (out and out[-1].startswith('<a id="q')):
                    out.append(f'<a id="q{m.group(1)}"></a>')
            out.append(l)
        if len(nums) < 2: return None
        lines = out
        body = L['jump_to'] + ': ' + ' · '.join(f'[Q{n}](#q{n})' for n in nums)
    else:
        hs = [h for h in headings(lines) if h[1].strip().lower() != L['contents'].lower()]
        use = [h for h in hs if h[0] == 2 or (k == 'lesson' and h[0] == 3)]
        if len([h for h in hs if h[0] == 2]) < 2: return None
        body = '\n'.join(('  ' if h[0] == 3 else '') + f'- [{display(h[1])}](#{h[2]})' for h in use)
    block = f'<!-- toc -->\n## {L["contents"]}\n\n{body}\n<!-- /toc -->\n'
    # insertion point: after a legacy top banner if one exists, else after the H1 (the audience note is now a footer)
    top = next((i for i, l in enumerate(lines) if l.strip() == '<!-- audience-banner:top -->'), None)
    idx = next((i for i, l in enumerate(lines) if i > top and l.strip() == '<!-- /audience-banner -->'), None) if top is not None else None
    if idx is None:
        idx = next((i for i, l in enumerate(lines) if l.startswith('# ')), 0)
    new = lines[:idx + 1] + ['', block.rstrip('\n'), ''] + [l for l in lines[idx + 1:]]
    text = '\n'.join(new)
    return re.sub(r'\n{3,}', '\n\n', text)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('root'); ap.add_argument('--check', action='store_true')
    a = ap.parse_args(); changed = missing = 0
    for f in sorted(glob.glob(os.path.join(a.root, '**', '*.md'), recursive=True)):
        if 'graphify-out' in f or os.path.basename(f) == 'CLAUDE.md': continue
        s = open(f).read(); t = build(f)
        if t is None: continue
        has = '<!-- toc -->' in s
        if a.check:
            if not has: print('NO TOC', os.path.relpath(f, a.root)); missing += 1
            continue
        if t != s: open(f, 'w').write(t); changed += 1
    if a.check:
        print('RESULT:', 'FAIL' if missing else 'OK', f'({missing} files without a TOC)'); sys.exit(1 if missing else 0)
    print(f'updated {changed} files')


if __name__ == '__main__':
    main()
