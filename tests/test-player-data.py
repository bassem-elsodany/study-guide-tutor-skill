#!/usr/bin/env python3
"""Test that the player reads a course whatever the order the files were built in. Standard library only.

The exam and key files get their <a id="qN"> anchors from the contents step (add_toc.py). A player built before that step
must still find every question, so this test removes the anchors from a copy of the example course and checks that the
same questions come out. It also checks the counts the README promises for the example.
"""
import os, re, shutil, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'skills', 'study-guide-tutor-skill', 'scripts'))
import make_player  # noqa: E402

fails = []


def check(name, cond, detail=''):
    print(('PASS ' if cond else 'FAIL ') + name + ((' :: ' + str(detail)) if (detail and not cond) else ''))
    if not cond: fails.append(name)


def main():
    ex = os.path.join(ROOT, 'examples', 'water-cycle', 'course')
    data, problems = make_player.build(ex)
    check('example course: 2 chapters, 8 questions, 6 exam questions', len(data['chapters']) == 2 and sum(len(c['questions']) for c in data['chapters']) == 8 and data['exam'] and len(data['exam']['questions']) == 6, problems)
    check('example course: title comes from its README', data['title'] == 'The Water Cycle', data['title'])
    d = tempfile.mkdtemp(); c = os.path.join(d, 'c'); shutil.copytree(ex, c)
    for root, _, files in os.walk(c):
        for f in files:
            if f.endswith('.md'):
                p = os.path.join(root, f); t = open(p, encoding='utf-8').read()
                open(p, 'w', encoding='utf-8').write(re.sub(r'<a id="q\d+"></a>\n', '', t))
    d2, p2 = make_player.build(c)
    same = [q['stem'] for ch in data['chapters'] for q in ch['questions']] == [q['stem'] for ch in d2['chapters'] for q in ch['questions']]
    check('without any anchors the chapter questions are the same', same, p2)
    check('without any anchors the exam is still found, with its keys', d2['exam'] and len(d2['exam']['questions']) == 6 and all(q['key'] in q['opts'] and q['why'] for q in d2['exam']['questions']), p2)
    print('RESULT: OK' if not fails else f'RESULT: {len(fails)} failed: {fails}')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
