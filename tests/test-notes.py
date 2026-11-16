#!/usr/bin/env python3
"""Tests for the student's notes file (06-notes.md): the format round-trips, hand-written notes are read,
the player build picks the file up, and the file is left alone by the scripts that rewrite generated files."""
import os, subprocess, sys, tempfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SK = os.path.join(ROOT, 'skills', 'study-guide-tutor-skill', 'scripts')
sys.path.insert(0, SK)
import _notes, make_player

fails = []


def check(name, cond):
    print(('ok   ' if cond else 'FAIL ') + name)
    if not cond:
        fails.append(name)


sample = [
    {'id': 'n1', 'quote': 'puddle  in a\nschool yard', 'note': 'one\n## not a heading\n> not a quote\nend --> done', 'sec': '1. What?',
     'start': 4, 'end': 30, 'prefix': 'One ', 'suffix': 'ory', 'ts': 1700000000000},
    {'id': 'n2', 'quote': 'é ünïcode "q" <b>', 'note': '', 'sec': '', 'start': 100, 'end': 110, 'prefix': 'a-->b', 'suffix': 'x', 'ts': 1700000000001}]
md = _notes.render('Notes: test', sample)
back = _notes.parse(md)
check('render then parse gives the same notes (quote spacing normalised)',
      [(n['id'], n['note'], n['sec'], n['start'], n['prefix']) for n in back] == [(n['id'], n['note'], n['sec'], n['start'], n['prefix']) for n in sample]
      and back[0]['quote'] == 'puddle in a school yard' and back[1]['quote'] == sample[1]['quote'])
check('a note with --> in it cannot break out of its comment', md.count('<!-- note ') == 2 and '-->b' not in md.split('<!-- note ')[2].split(' -->')[0])
check('a note line starting with # or > is escaped, so it stays note text', '\n\\## not a heading\n' in md and '\n\\> not a quote\n' in md)
check('notes are written in lesson order', md.index('puddle') < md.index('code'))
check('the same notes always give the same file', _notes.render('Notes: test', list(reversed(sample))) == md)

hand = '# My notes\n\n## whatever\n\n> a quoted\n> line\n\nmy own words\n\n## second\n\nno quote here, so no note\n\n## third\n\n> only a highlight\n'
h = _notes.parse(hand)
check('hand-written notes are read: quote, text, an id made from the quote', len(h) == 2 and h[0]['quote'] == 'a quoted line' and h[0]['note'] == 'my own words'
      and h[0]['id'].startswith('h') and h[1]['note'] == '')
check('an empty or missing file has no notes', _notes.parse('') == [] and _notes.parse('# only a title\n') == [])
check('a damaged meta comment is ignored, the note is kept', len(_notes.parse('## x\n\n> q q\n\n<!-- note {broken -->\n')) == 1)
check('the content hash is FNV-1a over UTF-8', _notes.fnv('hello') == '4f9f2cab' and _notes.fnv('') == '811c9dc5')

fx = os.path.join(HERE, 'fixtures', 'by-module', 'module-1')
data, problems = make_player.build(fx, diagrams=False)
c1 = data['chapters'][0]
text = open(os.path.join(fx, 'chapter-01-the-four-stages', '06-notes.md'), encoding='utf-8').read()
check('the player build reads a chapter notes file', len(c1['notes']) == 1 and 'only warm air' in c1['notes'][0]['note'] and c1['notesHash'] == _notes.fnv(text)
      and c1['dir'] == 'chapter-01-the-four-stages')
check('a chapter without a notes file has none', make_player.build(os.path.join(HERE, 'fixtures', 'by-week-and-lecture', 'week-02'), diagrams=False)[0]['chapters'][0]['notes'] == [])

# the scripts that rewrite generated files leave the student's file alone
tmp = tempfile.mkdtemp()
try:
    dst = os.path.join(tmp, 'course')
    shutil.copytree(os.path.join(HERE, 'fixtures', 'by-module'), dst)
    nf = os.path.join(dst, 'module-1', 'chapter-01-the-four-stages', '06-notes.md')
    open(nf, 'w', encoding='utf-8').write(hand)
    for script in ('add_toc.py', 'apply_banner.py'):
        subprocess.run([sys.executable, os.path.join(SK, script), dst], capture_output=True, text=True)
    check('add_toc and apply_banner do not touch 06-notes.md', open(nf, encoding='utf-8').read() == hand)
    r = subprocess.run([sys.executable, os.path.join(SK, 'add_toc.py'), dst, '--check'], capture_output=True, text=True)
    check('add_toc --check does not ask for a table of contents in the notes file', 'notes' not in r.stdout)
finally:
    shutil.rmtree(tmp, ignore_errors=True)
sys.exit(1 if fails else 0)
