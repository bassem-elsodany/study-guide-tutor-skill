#!/usr/bin/env python3
"""Build one self-contained interactive study player (a single HTML file) from a generated course.

Usage: make_player.py UNIT_DIR [--out FILE] [--title TEXT] [--no-diagrams] [--no-lessons] [--selftest]

UNIT_DIR is any folder that directly holds chapter-NN-slug/ folders (and optionally 00-overview/): the course
folder of a flat course, or one module, week, part, domain ... of a grouped one. Build one player per unit. For every chapter it
reads 03-quiz.md + 04-answer-key.md (questions, the key, a "why each wrong option is wrong" line per option, the hint,
the source location) and 02-flashcards.csv; from 00-overview/ it reads the exam (07-exam.md + 08-exam-key.md; the older 07-unit-exam / 07-domain-exam names too) and the checkpoint
quiz (03 + 04) when present. The result opens by double-click in any browser: no install, no server, no network.

The player has five tabs. Lesson comes first: every chapter's 01-lesson.md, rendered as a page (headings, tables,
the Tricky-part boxes, the open-and-close boxes, the Mermaid diagrams drawn as pictures) with a chapter picker, an "on
this page" list, a "mark as read" box, and buttons to the quiz and flashcards of that chapter. The Markdown files stay
the source: the player is a view built from them, so the student can read either, and rebuilding the player after an edit
refreshes it. Diagrams are drawn at build time with mermaid-cli (mmdc) when it is installed, cached under
~/.cache/study-guide-tutor/diagrams (or $SGT_CACHE_DIR); without it the diagram shows its Mermaid text instead.
The other four modes: Quiz (click or press A-D, instant feedback with the reason every wrong option is wrong,
optional hint, source location, retake of misses), Flashcards (flip, "knew it / missed it", spaced boxes with due
dates), Exam (timed, no feedback until submit, results by chapter, review of misses) and Progress (scores, boxes,
misses, "Download my results" as JSON for the tutor). Progress lives only in the browser (localStorage). The student's notes are different: they live in a Markdown file, 06-notes.md, in
each chapter's folder, read here when the player is built and written back by the player (see _notes.py).

Default output: UNIT_DIR/00-overview/09-study-player.html (or UNIT_DIR/study-player.html without 00-overview).
--selftest appends a scripted click-through to the page (for tests only; do not ship that file).
Questions that refer to other options by letter ("both A and B", "all of the above") are never reshuffled.
"""
import argparse, base64, csv, glob, hashlib, json, math, os, re, shutil, subprocess, sys, tempfile, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _layout
import _md
import _notes

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, '..', 'assets', 'player.html')

Q_SPLIT = re.compile(r'<a id="q(\d+)"></a>')
Q_HEAD = re.compile(r'\*\*Q(\d+) \(([^)]*)\)\.\*\*\s*(.*?)(?=\n\s*\n- A\. |\n- A\. )', re.S)
OPT = re.compile(r'^- ([A-D])\. (.+)$', re.M)
KEY_ROW = re.compile(r'^\| (\d+) \| \*\*([A-D])\*\* \| ([^|]*?) \| ([^|]*?) \|\s*$', re.M)
KEY_BLOCK = re.compile(r'\*\*Q(\d+): ([A-D])\.\*\*\s*(.*?)(?=\n\n<a id="q\d+"></a>|\n\n\*\*Q\d+: |\n\n---|\Z)', re.S)
BULLET = re.compile(r'^- ([A-D](?:(?:,\s*| and | & )[A-D])*)(?=[:\s])\s*:?\s*(.*)$')
LABELS = _layout.DEFAULT_LABELS  # replaced by the course's own words in build()


def read(p):
    return open(p, encoding='utf-8').read() if os.path.exists(p) else ''


def parse_quiz(path):
    """-> {n: {label, stem, opts}}"""
    out = {}
    text = read(path)
    parts = Q_SPLIT.split(text)
    if len(parts) < 3:  # no <a id="qN"> anchors yet (the contents step adds them): split on the question markers
        parts = [''] + [x for m in re.split(r'(?m)^(?=\*\*Q\d+ \()', text)[1:] for x in (re.match(r'\*\*Q(\d+) ', m).group(1), m)]
    for i in range(1, len(parts), 2):
        n, body = int(parts[i]), parts[i + 1]
        m = re.search(r'\*\*Q\d+ \(([^)]*)\)\.\*\*\s*(.*?)(?=\n\s*\n?- A\. )', body, re.S)
        opts = dict(OPT.findall(body))
        if not m or len(opts) < 2:
            continue
        stem = re.sub(r'\s*\n\s*', ' ', m.group(2)).strip()
        out[n] = {'label': m.group(1).strip(), 'stem': stem, 'opts': opts}
    return out


def parse_key(path):
    """-> {n: {key, col3, source, explanation, why, hint}}"""
    text = read(path)
    rows = {int(n): (k, c3.strip(), src.strip()) for n, k, c3, src in KEY_ROW.findall(text)}
    out = {}
    for m in KEY_BLOCK.finditer(text):
        n, key, rest = int(m.group(1)), m.group(2), m.group(3)
        lines = rest.split('\n')
        expl, why, hint = lines[0].strip(), {}, ''
        for l in lines[1:]:
            l = l.strip()
            hp = '- ' + LABELS['hint'].lower() + ':'
            if l.lower().startswith(hp):
                hint = l[len(hp):].strip()
                continue
            b = BULLET.match(l)
            if b:
                for L in re.findall(r'[A-D]', b.group(1)):
                    why[L] = b.group(2).strip() or why.get(L, '')
        k, c3, src = rows.get(n, (key, '', ''))
        out[n] = {'key': key, 'col3': c3, 'source': re.sub(r'\s*\[[^\]]*\]\s*$', '', src), 'explanation': expl, 'why': why, 'hint': hint}
    return out


def build_questions(prefix, quiz, key, chapter=None):
    qs, problems = [], []
    for n in sorted(quiz):
        q, k = quiz[n], key.get(n)
        if not k:
            problems.append(f'{prefix}{n}: no key block'); continue
        if k['key'] not in q['opts']:
            problems.append(f'{prefix}{n}: key {k["key"]} not among options'); continue
        label = q['label']
        ch = chapter
        ab = re.escape(LABELS['chapter_abbrev'])
        m = re.search(ab + r'\s*(\d+)', label)
        if m: ch = int(m.group(1))
        elif re.fullmatch(r'\d+', k['col3']): ch = int(k['col3'])
        label = re.sub(r',?\s*' + ab + r'\s*\d+', '', label).strip(', ')
        diff = label or (k['col3'] if not re.fullmatch(r'\d+', k['col3']) else '')
        fixed = bool(re.search(LABELS['letter_ref_regex'], ' '.join(q['opts'].values())))
        qs.append({'id': f'{prefix}{n}', 'n': n, 'ch': ch, 'label': diff, 'stem': q['stem'], 'opts': q['opts'], 'key': k['key'],
                   'explanation': k['explanation'], 'why': k['why'], 'hint': k['hint'], 'source': k['source'], 'fixed': fixed})
    return qs, problems


def lesson_title(chdir, n):
    t = read(os.path.join(chdir, '01-lesson.md'))
    m = re.search(r'^# (?:Chapter\s+\d+\s*[:.\-]\s*)?(.+)$', t, re.M)
    return m.group(1).strip() if m else os.path.basename(chdir)


def audience_statement(root):
    """The one-line 'Audience statement' from learner-profile.md (course root or its parent), or ''."""
    label = re.escape(LABELS['audience_statement'])
    for d in (root, os.path.dirname(root)):
        m = re.search(r'(?mi)^\**' + label + r':?\**:?\s*(.+)$', read(os.path.join(d, 'learner-profile.md')))
        if m:
            return m.group(1).strip().rstrip('.')
    return ''


MERMAID = re.compile(r'^```mermaid[ \t]*\n(.*?)\n```', re.S | re.M)
IMAGE_TYPES = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.webp': 'image/webp', '.svg': 'image/svg+xml'}


def diagram_cache():
    return os.environ.get('SGT_CACHE_DIR') or os.path.join(os.path.expanduser('~'), '.cache', 'study-guide-tutor', 'diagrams')


def render_diagrams(codes):
    """-> {mermaid source: SVG text} for every diagram mermaid-cli could draw. Cached by content, drawn in one batch."""
    out, todo = {}, []
    cache = diagram_cache()
    for c in dict.fromkeys(codes):
        key = hashlib.sha256(('neutral\n' + c).encode('utf-8')).hexdigest()[:20]
        f = os.path.join(cache, key + '.svg')
        if os.path.exists(f):
            out[c] = (key, read(f))
        else:
            todo.append((c, key, f))
    mmdc = shutil.which('mmdc') if todo else None
    if not mmdc:
        return out
    with tempfile.TemporaryDirectory() as d:
        cfg = os.path.join(d, 'p.json'); open(cfg, 'w').write('{"args": ["--no-sandbox"]}')

        def run(src, dst):
            try:
                return subprocess.run([mmdc, '-i', src, '-o', dst, '-e', 'svg', '-t', 'neutral', '-b', 'transparent', '-p', cfg, '-q'],
                                      capture_output=True, text=True, timeout=900).returncode == 0
            except (OSError, subprocess.TimeoutExpired):
                return False
        src = os.path.join(d, 'all.md')
        open(src, 'w', encoding='utf-8').write('\n\n'.join('```mermaid\n' + c + '\n```' for c, _, _ in todo))
        run(src, os.path.join(d, 'all-out.md'))
        for i, (c, key, f) in enumerate(todo, 1):
            svg = os.path.join(d, 'all-out-%d.svg' % i)
            if not os.path.exists(svg):   # one bad diagram can stop the batch: draw the rest one by one
                one, dst = os.path.join(d, 'one-%d.mmd' % i), os.path.join(d, 'one-%d.svg' % i)
                open(one, 'w', encoding='utf-8').write(c)
                if run(one, dst): svg = dst
            if os.path.exists(svg):
                text = read(svg)
                out[c] = (key, text)
                try:
                    os.makedirs(cache, exist_ok=True); open(f, 'w', encoding='utf-8').write(text)
                except OSError:
                    pass
    return out


def diagram_html(code, drawn):
    got = drawn.get(code)
    if got:
        key, svg = got
        svg = svg.replace('my-svg', 'mmd' + key[:10])
        svg = re.sub(r'^<\?xml[^>]*\?>\s*', '', svg)
        return '<div class="diagram" role="img" aria-label="Diagram">%s</div>' % svg
    return '<div class="diagram"><p class="muted small" data-t="diagramMissing"></p><pre>%s</pre></div>' % _md.esc(code)


def lesson_html(chdir, text, chapter_dirs, out_dir, drawn):
    """-> {html, toc, minutes, md} for one 01-lesson.md, links and images resolved against this chapter's folder."""
    def link(href):
        path, _, frag = href.partition('#')
        if not path:
            return ('text', None)
        target = os.path.normpath(os.path.join(chdir, urllib.parse.unquote(path)))
        if not os.path.exists(target):
            return ('text', None)
        n = chapter_dirs.get(os.path.dirname(target))
        base = os.path.basename(target)
        if n is not None:
            if base == '01-lesson.md': return ('go', 'lesson:%d' % n)
            if base in ('03-quiz.md', '04-answer-key.md'): return ('go', 'quiz:%d' % n)
            if base == '02-flashcards.csv': return ('go', 'cards:%d' % n)
        return ('href', urllib.parse.quote(os.path.relpath(target, out_dir).replace(os.sep, '/')))

    def image(src, alt):
        f = os.path.normpath(os.path.join(chdir, urllib.parse.unquote(src)))
        ext = os.path.splitext(f)[1].lower()
        if ext in IMAGE_TYPES and os.path.isfile(f) and os.path.getsize(f) <= 1500000:
            return 'data:%s;base64,%s' % (IMAGE_TYPES[ext], base64.b64encode(open(f, 'rb').read()).decode('ascii'))
        return None
    ctx = {'prefix': 'l%d-' % chapter_dirs[os.path.normpath(chdir)], 'link': link, 'image': image,
           'diagram': lambda code: diagram_html(code, drawn)}
    html, title, heads = _md.render(text, ctx)
    html = re.sub(r'<h1[^>]*>.*?</h1>\s*', '', html, count=1, flags=re.S)
    words = len(re.sub(r'<!--.*?-->|```mermaid.*?```', '', text, flags=re.S).split())
    return {'html': html, 'toc': [[lv, tx, hid] for lv, tx, hid in heads],
            'minutes': max(1, math.ceil(words / 200 + 0.3 * len(MERMAID.findall(text)))),
            'md': urllib.parse.quote(os.path.relpath(os.path.join(chdir, '01-lesson.md'), out_dir).replace(os.sep, '/'))}


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-') or 'course'


def default_out(unit):
    return os.path.join(unit, '00-overview', '09-study-player.html') if os.path.isdir(os.path.join(unit, '00-overview')) else os.path.join(unit, 'study-player.html')


def build(unit, title=None, out=None, diagrams=True, lessons=True):
    global LABELS
    unitdir = os.path.abspath(unit)
    out_dir = os.path.dirname(os.path.abspath(out or default_out(unit)))
    chapter_dirs = {os.path.normpath(c): int(os.path.basename(c).split('-')[1]) for c in _layout.chapters_of(unitdir)}
    lesson_text = {c: read(os.path.join(c, '01-lesson.md')) for c in chapter_dirs} if lessons else {}
    drawn = render_diagrams([code for tx in lesson_text.values() for code in MERMAID.findall(tx)]) if (lessons and diagrams) else {}
    LABELS = _layout.labels(unitdir)
    cfg = _layout.course_config(unitdir)
    lang, direction = _layout.language(unitdir)
    problems, chapters = [], []
    for chdir in _layout.chapters_of(unitdir):
        n = int(os.path.basename(chdir).split('-')[1])
        quiz, key = parse_quiz(os.path.join(chdir, '03-quiz.md')), parse_key(os.path.join(chdir, '04-answer-key.md'))
        qs, pr = build_questions(f'c{n}q', quiz, key, n)
        problems += [f'chapter {n} {x}' for x in pr]
        cards = []
        cp = os.path.join(chdir, '02-flashcards.csv')
        if os.path.exists(cp):
            with open(cp, encoding='utf-8', newline='') as f:
                for r in csv.reader(f):
                    if len(r) >= 2 and r[0].strip().lower() != 'question':
                        cards.append({'q': r[0].strip(), 'a': r[1].strip()})
        ch = {'n': n, 'title': lesson_title(chdir, n), 'questions': qs, 'cards': cards}
        ntext = read(os.path.join(chdir, _notes.FILE))      # the student's own notes file, if there is one
        ch['dir'] = os.path.basename(chdir)
        ch['notes'] = _notes.parse(ntext)
        ch['notesHash'] = _notes.fnv(ntext)
        tx = lesson_text.get(os.path.normpath(chdir), '')
        if tx.strip():
            ch['lesson'] = lesson_html(os.path.normpath(chdir), tx, chapter_dirs, out_dir, drawn)
        chapters.append(ch)
    ov = os.path.join(unitdir, '00-overview')
    final = exam = None
    fq, fk = parse_quiz(os.path.join(ov, '03-final-quiz.md')), parse_key(os.path.join(ov, '04-final-quiz-key.md'))
    if fq:
        qs, pr = build_questions('f', fq, fk); problems += [f'final {x}' for x in pr]; final = {'questions': qs}
    exam_q, exam_k = _layout.exam_pair(ov)
    eq, ek = (parse_quiz(exam_q), parse_key(exam_k)) if exam_q else ({}, {})
    if eq:
        qs, pr = build_questions('x', eq, ek); problems += [f'exam {x}' for x in pr]
        m = re.search(re.escape(LABELS['suggested_time']) + r':\s*\*\*(\d+)\s*' + re.escape(LABELS['minutes']), read(exam_q))
        exam = {'minutes': int(m.group(1)) if m else max(10, round(len(qs) * 1.5)), 'questions': qs}
    m_title = re.search(r'^# (.+?)(?::\s*(?:Domain |Unit )?' + re.escape(LABELS['exam_label']) + r')?\s*$', read(exam_q) if exam_q else '', re.M)
    if title: name = title
    elif m_title: name = m_title.group(1)
    elif len(chapters) == 1: name = chapters[0]['title']
    else: name = re.sub(r'[-_]+', ' ', os.path.basename(unitdir)).strip().capitalize()
    nq = sum(len(c['questions']) for c in chapters)
    data = {'id': slug(os.path.basename(os.path.dirname(unitdir)) + '-' + os.path.basename(unitdir) + '-' + name),
            'title': name, 'counts': {'chapters': len(chapters), 'questions': nq, 'cards': sum(len(c['cards']) for c in chapters),
                                      'exam': len(exam['questions']) if exam else 0},
            'audience': audience_statement(unitdir), 'chapters': chapters, 'final': final, 'exam': exam,
            'notesIntro': _notes.INTRO,
            'lang': lang, 'dir': direction, 'ui': {k: v for k, v in cfg.get('ui', {}).items() if isinstance(v, str)}}
    return data, problems


SELFTEST = r'''<script>
(function(){
var out = [], ok = true, tail = Promise.resolve();
function check(n, c){ out.push((c ? 'PASS ' : 'FAIL ') + n); if (!c) ok = false; }
function $(s){ return document.querySelector(s); }
function $$(s){ return Array.prototype.slice.call(document.querySelectorAll(s)); }
function click(el){ el.click(); }
try {
  var A = window.__sgt, D = A.D;
  check('data has chapters', D.chapters.length > 0);
  check('tabs rendered', $$('#tabs button').length >= 4);
  // lesson tab comes first and shows the chapter's Markdown as a page
  var hasLessons = D.chapters.some(function(c){ return !!c.lesson; });
  if (hasLessons) {
    var lessonCh = D.chapters.filter(function(c){ return c.lesson; });
    check('lesson is the first tab and selected', $$('#tabs button')[0].textContent === A.t('tabLesson') && $$('#tabs button')[0].getAttribute('aria-selected') === 'true');
    check('lesson text shown', !!$('#lesson h2') && $('#lesson').textContent.length > 200);
    check('lesson has a chapter picker', !!$('#lchap') && $('#lchap').options.length === lessonCh.length);
    check('lesson tables are wrapped for narrow screens', $$('#lesson .tablewrap table').length >= 1);
    check('lesson has a diagram or its text fallback', $$('#lesson .diagram').length >= 1);
    check('lesson boxes are native details', $$('#lesson details > summary').length >= 1);
    check('no script or handler in lesson html', !$('#lesson script') && !$('#lesson [onclick]'));
    check('open-markdown link present', !!$('#openmd') && $('#openmd').getAttribute('href').indexOf('01-lesson.md') >= 0);
    $('#markread').click();
    check('mark as read saved', !!A.S().read[lessonCh[0].n]);
    click($('#quizthis'));
    check('quiz-this-chapter opens Quiz with the chapter preselected', !!$('#qset') && $('#qset').value === 'c' + lessonCh[0].n);
    A.setTab('lesson');
    var links = $$('#lesson a[data-go]');
    if (links.length) {
      var kind = links[0].getAttribute('data-go').split(':')[0];
      click(links[0]);
      check('a link inside the lesson switches tab (' + kind + ')', (kind === 'quiz' && !!$('#qset')) || (kind === 'cards' && !!$('#cset')) || (kind === 'lesson' && !!$('#lesson')));
    }
    A.setTab('lesson');
    if (lessonCh.length > 1) { click($('#nextch')); check('next chapter shows another lesson', A.S().lesson === lessonCh[1].n && !!$('#lesson')); }
    // section tabs: one per section, the clicked one is current
    A.setTab('lesson');
    var h2n = $$('#lesson h2').length;
    check('a section tab for every section', h2n < 2 || $$('#secnav a').length === h2n);
    if ($$('#secnav a').length > 1) { click($$('#secnav a')[1]); check('a clicked section tab becomes current', $$('#secnav a')[1].getAttribute('aria-current') === 'true'); }
    // highlights and notes
    window.confirm = function(){ return true; };
    function textNodes(){
      var w = document.createTreeWalker($('#lesson'), NodeFilter.SHOW_TEXT), n, out = [];
      while ((n = w.nextNode())) if (n.nodeValue.trim().length >= 30 && !(n.parentNode.closest && n.parentNode.closest('.diagram, mark, summary'))) out.push(n);
      return out;
    }
    function selectText(node, a, b){ var r = document.createRange(); r.setStart(node, a); r.setEnd(node, b); var s = window.getSelection(); s.removeAllRanges(); s.addRange(r); return r.toString(); }
    var cur = $('#lchap').value, curN = parseInt(cur, 10);
    var mineNotes = function(){ return A.S().notes[cur] || []; };
    var base = mineNotes().length;
    check('notes seeded from the notes file (if any) are painted', mineNotes().length === 0 || $$('#lesson mark.hl').length >= 1);
    var first = textNodes()[0], quote1 = selectText(first, 0, 12).replace(/\s+/g, ' ').trim();
    check('selecting lesson text shows the highlight toolbar', A.checkSelection() && !!$('#nphl') && !!$('#npnote'));
    click($('#nphl'));
    check('a highlight is saved and painted', mineNotes().length === base + 1 && mineNotes().some(function(n){ return n.quote === quote1; }) && $$('#lesson mark.hl').length >= 1);
    var tn = textNodes(), last = tn[tn.length - 1];
    selectText(last, 0, 14);
    check('toolbar shows again for new text', A.checkSelection());
    click($('#npnote'));
    check('note editor opens with a text box', !!$('#nptext') && !!$('#npsave'));
    $('#nptext').value = 'my test note'; click($('#npsave'));
    function mine(){ return mineNotes().filter(function(n){ return n.note === 'my test note' || n.note === 'changed note' || n.note === 'edited again'; })[0]; }
    check('a note is saved, painted and listed', mineNotes().length === base + 2 && !!mine() && $$('#lesson mark.has-note').length >= 1 && $('#chnotes').textContent.indexOf('my test note') >= 0);
    check('the note remembers its section', typeof mine().sec === 'string' && mine().sec.length > 0);
    check('the chapter is marked as not yet saved to its notes file', !!A.S().dirty[curN]);
    var m0 = $('#lesson mark.hl[data-id="' + mineNotes().filter(function(n){ return n.quote === quote1; })[0].id + '"]');
    selectText(m0.firstChild, 0, m0.firstChild.nodeValue.length);
    check('selecting already highlighted text offers nothing', !A.checkSelection() && !$('#notepop'));
    window.getSelection().removeAllRanges();
    A.setTab('notes');
    check('Notes tab lists the notes and offers downloads', $('#app').textContent.indexOf('my test note') >= 0 && !!$('#notesdl') && A.notesMd().indexOf('my test note') >= 0);
    check('Notes tab label shows the count', $$('#tabs button').some(function(b){ return b.textContent.indexOf('(' + (base + 2) + ')') >= 0; }));
    click($$('.notelist li')[0].querySelector('button'));
    check('Show in lesson opens the lesson with the highlights painted', !!$('#lesson') && $$('#lesson mark.hl').length >= 2);
    A.render();
    check('highlights come back after a redraw', $$('#lesson mark.hl').length >= 2);
    function liWith(s){ return $$('#chnotes .notelist li').filter(function(li){ return li.textContent.indexOf(s) >= 0; })[0]; }
    click(liWith('my test note').querySelectorAll('button')[0]);
    check('Edit opens the editor with the saved note', !!$('#nptext') && $('#nptext').value === 'my test note');
    $('#nptext').value = 'changed note'; click($('#npsave'));
    check('an edited note is saved', mine().note === 'changed note');
    var lb = liWith(quote1).querySelectorAll('button');
    click(lb[lb.length - 1]);
    check('deleting a note removes it and its highlight', mineNotes().length === base + 1 && $$('#lesson mark.hl').every(function(m){ return m.getAttribute('data-id') !== undefined && mineNotes().some(function(n){ return n.id === m.getAttribute('data-id'); }); }));

    // the notes file: the same text as Python writes and reads, and a folder to keep it in
    var FX = __NOTES_FIXTURE__;
    var keyed = function(n){ return [n.id, n.quote, n.note, n.sec, n.start, n.end, n.prefix, n.suffix, n.ts]; };
    check('the player writes the same notes file as the Python writer', A.notesToMd(FX.title, FX.notes) === FX.md);
    check('the player reads a notes file the same way as the Python reader', JSON.stringify(A.parseNotes(FX.md).map(keyed)) === JSON.stringify(FX.parsed.map(keyed)));
    check('the content hash matches the Python one', A.fnv('hello') === '4f9f2cab' && A.fnv(FX.md) === FX.hash);
    var files = {};
    var fake = {getDirectoryHandle: function(name){
      if (!D.chapters.some(function(c){ return c.dir === name; })) return Promise.reject({name: 'NotFoundError'});
      return Promise.resolve({getFileHandle: function(fn, o){
        var key = name + '/' + fn;
        if (!(key in files) && !(o && o.create)) return Promise.reject({name: 'NotFoundError'});
        return Promise.resolve({
          createWritable: function(){ return Promise.resolve({write: function(t){ files[key] = t; return Promise.resolve(); }, close: function(){ return Promise.resolve(); }}); },
          getFile: function(){ return Promise.resolve({text: function(){ return Promise.resolve(files[key]); }}); }});
      }});
    }};
    var chd = D.chapters.filter(function(c){ return String(c.n) === cur; })[0].dir, nfile = chd + '/06-notes.md';
    tail = tail.then(function(){ return A.useFolder(fake); }).then(function(ok){
      check('connecting a course folder works', ok === true);
      var text = files[nfile];
      check('connecting writes the unsaved notes into the chapter folder', !!text && text.indexOf('changed note') >= 0 && A.parseNotes(text).length === mineNotes().length);
      check('a saved chapter is no longer marked unsaved', !A.S().dirty[curN]);
      files[nfile] = text + '\n## Note 99\n\n> written by hand in the file\n\nfrom the file\n';
      return A.useFolder(fake);
    }).then(function(){
      check('a note written by hand in the file is picked up', mineNotes().some(function(n){ return n.note === 'from the file'; }));
      A.setTab('lesson');
      click(liWith('changed note').querySelectorAll('button')[0]);
      $('#nptext').value = 'edited again'; click($('#npsave'));
      return A.flush();
    }).then(function(){
      check('a change made in the player is written to the notes file', files[nfile].indexOf('edited again') >= 0 && !A.S().dirty[curN]);
    });
  }
  // quiz: start first chapter set
  A.setTab('quiz'); A.state().quiz = null; A.render();
  var sel = $('#qset'); sel.value = 'c' + D.chapters[0].n; click($('#qstart'));
  check('question shown', !!$('.stem') && $$('button.opt').length >= 2);
  check('options enabled', $$('button.opt').every(function(b){ return !b.disabled; }));
  var q = A.state().quiz.list[0], order = A.state().quiz.order;
  var wrongIdx = order.findIndex(function(o){ return o !== q.key; });
  click($$('button.opt')[wrongIdx]);
  check('feedback shown for wrong answer', !!$('#feedback.bad'));
  check('correct option highlighted', $$('button.opt.ok').length === 1 && $$('button.opt.bad').length === 1);
  check('why-wrong text shown', $$('#feedback .why li').length >= 1);
  check('options locked after answer', $$('button.opt').every(function(b){ return b.disabled; }));
  check('miss recorded', !!A.S().misses[q.id]);
  click($('#nextbtn'));
  if (A.state().quiz.list.length > 1) {
    check('advanced to question 2', $('.card').textContent.indexOf(A.t('qOf', {i: 2, n: A.state().quiz.list.length})) >= 0);
    var q2 = A.state().quiz.list[1], o2 = A.state().quiz.order;
    click($$('button.opt')[o2.indexOf(q2.key)]);
    check('correct answer feedback', !!$('#feedback.ok'));
  }
  // finish the set
  var guard = 0;
  while (A.state().quiz && !A.state().quiz.done && guard++ < 200) {
    var Z = A.state().quiz;
    if (!Z.answered) click($$('button.opt')[0]);
    click($('#nextbtn'));
  }
  check('summary reached', $('.card').textContent.indexOf(A.t('results', {label: ''}).trim()) >= 0);
  check('quiz record saved', !!A.S().quiz['c' + D.chapters[0].n]);
  if ($$('.card button').some(function(b){ return b.textContent === A.t('retakeBtn'); })) {
    click($$('.card button').filter(function(b){ return b.textContent === A.t('retakeBtn'); })[0]);
    check('retake starts', $('.card').textContent.indexOf(A.t('qOf', {i: 1, n: A.state().quiz.list.length})) >= 0);
    click($('.btn.small'));  // quit
  }
  // a mixed-set quiz must also show up in Progress
  A.setTab('quiz'); A.state().quiz = null; A.render();
  $('#qset').value = 'all'; click($('#qstart'));
  var g2 = 0;
  while (A.state().quiz && !A.state().quiz.done && g2++ < 400) {
    if (!A.state().quiz.answered) click($$('button.opt')[0]);
    click($('#nextbtn'));
  }
  check('mixed quiz finished and recorded', !!A.S().quiz.all);
  // flashcards
  A.setTab('cards');
  var csel = $('#cset'); click($('#cstart'));
  check('card front shown', !!$('.flash') && !!$('#revealbtn'));
  var front = $('.flash').textContent;
  click($('#revealbtn'));
  check('card flipped', $('.flash').textContent !== front && !!$('#gotbtn'));
  click($('#missbtn'));
  var ids = Object.keys(A.S().cards);
  check('missed card stored in box 1', ids.length === 1 && A.S().cards[ids[0]].box === 1);
  click($('#revealbtn')); click($('#gotbtn'));
  check('known card moves to box 2', Object.keys(A.S().cards).some(function(id){ return A.S().cards[id].box === 2; }) || A.state().cards.list.length < 2);
  // exam
  if (D.exam) {
    A.setTab('exam'); click($('#examstart'));
    check('exam question shown', !!$('.stem') && !!$('#timer'));
    check('no feedback during exam', !$('#feedback'));
    var X = A.state().exam, id = X.order[0];
    click($$('button.opt')[0]);
    check('exam answer recorded', !!X.answers[id]);
    window.confirm = function(){ return true; };
    click($('#examsubmit'));
    check('exam results shown', $('.card').textContent.indexOf(A.t('examResults')) >= 0 && $('.card').textContent.indexOf(A.t('thChapter')) >= 0);
    check('exam attempt saved', A.S().exams.length === 1);
  }
  // progress + export
  A.setTab('progress');
  check('progress table', $$('table').length >= 1 && !!$('#exportbtn'));
  if (hasLessons) check('progress shows the lesson column', $('#app').textContent.indexOf(A.t('thLesson')) >= 0 && $('#app').textContent.indexOf(A.t('readYes')) >= 0);
  check('progress lists the mixed quiz set', $('#app').textContent.indexOf(A.t('otherSets')) >= 0 && $('#app').textContent.indexOf(A.t('setAllShort')) >= 0);
  check('page language and direction set', document.documentElement.lang === (A.D.lang || 'en') && document.documentElement.dir === (A.D.dir || 'ltr'));
  var persisted = JSON.parse(localStorage.getItem('sgt:' + D.id) || 'null');
  check('progress persisted to localStorage', !!persisted && Object.keys(persisted.cards).length >= 1);
  // markdown escaping
  check('no raw script injection in stem', !/<script/i.test(document.getElementById('app').innerHTML));
} catch (e) { out.push('FAIL exception: ' + e.message); ok = false; }
tail.catch(function(e){ out.push('FAIL exception (async): ' + (e && e.message || e)); ok = false; }).then(function(){
  var pre = document.createElement('pre'); pre.id = 'selftest'; pre.textContent = (ok ? 'SELFTEST OK\n' : 'SELFTEST FAILED\n') + out.join('\n');
  document.body.appendChild(pre);
});
})();
</script>'''


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('unit'); ap.add_argument('--out'); ap.add_argument('--title'); ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--no-diagrams', action='store_true', help='do not draw Mermaid diagrams (show their text instead)')
    ap.add_argument('--no-lessons', action='store_true', help='leave the Lesson tab out')
    a = ap.parse_args()
    out = a.out or default_out(a.unit)
    data, problems = build(a.unit, a.title, out, diagrams=not a.no_diagrams, lessons=not a.no_lessons)
    for p in problems:
        print('WARN', p, file=sys.stderr)
    if not any(c['questions'] for c in data['chapters']):
        sys.exit('no questions found: is this a unit folder whose chapter folders hold 03-quiz.md and 04-answer-key.md?')
    blob = json.dumps(data, ensure_ascii=False).replace('</', '<\\/').replace('<!--', '<\\u0021--')
    sample = [
        {'id': 'n1', 'quote': 'puddle  in a\nschool yard', 'note': 'Line one\n## not a heading\n> not a quote\nend --> done', 'sec': '1. What happens?',
         'start': 4, 'end': 30, 'prefix': 'One ', 'suffix': 'ory', 'ts': 1700000000000},
        {'id': 'n2', 'quote': '\u00e9 \u00fcn\u00efcode "q" <b>', 'note': '', 'sec': '', 'start': 100, 'end': 110, 'prefix': 'a-->b', 'suffix': 'x', 'ts': 1700000000001}]
    md = _notes.render('Notes: Ch. 1 Test', sample)
    fixture = json.dumps({'title': 'Notes: Ch. 1 Test', 'notes': sample, 'md': md, 'parsed': _notes.parse(md), 'hash': _notes.fnv(md)}, ensure_ascii=False).replace('</', '<\\/')
    page = read(TEMPLATE).replace('__TITLE__', re.sub(r'[<>&]', '', data['title'])).replace('__DATA__', blob).replace('__SELFTEST__', SELFTEST.replace('__NOTES_FIXTURE__', fixture) if a.selftest else '')
    open(out, 'w', encoding='utf-8').write(page)
    nq = sum(len(c['questions']) for c in data['chapters'])
    extra = []
    if data['final']: extra.append(f'{len(data["final"]["questions"])} checkpoint')
    if data['exam']: extra.append(f'{len(data["exam"]["questions"])} exam questions')
    nl = sum(1 for c in data['chapters'] if c.get('lesson'))
    nd = sum(c['lesson']['html'].count('<svg') for c in data['chapters'] if c.get('lesson'))
    nm = sum(c['lesson']['html'].count('data-t="diagramMissing"') for c in data['chapters'] if c.get('lesson'))
    print(f'wrote {out}: {len(data["chapters"])} chapters, {nl} lessons ({nd} diagrams drawn' + (f', {nm} shown as text: install mermaid-cli to draw them' if nm else '') + f'), {nq} questions, '
          f'{sum(len(c["cards"]) for c in data["chapters"])} flashcards' + ''.join(', ' + e for e in extra)
          + (f'; {len(problems)} warning(s)' if problems else ''))


if __name__ == '__main__':
    main()
