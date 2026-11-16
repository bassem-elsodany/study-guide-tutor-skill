#!/usr/bin/env python3
"""Add ONE combined audience note, at the END of every study markdown file (no banner at the top).

Usage: apply_banner.py COURSE_ROOT [--texts references/banner-texts.json] [--profile-version 1] [--refresh]

The footer is appended after a '---' between <!-- audience-banner:end --> markers and states, in one
high-level paragraph: whom the file is written for, what that changed in this kind of file, that facts
never change with the level, and how to ask for a different level (with the profile link, computed
relative to learner-profile.md at the course root). File type comes from the file name
(03-quiz.md -> quiz, 99-fact-ledger.md -> fact-ledger, README.md -> README, ...).

Wording in another language: a course.json at the course root can set `labels` (footer words) and `footer_checks`
(the per-file-type sentence, keyed like banner-texts.json: lesson, quiz, answer-key ...). See _layout.py.

Audience wording: taken from the line "Audience statement: ..." in learner-profile.md at the course root
(written during intake); without it the neutral default in references/banner-texts.json is used.

Migration: a file that still has the old two-part banner (<!-- audience-banner:top --> block plus a
"**Audience check:**" footer) is converted: the top block is removed and the footer is rebuilt from
the old check text, so nothing the writer customised is lost. Idempotent: a file whose footer
already starts "**Audience:**" is left alone except that its profile link is re-pointed (links go stale
when files move); use --refresh to rewrite its check text from the texts file.
"""
import argparse, glob, json, os, re
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import _layout

KINDS = ['fact-ledger', 'lesson', 'quiz', 'answer-key', 'review', 'concept-map', 'cram-sheet',
         'final-quiz-key', 'final-quiz', 'domain-exam-key', 'domain-exam', 'unit-exam-key', 'unit-exam', 'exam-key', 'exam', 'score-tracker', 'revisit-list', 'mock-exam-key', 'mock-exam', 'README']
TOP = re.compile(r'<!-- audience-banner:top -->.*?<!-- /audience-banner -->\n*', re.S)
END = re.compile(r'\n*(?:---\n+)?<!-- audience-banner:end -->\n(.*?)\n<!-- /audience-banner -->\n*', re.S)
DUP = re.compile(r'^written for a beginner(?: with a technical background)?[.:]\s*', re.I)


def kind_of(path):
    n = os.path.basename(path)
    n = re.sub(r'^\d+-', '', n).replace('.md', '')
    n = re.sub(r'-\d+$', '', n)  # mock-exam-01 -> mock-exam
    if n.startswith('mock-exam') and n.endswith('key'): return 'mock-exam-key'
    if n == 'domain-exam-key': return 'domain-exam-key'
    return n if n in KINDS else None


def sentence(t):
    t = DUP.sub('', t.strip())
    t = t[:1].upper() + t[1:]
    return t if t.endswith(('.', '!', '?')) else t + '.'


def footer(gen, check, rel, version, L=None):
    L = L or _layout.DEFAULT_LABELS   # the words of the footer come from the course's labels (course.json)
    return ("---\n\n<!-- audience-banner:end -->\n"
            f"> **{L['footer_audience']}:** {L['footer_written_for']} {gen.strip().rstrip(chr(46))}. {sentence(check)} "
            f"{L['footer_facts']} {L['footer_wrong_level']} "
            f"{L['footer_profile']}: [`learner-profile.md`]({rel}), {L['footer_version']} {version}.\n"
            "<!-- /audience-banner -->\n")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('root')
    ap.add_argument('--texts', default=os.path.join(os.path.dirname(__file__), '..', 'references', 'banner-texts.json'))
    ap.add_argument('--profile-version', default='1')
    ap.add_argument('--refresh', action='store_true', help='rewrite the check text of existing footers from the texts file')
    a = ap.parse_args()
    T = json.load(open(a.texts)); gen = T['generated_for']; types = T['types']
    root = os.path.abspath(a.root); n = 0
    L = _layout.labels(root)
    cfg_checks = _layout.course_config(root).get('footer_checks', {})  # per file type wording, for a course in another language
    prof = os.path.join(root, 'learner-profile.md')
    if os.path.exists(prof):  # one line in the profile: "Audience statement: <who the files are written for>"
        m = re.search(r'(?mi)^\**' + re.escape(L['audience_statement']) + r':?\**:?\s*(.+)$', open(prof, encoding='utf-8').read())
        if m: gen = m.group(1).strip()
    for f in glob.glob(os.path.join(root, '**', '*.md'), recursive=True):
        if 'graphify-out' in f or os.path.basename(f) in ('CLAUDE.md',) or os.path.abspath(f) == os.path.join(root, 'README.md'):
            continue
        k = kind_of(f)
        if not k or k not in types: continue
        s = open(f).read()
        rel = os.path.relpath(os.path.join(root, 'learner-profile.md'), os.path.dirname(f))
        m = END.search(s)
        version = a.profile_version
        vm = re.search(r'version (\d+)', s[:s.find('<!-- /audience-banner -->')] if 'audience-banner:top' in s else (m.group(1) if m else ''))
        if vm: version = vm.group(1)
        if m and m.group(1).lstrip('> ').startswith('**' + L['footer_audience'] + ':**') and not a.refresh and 'audience-banner:top' not in s:
            # already in the new format: only re-point the profile link (it goes stale when files move)
            fixed = re.sub(r'(' + re.escape(L['footer_profile']) + r': \[`learner-profile\.md`\]\()[^)]*(\))', lambda mm: mm.group(1) + rel + mm.group(2), s)
            if fixed != s:
                open(f, 'w').write(fixed); n += 1
            continue
        if m:
            old = m.group(1)
            cm = re.search(r'\*\*Audience check:\*\*\s*(.*)', old)
            check = cfg_checks.get(k) or (types[k]['check'] if a.refresh or not cm else cm.group(1))
            body = END.sub('\n', TOP.sub('', s)).rstrip('\n') + '\n\n' + footer(gen, check, rel, version, L)
        else:
            if not s.startswith('# '): continue
            body = TOP.sub('', s).rstrip('\n') + '\n\n' + footer(gen, cfg_checks.get(k) or types[k]['check'], rel, version, L)
        body = re.sub(r'\n{3,}', '\n\n', body)
        open(f, 'w').write(body); n += 1
    print('footer written in', n, 'files')


if __name__ == '__main__':
    main()
