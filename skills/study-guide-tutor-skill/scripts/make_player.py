#!/usr/bin/env python3
"""Build one self-contained interactive study player (a single HTML file) from a generated course.

Usage: make_player.py UNIT_DIR [--out FILE] [--title TEXT] [--selftest]

UNIT_DIR is any folder that directly holds chapter-NN-slug/ folders (and optionally 00-overview/): the course
folder of a flat course, or one module, week, part, domain ... of a grouped one. Build one player per unit. For every chapter it
reads 03-quiz.md + 04-answer-key.md (questions, the key, a "why each wrong option is wrong" line per option, the hint,
the source location) and 02-flashcards.csv; from 00-overview/ it reads the exam (07-exam.md + 08-exam-key.md; the older 07-unit-exam / 07-domain-exam names too) and the checkpoint
quiz (03 + 04) when present. The result opens by double-click in any browser: no install, no server, no network.

The player has four modes: Quiz (click or press A-D, instant feedback with the reason every wrong option is wrong,
optional hint, source location, retake of misses), Flashcards (flip, "knew it / missed it", spaced boxes with due
dates), Exam (timed, no feedback until submit, results by chapter, review of misses) and Progress (scores, boxes,
misses, "Download my results" as JSON for the tutor). Progress lives only in the browser (localStorage).

Default output: UNIT_DIR/00-overview/09-study-player.html (or UNIT_DIR/study-player.html without 00-overview).
--selftest appends a scripted click-through to the page (for tests only; do not ship that file).
Questions that refer to other options by letter ("both A and B", "all of the above") are never reshuffled.
"""
import argparse, csv, glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _layout

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


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-') or 'course'


def build(unit, title=None):
    global LABELS
    unitdir = os.path.abspath(unit)
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
        chapters.append({'n': n, 'title': lesson_title(chdir, n), 'questions': qs, 'cards': cards})
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
            'lang': lang, 'dir': direction, 'ui': {k: v for k, v in cfg.get('ui', {}).items() if isinstance(v, str)}}
    return data, problems


SELFTEST = r'''<script>
(function(){
var out = [], ok = true;
function check(n, c){ out.push((c ? 'PASS ' : 'FAIL ') + n); if (!c) ok = false; }
function $(s){ return document.querySelector(s); }
function $$(s){ return Array.prototype.slice.call(document.querySelectorAll(s)); }
function click(el){ el.click(); }
try {
  var A = window.__sgt, D = A.D;
  check('data has chapters', D.chapters.length > 0);
  check('tabs rendered', $$('#tabs button').length >= 3);
  // quiz: start first chapter set
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
  check('progress lists the mixed quiz set', $('#app').textContent.indexOf(A.t('otherSets')) >= 0 && $('#app').textContent.indexOf(A.t('setAllShort')) >= 0);
  check('page language and direction set', document.documentElement.lang === (A.D.lang || 'en') && document.documentElement.dir === (A.D.dir || 'ltr'));
  var persisted = JSON.parse(localStorage.getItem('sgt:' + D.id) || 'null');
  check('progress persisted to localStorage', !!persisted && Object.keys(persisted.cards).length >= 1);
  // markdown escaping
  check('no raw script injection in stem', !/<script/i.test(document.getElementById('app').innerHTML));
} catch (e) { out.push('FAIL exception: ' + e.message); ok = false; }
var pre = document.createElement('pre'); pre.id = 'selftest'; pre.textContent = (ok ? 'SELFTEST OK\n' : 'SELFTEST FAILED\n') + out.join('\n');
document.body.appendChild(pre);
})();
</script>'''


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('unit'); ap.add_argument('--out'); ap.add_argument('--title'); ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    data, problems = build(a.unit, a.title)
    for p in problems:
        print('WARN', p, file=sys.stderr)
    if not any(c['questions'] for c in data['chapters']):
        sys.exit('no questions found: is this a unit folder whose chapter folders hold 03-quiz.md and 04-answer-key.md?')
    blob = json.dumps(data, ensure_ascii=False).replace('</', '<\\/').replace('<!--', '<\\!--')
    page = read(TEMPLATE).replace('__TITLE__', re.sub(r'[<>&]', '', data['title'])).replace('__DATA__', blob).replace('__SELFTEST__', SELFTEST if a.selftest else '')
    out = a.out or (os.path.join(a.unit, '00-overview', '09-study-player.html') if os.path.isdir(os.path.join(a.unit, '00-overview')) else os.path.join(a.unit, 'study-player.html'))
    open(out, 'w', encoding='utf-8').write(page)
    nq = sum(len(c['questions']) for c in data['chapters'])
    extra = []
    if data['final']: extra.append(f'{len(data["final"]["questions"])} checkpoint')
    if data['exam']: extra.append(f'{len(data["exam"]["questions"])} exam questions')
    print(f'wrote {out}: {len(data["chapters"])} chapters, {nq} questions, '
          f'{sum(len(c["cards"]) for c in data["chapters"])} flashcards' + ''.join(', ' + e for e in extra)
          + (f'; {len(problems)} warning(s)' if problems else ''))


if __name__ == '__main__':
    main()
