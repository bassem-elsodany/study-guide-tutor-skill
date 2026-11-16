#!/usr/bin/env python3
"""Build the "At a glance" block at the top of a chapter's 01-lesson.md (one file, not two).

Usage:
  make_glance.py CHAPTER_DIR [--spec spec.json] [--seed legacy-summary.md] [--chapter-map] [--keep-lists] [--no-validate]

A chapter is ONE lesson file. Its top block, between <!-- glance --> and <!-- /glance -->, is the
part a student reads first (about 3-4 minutes) and must be enough to pass the chapter quiz:
  Picture N   Mermaid diagrams for real flows, hierarchies and decisions; tables for plain lists
  Key facts   every card of 02-flashcards.csv as a question/answer table (the exam lists)
  Traps       the confusable pairs and why each one fools people (written as the CLOSING section of the lesson, before '## Next', not in the top block)
  Words       plain-word definitions of every term the chapter uses before explaining it
Everything below the block is the optional full explanation. A block that starts with `<!-- authored -->` on the line after `<!-- glance -->` was written as a taught lesson (see references/teaching-design.md) and is never regenerated. The block is rewritten in place on
every run; the lesson text outside it is never touched.
Sources, in order of precedence
  pictures : --spec (json {"diagrams": [{title, caption, code}]}), else the block already in the
             lesson, else --seed (a legacy 01-visual-summary.md being merged in).
  traps    : the block already in the lesson, else legacy "> **Exam trap:**" lines in the lesson body.
  words    : the block already in the lesson, else the lesson's legacy "## Glossary" table.
The auto "Chapter map" is OFF unless --chapter-map is given (reviewers found it repeated the rest
and its labels were truncated). A diagram that is only boxes (no arrows, or invisible ~~~ links) is a
list in disguise and becomes a table unless --keep-lists is given. Every Mermaid block is validated
with mermaid-cli (mmdc) when available. The stated reading time is computed (200 words/min + 20 s
per diagram), never promised.
"""
import argparse, csv, json, os, re, shutil, subprocess, sys, tempfile

CLASSDEF = ("  classDef root fill:#1f3a5f,stroke:#1f3a5f,color:#ffffff;\n"
            "  classDef sec fill:#e8f1ff,stroke:#3b6fd4,color:#111111;\n"
            "  classDef sum fill:#fff7e0,stroke:#d4a017,color:#111111;\n")
REGION = re.compile(r'<!-- glance -->.*?<!-- /glance -->\n*', re.S)


def clean(t):
    t = re.sub(r'\s*\[[A-Z]+\d+-\d+[^\]]*\]', '', t)
    t = re.sub(r'\*\*|\*|`', '', t)
    return re.sub(r'\s+', ' ', t).strip()


def cell(t):
    return re.sub(r'\s+', ' ', t.replace('|', '/')).strip()


def esc(t, n=95):
    t = clean(t).replace('"', "'")
    if len(t) > n:
        t = t[:n].rsplit(' ', 1)[0] + '...'
    words, lines, cur = t.split(' '), [], ''
    for w in words:
        if len(cur) + len(w) + 1 > 32 and cur:
            lines.append(cur); cur = w
        else:
            cur = (cur + ' ' + w).strip()
    lines.append(cur)
    return '<br/>'.join(lines)


def split_headings(text, level):
    """[(heading, body)] split on headings of exactly `level` '#', ignoring fenced code."""
    mark = '#' * level + ' '
    out, cur, fence = [], None, False
    for line in text.split('\n'):
        if line.startswith('```'): fence = not fence
        if not fence and line.startswith(mark):
            cur = [line[len(mark):].strip(), []]; out.append(cur)
        elif cur is not None:
            cur[1].append(line)
    return [(h, '\n'.join(b).strip('\n')) for h, b in out]


def rows_of(body, header):
    return [tuple(c.strip() for c in l.strip().strip('|').split(' | ', 1)) for l in body.split('\n')
            if l.startswith('| ') and not l.startswith('| ' + header) and not l.startswith('|---')]


def visual_from(title, body):
    fm = re.search(r'```mermaid\n(.*?)\n```', body, re.S)
    cap = re.findall(r'^\*(.+)\*\s*$', body, re.M)
    if fm: return {'title': title, 'caption': cap[-1] if cap else '', 'code': fm.group(1)}
    tbl = '\n'.join(l for l in body.split('\n') if l.startswith('|'))
    return {'title': title, 'caption': cap[-1] if cap else '', 'raw': tbl}


def parse_region(text):
    """visuals, traps, words from an existing glance block (H3 sub-headings)."""
    m = REGION.search(text)
    if not m: return None
    visuals, traps, words = [], None, None
    for head, body in split_headings(m.group(0), 3):
        low = head.lower()
        pm = re.match(r'^picture \d+: (.+)$', head, re.I)
        if pm: visuals.append(visual_from(pm.group(1), body))
        elif low.startswith('traps'): traps = rows_of(body, 'Trap') or [(l[2:].strip(), '') for l in body.split('\n') if l.startswith('- ')]
        elif low.startswith('words'): words = rows_of(body, 'Term')
    return visuals, traps, words


def parse_seed(path):
    """visuals from a legacy 01-visual-summary.md ('## N. Title' blocks)."""
    vis = []
    for head, body in split_headings(open(path).read(), 2):
        m = re.match(r'^\d+\. (.+)$', head)
        if m and m.group(1).lower() != 'chapter map': vis.append(visual_from(m.group(1), body))
    return vis


def parse_lesson_legacy(text):
    secs = []
    for m in re.finditer(r'^## (\d+)\. (.+)$', text, re.M):
        start = m.end(); nxt = re.search(r'^## ', text[start:], re.M)
        body = text[start:start + nxt.start()] if nxt else text[start:]
        one = re.search(r'\*\*In one sentence:\*\* (.+)', body)
        summ = re.search(r'\*\*One-line summary:\*\* (.+)', body)
        secs.append((m.group(1), m.group(2), clean(one.group(1)) if one else '', clean(summ.group(1)) if summ else ''))
    traps = []
    lines = text.split('\n'); i = 0
    while i < len(lines):
        m = re.match(r'^> \*\*Exam traps?:\*\*\s*(.*)$', lines[i])
        if m:
            parts = [m.group(1)] if m.group(1) else []; i += 1
            while i < len(lines) and lines[i].startswith('>'):
                parts.append(re.sub(r'^>\s*(?:[-*]\s+)?', '', lines[i])); i += 1
            blob = clean(' '.join(p for p in parts if p))
            w = re.search(r'Why (?:it|they) fool[s]? people:\s*(.+)$', blob)
            if w: traps.append((blob[:w.start()].strip(), w.group(1).strip()))
            else:
                for p in parts:
                    if clean(p): traps.append((clean(p), ''))
            continue
        i += 1
    words = None
    for head, body in split_headings(text, 2):
        if head.lower().startswith('glossary'): words = rows_of(body, 'Term')
    return secs, traps or None, words


def flashcards(ch):
    p = os.path.join(ch, '02-flashcards.csv')
    if not os.path.exists(p): return []
    rows = list(csv.reader(open(p)))
    return [r[:2] for r in rows[1:] if len(r) >= 2]


def auto_map(title, secs):
    out = ['flowchart TD', f'  C["{esc(title, 70)}"]:::root']
    for i, (num, name, one, summ) in enumerate(secs, 1):
        out.append(f'  S{i}["{num}. {esc(name, 60)}"]:::sec')
        out.append(f'  C --> S{i}')
        text = summ or one
        if text:
            out.append(f'  T{i}["{esc(text, 110)}"]:::sum')
            out.append(f'  S{i} --> T{i}')
    out.append(CLASSDEF.rstrip('\n'))
    return '\n'.join(out)


def list_as_table(code):
    """If the diagram is only boxes (no real arrows), return a markdown table, else None."""
    body = [l for l in code.split('\n') if not l.strip().startswith('classDef')]
    if any(re.search(r'-->|-\.->|==>|--[a-z]', l) for l in body): return None
    nodes = re.findall(r'^\s*\w+\["(.+?)"\](?::::\w+)?\s*$', '\n'.join(body), re.M)
    if len(nodes) < 2: return None
    rows = []
    for n in nodes:
        parts = [re.sub(r'</?b>', '', p).strip() for p in n.split('<br/>')]
        rows.append((parts[0], '; '.join(p for p in parts[1:] if p)))
    t = ['| Item | What to know |', '|---|---|']
    t += [f'| **{cell(a)}** | {cell(b)} |' for a, b in rows]
    return '\n'.join(t)


def validate(code):
    mmdc = shutil.which('mmdc')
    if not mmdc: return True, 'mmdc not found, not validated'
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, 'd.mmd'); dst = os.path.join(d, 'd.svg')
        open(src, 'w').write(code)
        cfg = os.path.join(d, 'p.json'); open(cfg, 'w').write('{"args": ["--no-sandbox"]}')
        r = subprocess.run([mmdc, '-i', src, '-o', dst, '-p', cfg, '-q'], capture_output=True, text=True, timeout=120)
        return (r.returncode == 0 and os.path.exists(dst)), (r.stderr or r.stdout)[-400:]


def insert_point(lines):
    """index of the first '## ' heading that is not the table of contents (and not our block)."""
    in_toc = in_glance = False
    for i, l in enumerate(lines):
        if '<!-- toc -->' in l: in_toc = True
        if '<!-- /toc -->' in l: in_toc = False; continue
        if '<!-- glance -->' in l: in_glance = True
        if '<!-- /glance -->' in l: in_glance = False; continue
        if not in_toc and not in_glance and l.startswith('## '): return i
    return len(lines)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('chapter'); ap.add_argument('--spec'); ap.add_argument('--seed')
    ap.add_argument('--chapter-map', action='store_true'); ap.add_argument('--keep-lists', action='store_true')
    ap.add_argument('--no-validate', action='store_true')
    a = ap.parse_args(); ch = a.chapter.rstrip('/')
    lp = next((os.path.join(ch, n) for n in ('01-lesson.md', 'lesson.md') if os.path.exists(os.path.join(ch, n))), None)
    if not lp: sys.exit('no lesson file in ' + ch)
    text = open(lp).read()
    if '<!-- glance -->\n<!-- authored -->' in text:
        print('authored block, left alone:', lp); return
    title = re.search(r'^# (.+)$', text, re.M).group(1)
    region = parse_region(text)
    secs, l_traps, l_words = parse_lesson_legacy(REGION.sub('', text))
    r_vis, r_traps, r_words = region if region else ([], None, None)
    closing = re.search(r'<!-- traps -->\n## Traps to avoid\n(.*?)<!-- /traps -->', text, re.S)
    c_traps = (rows_of(closing.group(1), 'Trap') or None) if closing else None
    traps = c_traps or r_traps or l_traps or []; words = r_words or l_words or []
    if a.spec: visuals = json.load(open(a.spec))['diagrams']
    elif r_vis: visuals = r_vis
    elif a.seed: visuals = parse_seed(a.seed)
    else: visuals = []
    if a.chapter_map:
        visuals = list(visuals) + [{'title': 'Chapter map', 'caption': 'Sections and the one thing to remember from each.', 'code': auto_map(title, secs)}]
    final = []
    for d in visuals:
        if 'code' in d and not a.keep_lists:
            t = list_as_table(d['code'])
            if t: d = {'title': d['title'], 'caption': d.get('caption', ''), 'raw': t}
        if 'code' in d and not a.no_validate:
            ok, msg = validate(d['code'])
            if not ok: sys.exit(f"Mermaid error in '{d['title']}' of {ch}:\n{msg}\n{d['code']}")
        final.append(d)
    cards = flashcards(ch)
    md = ['@@HEAD@@', '']
    for n, d in enumerate(final, 1):
        md += [f"### Picture {n}: {d['title']}", '']
        md += (['```mermaid', d['code'].strip('\n'), '```'] if 'code' in d else [d['raw']])
        if d.get('caption'): md += ['', f"*{d['caption'].strip('*')}*"]
        md.append('')
    if cards:
        md += ['### Key facts (what the exam asks)', '', '| Question | Answer |', '|---|---|']
        md += [f'| {cell(q)} | {cell(an)} |' for q, an in cards] + ['']
    if words:
        md += ['### Words used in this chapter', '', '| Term | Plain words |', '|---|---|']
        md += [f'| {cell(t)} | {cell(w)} |' for t, w in words] + ['']
    md += ['> **Everything below is the full explanation.** Read it only where something above is unclear; the quiz is next: [03-quiz.md](03-quiz.md).', '']
    body = '\n'.join(md)
    n_words = len(re.sub(r'```mermaid.*?```', '', body, flags=re.S).split())
    diagrams = sum(1 for d in final if 'code' in d)
    minutes = n_words / 200 + diagrams * 20 / 60
    m = max(1, round(minutes)); head = f'## At a glance (read this first, about {m} minute{"" if m == 1 else "s"})'
    block = '<!-- glance -->\n' + body.replace('@@HEAD@@', head).rstrip('\n') + '\n<!-- /glance -->\n'
    text = REGION.sub('', text)
    lines = text.split('\n'); i = insert_point(lines)
    new = '\n'.join(lines[:i]).rstrip('\n') + '\n\n' + block + '\n' + '\n'.join(lines[i:])
    new = re.sub(r'<!-- traps -->.*?<!-- /traps -->\n*', '', new, flags=re.S)
    if traps:
        rows = ('| Trap | Why it fools people |\n|---|---|\n' + '\n'.join(f'| {cell(t)} | {cell(w)} |' for t, w in traps)
                if any(w for _, w in traps) else '\n'.join(f'- {cell(t)}' for t, _ in traps))
        sec = ('<!-- traps -->\n## Traps to avoid\n\nThe last warning before the quiz. Each row is a mix-up the exam is built on.\n\n'
               + rows + '\n<!-- /traps -->\n\n')
        nx = re.search(r'(?m)^## Next\s*$', new) or re.search(r'(?m)^<!-- audience-banner:end -->', new)
        new = (new[:nx.start()] + sec + new[nx.start():]) if nx else new.rstrip('\n') + '\n\n' + sec
    open(lp, 'w').write(re.sub(r'\n{3,}', '\n\n', new))
    print('wrote glance in', lp, f'({diagrams} diagrams, {len(final) - diagrams} tables, {len(cards)} facts, {len(traps)} traps, {len(words)} words, ~{minutes:.1f} min)')


if __name__ == '__main__':
    main()
