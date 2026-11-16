#!/usr/bin/env python3
"""Extract the source material ONCE into a text cache, then read slices of it (saves tokens and time).

Usage:
  source_text.py extract SOURCE.pdf [--out assets/SOURCE.slides.txt]   extract per-slide text (one line per slide)
  source_text.py slice   SOURCE.slides.txt START END                    print slides START..END only
  source_text.py check   ASSETS_DIR                                     is every cache fresh? (hash of the PDF)
  source_text.py index   SOURCE.slides.txt                              slide count, image-only candidates

Cache format: one line per slide, `[N] first line | next line | ...`; pages with no text layer are written
as `[N] [NO TEXT: read this slide as an image once and transcribe it here]`. A `sources.json` beside the
caches records, per source: sha256 of the original, slide count, extraction method and the slides that
need a visual read. Agents read the cache (or the fact ledger) instead of the original file; they open the
original only when `check` reports a changed hash or when a slide is image-only.
Extraction tries `pdftotext`, then the Python modules pypdf, PyPDF2, fitz (PyMuPDF). If none exists it
says so; install one (for example `pip install pypdf`) and re-run.
"""
import argparse, hashlib, importlib.util, json, os, re, shutil, subprocess, sys


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()


def pages_of(pdf):
    if shutil.which('pdftotext'):
        out = subprocess.run(['pdftotext', '-layout', pdf, '-'], capture_output=True, text=True).stdout
        return out.split('\f')[:-1] if out.endswith('\f') else out.split('\f'), 'pdftotext'
    for mod in ('pypdf', 'PyPDF2'):
        if importlib.util.find_spec(mod):
            m = __import__(mod); r = m.PdfReader(pdf)
            return [(p.extract_text() or '') for p in r.pages], mod
    if importlib.util.find_spec('fitz'):
        import fitz
        return [p.get_text() for p in fitz.open(pdf)], 'fitz'
    sys.exit('No PDF text extractor found. Install poppler (pdftotext) or `pip install pypdf`, then re-run.')


def one_line(t):
    parts = [re.sub(r'\s+', ' ', l).strip() for l in t.split('\n')]
    return ' | '.join(p for p in parts if p)


def cmd_extract(a):
    pages, method = pages_of(a.pdf)
    out = a.out or os.path.splitext(a.pdf)[0] + '.slides.txt'
    lines, empty = [], []
    for i, t in enumerate(pages, 1):
        s = one_line(t)
        if len(s) < 12:
            empty.append(i); s = '[NO TEXT: read this slide as an image once and transcribe it here]'
        lines.append(f'[{i}] {s}')
    open(out, 'w').write('\n'.join(lines) + '\n')
    mp = os.path.join(os.path.dirname(os.path.abspath(out)), 'sources.json')
    man = json.load(open(mp)) if os.path.exists(mp) else {}
    man[os.path.basename(a.pdf)] = {'sha256': sha(a.pdf), 'slides': len(pages), 'cache': os.path.basename(out),
                                    'method': method, 'needs_visual_read': empty}
    json.dump(man, open(mp, 'w'), indent=2)
    print(f'{a.pdf}: {len(pages)} slides -> {out} ({method}); {len(empty)} slides without text')


def cmd_slice(a):
    for l in open(a.cache):
        m = re.match(r'\[(\d+)\] ', l)
        if m and a.start <= int(m.group(1)) <= a.end: print(l.rstrip('\n'))


def cmd_check(a):
    mp = os.path.join(a.dir, 'sources.json')
    if not os.path.exists(mp): sys.exit('no sources.json: run `extract` on each source first')
    man = json.load(open(mp)); bad = 0
    for pdf, info in man.items():
        p = os.path.join(a.dir, pdf)
        if not os.path.exists(p): print('MISSING ', pdf); bad += 1
        elif sha(p) != info['sha256']: print('CHANGED ', pdf, '(re-run extract, then rebuild what depends on it)'); bad += 1
        elif not os.path.exists(os.path.join(a.dir, info['cache'])): print('NO CACHE', pdf); bad += 1
        else: print('fresh   ', pdf, f"({info['slides']} slides, {len(info['needs_visual_read'])} need a visual read)")
    sys.exit(1 if bad else 0)


def cmd_index(a):
    n = empty = 0
    for l in open(a.cache):
        if re.match(r'\[\d+\] ', l):
            n += 1; empty += '[NO TEXT' in l
    print(f'{n} slides, {empty} without text')


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
    e = sp.add_parser('extract'); e.add_argument('pdf'); e.add_argument('--out'); e.set_defaults(f=cmd_extract)
    s = sp.add_parser('slice'); s.add_argument('cache'); s.add_argument('start', type=int); s.add_argument('end', type=int); s.set_defaults(f=cmd_slice)
    c = sp.add_parser('check'); c.add_argument('dir'); c.set_defaults(f=cmd_check)
    i = sp.add_parser('index'); i.add_argument('cache'); i.set_defaults(f=cmd_index)
    a = ap.parse_args(); a.f(a)


if __name__ == '__main__':
    main()
