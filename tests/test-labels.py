#!/usr/bin/env python3
"""Test the course.json mechanism: language, labels and the gates that read them. Standard library only.

Checks that defaults are English, that a course.json overrides only what it sets, that it is found from any folder
below the course root, that right-to-left languages are recognised, that the letter-reference pattern follows the
course language (so "ambas A y B" is never reshuffled), and that the gates really use the labels: the Spanish sample
course passes with its course.json and FAILS the tricky-parts gate without it.
"""
import json, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, 'skills', 'study-guide-tutor', 'scripts')
sys.path.insert(0, SK)
import _layout, make_player  # noqa: E402

ES = os.path.join(ROOT, 'tests', 'fixtures', 'sample-spanish-course')
fails = []


def check(name, cond, detail=''):
    print(('PASS ' if cond else 'FAIL ') + name + ((' :: ' + str(detail)) if (detail and not cond) else ''))
    if not cond: fails.append(name)


def gate(script, path):
    r = subprocess.run([sys.executable, '-I', os.path.join(SK, script), path], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def main():
    d = tempfile.mkdtemp()
    check('no course.json: English defaults', _layout.labels(d)['hint'] == 'Hint' and _layout.language(d) == ('en', 'ltr'))
    os.makedirs(os.path.join(d, 'unit', 'chapter-01'))
    json.dump({'language': 'ar', 'labels': {'hint': 'تلميح'}}, open(os.path.join(d, 'course.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    deep = os.path.join(d, 'unit', 'chapter-01', '01-lesson.md')
    check('course.json is found from a file deep inside the course', _layout.find_config(deep) == os.path.join(d, 'course.json'))
    L = _layout.labels(deep)
    check('only the labels it sets are overridden', L['hint'] == 'تلميح' and L['rule'] == 'Rule')
    check('Arabic is right-to-left', _layout.language(deep) == ('ar', 'rtl'))
    for code, want in (('he', 'rtl'), ('fa-IR', 'rtl'), ('es', 'ltr'), ('zh-Hans', 'ltr')):
        json.dump({'language': code}, open(os.path.join(d, 'course.json'), 'w'))
        check(f'language {code} is {want}', _layout.language(d)[1] == want)
    # letter-reference detection follows the course language
    en = _layout.DEFAULT_LABELS['letter_ref_regex']
    es = json.load(open(os.path.join(ES, 'course.json'), encoding='utf-8'))['labels']['letter_ref_regex']
    import re
    check('English: "both A and B" is a letter reference', bool(re.search(en, 'Both A and B are correct')))
    check('English pattern ignores ordinary text', not re.search(en, 'Water evaporates when the sun heats it'))
    check('Spanish: "ambas A y B" is a letter reference', bool(re.search(es, 'Ambas A y B son correctas')))
    check('Spanish: "ninguna de las anteriores" is a letter reference', bool(re.search(es, 'Ninguna de las anteriores')))
    check('Spanish pattern ignores ordinary text', not re.search(es, 'El agua se evapora cuando el sol la calienta'))
    # the gates read the labels: same lesson, with and without its course.json
    code, out = gate('check_tricky.py', ES)
    check('Spanish course passes check_tricky with its course.json', code == 0, out[-200:])
    bare = os.path.join(d, 'bare'); shutil.copytree(ES, bare); os.remove(os.path.join(bare, 'course.json'))
    code, out = gate('check_tricky.py', bare)
    check('the same course FAILS check_tricky without course.json (English markers expected)', code != 0 and 'callouts' in out, out[-200:])
    code, out = gate('audit_quiz.py', bare)
    check('and FAILS audit_quiz (Spanish difficulty words are not English ones)', code != 0 and 'difficulty label' in out, out[-300:])
    data, problems = make_player.build(ES)
    check('player data carries language, text overrides and the audience statement', data['lang'] == 'es' and data['ui'].get('start') == 'Empezar' and data['audience'].startswith('una persona'))
    print('RESULT: OK' if not fails else f'RESULT: {len(fails)} failed: {fails}')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
