#!/usr/bin/env python3
"""Test that source_text.py reads every supported kind of student asset.

Builds tiny sample sources in a temporary folder (nothing is committed): markdown, plain text, HTML, Word (.docx),
PowerPoint (.pptx), EPUB, SubRip and WebVTT transcripts, an image and a folder of images; extracts each, checks the
unit counts, unit words and text, then checks that `check` notices a changed original and that an unsupported file is
refused with a helpful message. Standard library only. Exit code 1 on any failure.
"""
import base64, json, os, subprocess, sys, tempfile, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(ROOT, 'skills', 'study-guide-tutor', 'scripts', 'source_text.py')
PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==')
fails = []


def run(*args):
    return subprocess.run([sys.executable, '-I', TOOL, *args], capture_output=True, text=True)


def check(name, cond, detail=''):
    print(('PASS ' if cond else 'FAIL ') + name + ((' :: ' + detail) if (detail and not cond) else ''))
    if not cond: fails.append(name)


def cache_of(d, stem, word):
    p = os.path.join(d, f'{stem}.{word}s.txt')
    return open(p, encoding='utf-8').read() if os.path.exists(p) else ''


def units(text): return [l for l in text.split('\n') if l.startswith('[')]


def minimal_pdf(pages):
    """A tiny valid text PDF with one line of text per page (no compression), built by hand."""
    objs = []
    n = len(pages)
    kids = ' '.join(f'{3 + i * 2} 0 R' for i in range(n))
    objs.append('<< /Type /Catalog /Pages 2 0 R >>')
    objs.append(f'<< /Type /Pages /Kids [{kids}] /Count {n} >>')
    for i, text in enumerate(pages):
        page_obj, content_obj = 3 + i * 2, 4 + i * 2
        objs.append(f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] /Contents {content_obj} 0 R /Resources << /Font << /F1 {3 + n * 2} 0 R >> >> >>')
        stream = f'BT /F1 14 Tf 20 100 Td ({text}) Tj ET'
        objs.append(f'<< /Length {len(stream)} >>\nstream\n{stream}\nendstream')
    objs.append('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>')
    out, offs = '%PDF-1.4\n', []
    for i, o in enumerate(objs, 1):
        offs.append(len(out.encode('latin-1'))); out += f'{i} 0 obj\n{o}\nendobj\n'
    xref = len(out.encode('latin-1'))
    out += f'xref\n0 {len(objs) + 1}\n0000000000 65535 f \n' + ''.join(f'{o:010d} 00000 n \n' for o in offs)
    out += f'trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'
    return out.encode('latin-1')


def have_pdf_extractor():
    import importlib.util, shutil
    return bool(shutil.which('pdftotext') or any(importlib.util.find_spec(m) for m in ('pypdf', 'PyPDF2', 'fitz')))


def main():
    d = tempfile.mkdtemp()
    w = lambda n, t, m='w': open(os.path.join(d, n), m, **({} if 'b' in m else {'encoding': 'utf-8'})).write(t)
    w('notes.md', '# Water\nEvaporation turns liquid into vapour.\n\n## Clouds\nCondensation forms clouds when vapour cools.\n\n## Rain\nPrecipitation returns water to the ground.\n')
    w('plain.txt', ' '.join(['word'] * 200) + '\n\n' + ' '.join(['more'] * 200) + '\n\n' + ' '.join(['last'] * 200) + '\n')
    w('page.html', '<html><body><h1>Intro</h1><p>Plants release vapour through leaves.</p><h2>Ground</h2><p>Runoff flows over land.</p><h2>Ice</h2><script>x=1</script><p>Sublimation skips the liquid stage.</p></body></html>')
    # docx with two headed sections
    para = lambda t, style=None: '<w:p>' + (f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else '') + f'<w:r><w:t>{t}</w:t></w:r></w:p>'
    docx = '<?xml version="1.0"?><w:document xmlns:w="w"><w:body>' + para('Part one', 'Heading1') + para('The first section text is here for the test.') + para('Part two', 'Heading1') + para('The second section text is here too.') + '</w:body></w:document>'
    with zipfile.ZipFile(os.path.join(d, 'brief.docx'), 'w') as z: z.writestr('word/document.xml', docx)
    # pptx with two slides, notes on the first
    sl = lambda t: f'<p:sld xmlns:a="a"><a:p><a:r><a:t>{t}</a:t></a:r></a:p></p:sld>'
    with zipfile.ZipFile(os.path.join(d, 'deck.pptx'), 'w') as z:
        z.writestr('ppt/slides/slide2.xml', sl('Second slide about condensation of vapour'))
        z.writestr('ppt/slides/slide1.xml', sl('First slide about evaporation from the sun'))
        z.writestr('ppt/notesSlides/notesSlide1.xml', sl('Remember the sun supplies the heat'))
    # epub: spine order is ch2 then ch1
    with zipfile.ZipFile(os.path.join(d, 'book.epub'), 'w') as z:
        z.writestr('OEBPS/content.opf', '<package><manifest><item id="a" href="ch1.xhtml"/><item id="b" href="ch2.xhtml"/></manifest><spine><itemref idref="b"/><itemref idref="a"/></spine></package>')
        z.writestr('OEBPS/ch1.xhtml', '<html><body><h1>One</h1><p>First chapter text of the book.</p></body></html>')
        z.writestr('OEBPS/ch2.xhtml', '<html><body><h1>Two</h1><p>Second chapter text of the book.</p></body></html>')
    # transcripts: 5 minutes of 10-second cues
    def cue(i): t = i * 10; s = lambda x: f'00:{x // 60:02d}:{x % 60:02d}'; return f'{i + 1}\n{s(t)},000 --> {s(t + 9)},000\nCue number {i} talks about the water cycle.\n'
    w('talk.srt', '\n'.join(cue(i) for i in range(30)))
    w('talk2.vtt', 'WEBVTT\n\n00:00:00.000 --> 00:00:05.000\nShort clip about runoff and infiltration.\n')
    w('scan.png', PNG, 'wb')
    os.makedirs(os.path.join(d, 'photos'))
    for n in ('b.png', 'a.png', 'c.png'): open(os.path.join(d, 'photos', n), 'wb').write(PNG)
    w('table.xlsx', 'not really a spreadsheet')
    w('lecture.pdf', minimal_pdf(['Evaporation turns liquid water into vapour', 'Condensation forms clouds from cooling vapour']), 'wb')

    expect = {  # source -> (stem, word, units, text that must appear)
        'notes.md': ('notes', 'section', 3, 'Condensation forms clouds'),
        'plain.txt': ('plain', 'section', 2, 'word word'),
        'page.html': ('page', 'section', 3, 'Sublimation skips'),
        'brief.docx': ('brief', 'section', 2, 'second section text'),
        'deck.pptx': ('deck', 'slide', 2, 'Notes: Remember the sun'),
        'book.epub': ('book', 'section', 2, 'Second chapter text'),
        'talk.srt': ('talk', 'segment', 3, '(0:00-'),
        'talk2.vtt': ('talk2', 'segment', 1, 'runoff and infiltration'),
        'scan.png': ('scan', 'page', 1, 'NO TEXT'),
    }
    for src, (stem, word, n, needle) in expect.items():
        r = run('extract', os.path.join(d, src))
        c = cache_of(d, stem, word)
        got = len(units(c))
        check(f'{src}: {n} {word}(s) found, text present', r.returncode == 0 and (got == n or (src == 'plain.txt' and got >= 2) or (src == 'talk.srt' and got >= 3)) and needle in c, f'rc={r.returncode} units={got} err={r.stderr[:120]}')
    if have_pdf_extractor():
        r = run('extract', os.path.join(d, 'lecture.pdf'))
        c = cache_of(d, 'lecture', 'slide')
        check('lecture.pdf: 2 slides found, text present', r.returncode == 0 and len(units(c)) == 2 and 'Condensation forms clouds' in c, f'rc={r.returncode} {r.stdout[:80]} {r.stderr[:120]}')
    else:
        print('SKIP lecture.pdf: no PDF extractor installed (install poppler-utils or pypdf to test the PDF path)')
    check('deck.pptx: slides read in numeric order', cache_of(d, 'deck', 'slide').split('\n')[0].startswith('[1] First slide'))
    check('book.epub: spine order is followed', cache_of(d, 'book', 'section').split('\n')[0].startswith('[1] Two'))
    check('scan.png: flagged as needing a visual read', json.load(open(os.path.join(d, 'sources.json')))['scan.png']['needs_visual_read'] == [1])
    r = run('extract', os.path.join(d, 'photos'))
    check('folder of images: one page per image', r.returncode == 0 and len(units(open(os.path.join(d, 'photos.pages.txt')).read())) == 3, r.stderr[:120])
    r = run('extract', os.path.join(d, 'table.xlsx'))
    check('unsupported file is refused with advice', r.returncode != 0 and 'Supported:' in (r.stdout + r.stderr))
    r = run('slice', os.path.join(d, 'notes.sections.txt'), '2', '2')
    check('slice prints only the requested unit', r.stdout.startswith('[2] ## Clouds') and r.stdout.count('[') == 1, r.stdout[:100])
    r = run('index', os.path.join(d, 'notes.sections.txt'))
    check('index reports the unit count', '3 units' in r.stdout, r.stdout)
    os.remove(os.path.join(d, 'table.xlsx'))
    r = run('check', d)
    check('check: every cache is fresh', r.returncode == 0 and 'CHANGED' not in r.stdout, r.stdout[:200])
    w('notes.md', '# Water\nChanged text.\n')
    r = run('check', d)
    check('check: a changed original is reported', r.returncode != 0 and 'CHANGED  notes.md' in r.stdout, r.stdout[:200])
    # older manifests only had a "slides" count: check must still read them
    old = os.path.join(tempfile.mkdtemp(), 'x'); os.makedirs(old)
    open(os.path.join(old, 'a.pdf'), 'wb').write(b'%PDF-1.4')
    import hashlib; h = hashlib.sha256(b'%PDF-1.4').hexdigest()
    open(os.path.join(old, 'a.slides.txt'), 'w').write('[1] hello world hello world\n')
    json.dump({'a.pdf': {'sha256': h, 'slides': 1, 'cache': 'a.slides.txt', 'method': 'pdftotext', 'needs_visual_read': []}}, open(os.path.join(old, 'sources.json'), 'w'))
    r = run('check', old)
    check('check: reads manifests written by older versions', r.returncode == 0 and '1 slides' in r.stdout, r.stdout + r.stderr)
    print('RESULT: OK' if not fails else f'RESULT: {len(fails)} failed: {fails}')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
