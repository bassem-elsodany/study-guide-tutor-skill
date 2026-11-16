#!/usr/bin/env python3
"""Generate templates/course.json: every label and every player string with its English default.

Usage: gen-course-template.py [--check]

A course in another language copies this file to its course root as `course.json`, sets "language" (a BCP-47 code such
as es, fr, ar) and translates the values. The keys are read from the code, not typed by hand:
  labels  _layout.DEFAULT_LABELS   (the structural words the gates look for, and the audience note's words)
  ui      the STR table of skills/study-guide-tutor-skill/assets/player.html   (the interactive player's text)
`--check` fails if templates/course.json is out of date, so a new label or string cannot be added without the template.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'skills', 'study-guide-tutor-skill', 'scripts'))
import _layout  # noqa: E402


def player_strings():
    t = open(os.path.join(ROOT, 'skills', 'study-guide-tutor-skill', 'assets', 'player.html'), encoding='utf-8').read()
    m = re.search(r'var STR = (\{.*?\n\});', t, re.S)
    return json.loads(m.group(1))


def build():
    return {'language': 'en',
            '_note': 'Copy to the course root as course.json. Set language to a BCP-47 code (es, fr, ar ...) and translate the values; keep the keys. Anything left out falls back to English.',
            'labels': dict(_layout.DEFAULT_LABELS), 'footer_checks': {}, 'ui': player_strings()}


if __name__ == '__main__':
    want = json.dumps(build(), ensure_ascii=False, indent=2) + '\n'
    path = os.path.join(ROOT, 'templates', 'course.json')
    if '--check' in sys.argv:
        have = open(path, encoding='utf-8').read() if os.path.exists(path) else ''
        if have != want:
            print('templates/course.json is out of date: run scripts/gen-course-template.py'); sys.exit(1)
        print('templates/course.json is up to date'); sys.exit(0)
    open(path, 'w', encoding='utf-8').write(want)
    print('wrote', path)
