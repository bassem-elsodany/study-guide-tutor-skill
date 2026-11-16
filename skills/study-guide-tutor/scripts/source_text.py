#!/usr/bin/env python3
"""Extract the source material ONCE into a text cache, then read slices of it (saves tokens and time).

Usage:
  source_text.py extract SOURCE [--out CACHE] [--unit-word WORD]   extract per-unit text (one line per unit)
  source_text.py slice   CACHE START END                           print units START..END only
  source_text.py check   ASSETS_DIR                                is every cache fresh? (hash of the original)
  source_text.py index   CACHE                                     unit count, image-only candidates

The skill adapts to what the student provides. SOURCE can be:

  .pdf            one unit per page (pdftotext, or pypdf / PyPDF2 / PyMuPDF)          unit word: slide
  .pptx           one unit per slide, speaker notes appended as "Notes: ..."          unit word: slide
  .docx           one unit per section (a heading starts one; else ~350-word chunks)  unit word: section
  .md .txt        one unit per heading section (md) or per ~350-word chunk (txt)       unit word: section
  .html .htm      one unit per <h1>-<h3> section                                       unit word: section
  .epub           one unit per content file, in reading order                          unit word: section
  .srt .vtt       one unit per 2-minute window of a transcript, with its time range    unit word: segment
  image file      one unit, marked "NO TEXT": read it as an image once and transcribe  unit word: page
  folder of images  one unit per image in name order (scanned notes, photographed slides)  unit word: page

Not read directly: spreadsheets, audio and video (transcribe them first; a .srt/.vtt/.txt transcript works).

The unit word (slide, page, section, segment ...) is only the label used when locating a fact; `--unit-word` overrides
it. Cache format: one line per unit, `[N] first line | next line | ...`; a unit with no text is written as
`[N] [NO TEXT: read this unit as an image once and transcribe it here]`. A `sources.json` beside the caches records,
per source: sha256 of the original (a folder is hashed by its files), unit count and word, extraction method and
the units that need a visual read. Agents read the cache (or the fact ledger) instead of the original file; they open
the original only when `check` reports a changed hash or when a unit is image-only.
"""
import argparse, hashlib, html, importlib.util, json, os, re, shutil, subprocess, sys, zipfile

IMAGES = ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.tif', '.tiff', '.bmp')
UNIT_WORD = {'.pdf': 'slide', '.pptx': 'slide', '.docx': 'section', '.md': 'section', '.markdown': 'section',
             '.txt': 'section', '.html': 'section', '.htm': 'section', '.epub': 'section', '.srt': 'segment', '.vtt': 'segment'}
NO_TEXT = '[NO TEXT: read this unit as an image once and transcribe it here]'
CHUNK_WORDS = 350
WINDOW_SECONDS = 120


def sha(path):
    h = hashlib.sha256()
    if os.path.isdir(path):  # a folder of images: hash names and contents in order
        for n in sorted(os.listdir(path)):
            p = os.path.join(path, n)
            if os.path.isfile(p):
                h.update(n.encode()); h.update(sha(p).encode())
        return h.hexdigest()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()


def clean(t):
    return re.sub(r'[ \t\u00a0]+', ' ', html.unescape(t)).strip()


def chunk_words(text, size=CHUNK_WORDS):
    """Split free text into units of about `size` words on paragraph boundaries."""
    paras = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    units, cur, n = [], [], 0
    for p in paras:
        w = len(p.split())
        if cur and n + w > size:
            units.append('\n'.join(cur)); cur, n = [], 0
        cur.append(p); n += w
    if cur: units.append('\n'.join(cur))
    return units


# ---------- readers: each returns (list_of_unit_texts, method) ----------
def pdf_units(pdf):
    if shutil.which('pdftotext'):
        out = subprocess.run(['pdftotext', '-layout', pdf, '-'], capture_output=True, text=True).stdout
        return (out.split('\f')[:-1] if out.endswith('\f') else out.split('\f')), 'pdftotext'
    for mod in ('pypdf', 'PyPDF2'):
        if importlib.util.find_spec(mod):
            m = __import__(mod); r = m.PdfReader(pdf)
            return [(p.extract_text() or '') for p in r.pages], mod
    if importlib.util.find_spec('fitz'):
        import fitz
        return [p.get_text() for p in fitz.open(pdf)], 'fitz'
    sys.exit('No PDF text extractor found. Install poppler (pdftotext) or `pip install pypdf`, then re-run.')


def _xml_paragraphs(xml, para_tag, text_tag):
    out = []
    for p in re.findall(r'<%s[ >].*?</%s>' % (para_tag, para_tag), xml, re.S):
        t = ''.join(re.findall(r'<%s[^>]*>(.*?)</%s>' % (text_tag, text_tag), p, re.S))
        t = clean(re.sub(r'<[^>]+>', '', t))
        if t: out.append((p, t))
    return out


def pptx_units(path):
    z = zipfile.ZipFile(path)
    num = lambda n: int(re.search(r'(\d+)\.xml$', n).group(1))
    slides = sorted((n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', n)), key=num)
    notes = {num(n): n for n in z.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml', n)}
    units = []
    for n in slides:
        text = '\n'.join(t for _, t in _xml_paragraphs(z.read(n).decode('utf8', 'ignore'), 'a:p', 'a:t'))
        k = num(n)
        if k in notes:
            nt = '\n'.join(t for _, t in _xml_paragraphs(z.read(notes[k]).decode('utf8', 'ignore'), 'a:p', 'a:t'))
            if nt: text += '\nNotes: ' + nt
        units.append(text)
    return units, 'pptx-xml'


def docx_units(path):
    xml = zipfile.ZipFile(path).read('word/document.xml').decode('utf8', 'ignore')
    sections, cur, headed = [], [], False
    for raw, t in _xml_paragraphs(xml, 'w:p', 'w:t'):
        if re.search(r'<w:pStyle w:val="(?:Heading[1-3]|Title)"', raw):
            headed = True
            if cur: sections.append('\n'.join(cur)); cur = []
        cur.append(t)
    if cur: sections.append('\n'.join(cur))
    if not headed:
        sections = chunk_words('\n\n'.join(sections))
    return sections, 'docx-xml'


def md_units(path):
    text = open(path, encoding='utf-8', errors='ignore').read()
    parts = re.split(r'(?m)^(?=#{1,3} )', text)
    parts = [p.strip() for p in parts if p.strip()]
    if len(parts) <= 1:
        return chunk_words(text), 'markdown-chunks'
    return parts, 'markdown-headings'


def txt_units(path):
    text = open(path, encoding='utf-8', errors='ignore').read()
    if '\f' in text:
        return [p for p in text.split('\f') if p.strip()], 'text-formfeed'
    return chunk_words(text), 'text-chunks'


def _html_text(fragment):
    fragment = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', fragment)
    fragment = re.sub(r'(?i)<(br|/p|/div|/li|/tr|/h\d)[^>]*>', '\n', fragment)
    return '\n'.join(l for l in (clean(x) for x in re.sub(r'<[^>]+>', ' ', fragment).split('\n')) if l)


def html_units(path, text=None):
    raw = text if text is not None else open(path, encoding='utf-8', errors='ignore').read()
    body = re.search(r'(?is)<body[^>]*>(.*)</body>', raw)
    raw = body.group(1) if body else raw
    parts = [p for p in re.split(r'(?i)(?=<h[1-3][ >])', raw) if _html_text(p)]
    units = [_html_text(p) for p in parts]
    return (units if units else chunk_words(_html_text(raw))), 'html-headings'


def epub_units(path):
    z = zipfile.ZipFile(path)
    names = [n for n in z.namelist() if re.search(r'\.(x?html?)$', n, re.I) and 'nav' not in os.path.basename(n).lower()]
    order = names
    try:  # follow the spine when the package file lists one
        opf = next(n for n in z.namelist() if n.endswith('.opf')); x = z.read(opf).decode('utf8', 'ignore')
        manifest = dict(re.findall(r'<item[^>]*id="([^"]+)"[^>]*href="([^"]+)"', x)) | {i: h for h, i in re.findall(r'<item[^>]*href="([^"]+)"[^>]*id="([^"]+)"', x)}
        base = os.path.dirname(opf)
        spine = [os.path.normpath(os.path.join(base, manifest[i])) for i in re.findall(r'<itemref[^>]*idref="([^"]+)"', x) if i in manifest]
        order = [n for n in spine if n in z.namelist()] or names
    except Exception:
        pass
    units = [_html_text(z.read(n).decode('utf8', 'ignore')) for n in order]
    return [u for u in units if u], 'epub-spine'


def _secs(ts):
    ts = ts.strip().replace(',', '.')
    parts = [float(x) for x in ts.split(':')]
    while len(parts) < 3: parts.insert(0, 0.0)
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


def _mmss(s):
    s = int(s); return f'{s // 60:d}:{s % 60:02d}'


def subtitle_units(path):
    text = open(path, encoding='utf-8', errors='ignore').read().replace('\r', '')
    cues = []
    for block in re.split(r'\n\s*\n', text):
        m = re.search(r'([\d:.,]+)\s*-->\s*([\d:.,]+)', block)
        if not m: continue
        body = block[m.end():].strip()
        body = clean(re.sub(r'<[^>]+>', '', body.replace('\n', ' ')))
        if body: cues.append((_secs(m.group(1)), body))
    units, cur, start = [], [], None
    for t, body in cues:
        if start is None: start = t
        if t - start >= WINDOW_SECONDS and cur:
            units.append(f'({_mmss(start)}-{_mmss(t)}) ' + ' '.join(cur)); cur, start = [], t
        cur.append(body)
    if cur: units.append(f'({_mmss(start)}-{_mmss(cues[-1][0])}) ' + ' '.join(cur))
    return units, 'subtitle-windows'


def image_units(path):
    if os.path.isdir(path):
        files = sorted(n for n in os.listdir(path) if n.lower().endswith(IMAGES))
        return [''] * len(files), 'image-folder'
    return [''], 'image'


def units_of(path):
    if os.path.isdir(path): return image_units(path), 'page'
    ext = os.path.splitext(path)[1].lower()
    if ext in IMAGES: return image_units(path), 'page'
    readers = {'.pdf': pdf_units, '.pptx': pptx_units, '.docx': docx_units, '.md': md_units, '.markdown': md_units, '.txt': txt_units,
               '.html': html_units, '.htm': html_units, '.epub': epub_units, '.srt': subtitle_units, '.vtt': subtitle_units}
    if ext not in readers:
        sys.exit(f'Cannot read {ext or "this file"} directly. Supported: pdf, pptx, docx, md, txt, html, epub, srt, vtt, an image, or a folder of images. '
                 'For spreadsheets, audio or video, convert or transcribe first (a .txt, .srt or .vtt transcript works).')
    return readers[ext](path), UNIT_WORD[ext]


def one_line(t):
    parts = [re.sub(r'\s+', ' ', l).strip() for l in t.split('\n')]
    return ' | '.join(p for p in parts if p)


def cmd_extract(a):
    src = a.source.rstrip('/')
    (units, method), word = units_of(src)
    word = a.unit_word or word
    base = os.path.basename(src)
    out = a.out or (os.path.join(os.path.dirname(os.path.abspath(src)), os.path.splitext(base)[0] + '.' + word + 's.txt') if not os.path.isdir(src)
                    else os.path.join(os.path.dirname(os.path.abspath(src)), base + '.' + word + 's.txt'))
    lines, empty = [], []
    for i, t in enumerate(units, 1):
        s = one_line(t)
        if len(s) < 12 and not re.match(r'^\(\d', s):
            empty.append(i); s = NO_TEXT
        lines.append(f'[{i}] {s}')
    open(out, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    mp = os.path.join(os.path.dirname(os.path.abspath(out)), 'sources.json')
    man = json.load(open(mp)) if os.path.exists(mp) else {}
    man[base] = {'sha256': sha(src), 'units': len(units), 'unit_word': word, 'slides': len(units), 'cache': os.path.basename(out),
                 'method': method, 'needs_visual_read': empty}
    json.dump(man, open(mp, 'w'), indent=2)
    print(f'{a.source}: {len(units)} {word}s -> {out} ({method}); {len(empty)} {word}s without text')


def cmd_slice(a):
    for l in open(a.cache, encoding='utf-8'):
        m = re.match(r'\[(\d+)\] ', l)
        if m and a.start <= int(m.group(1)) <= a.end: print(l.rstrip('\n'))


def cmd_check(a):
    mp = os.path.join(a.dir, 'sources.json')
    if not os.path.exists(mp): sys.exit('no sources.json: run `extract` on each source first')
    man = json.load(open(mp)); bad = 0
    for name, info in man.items():
        p = os.path.join(a.dir, name)
        n, word = info.get('units', info.get('slides', 0)), info.get('unit_word', 'slide')
        if not os.path.exists(p): print('MISSING ', name); bad += 1
        elif sha(p) != info['sha256']: print('CHANGED ', name, '(re-run extract, then rebuild what depends on it)'); bad += 1
        elif not os.path.exists(os.path.join(a.dir, info['cache'])): print('NO CACHE', name); bad += 1
        else: print('fresh   ', name, f"({n} {word}s, {len(info['needs_visual_read'])} need a visual read)")
    sys.exit(1 if bad else 0)


def cmd_index(a):
    n = empty = 0
    for l in open(a.cache, encoding='utf-8'):
        if re.match(r'\[\d+\] ', l):
            n += 1; empty += '[NO TEXT' in l
    print(f'{n} units, {empty} without text')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    e = sp.add_parser('extract'); e.add_argument('source'); e.add_argument('--out'); e.add_argument('--unit-word'); e.set_defaults(f=cmd_extract)
    s = sp.add_parser('slice'); s.add_argument('cache'); s.add_argument('start', type=int); s.add_argument('end', type=int); s.set_defaults(f=cmd_slice)
    c = sp.add_parser('check'); c.add_argument('dir'); c.set_defaults(f=cmd_check)
    i = sp.add_parser('index'); i.add_argument('cache'); i.set_defaults(f=cmd_index)
    a = ap.parse_args(); a.f(a)


if __name__ == '__main__':
    main()
