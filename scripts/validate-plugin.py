#!/usr/bin/env python3
"""Offline validator for this plugin repository (CI runs it; `claude plugin validate . --strict` is the official check).

Usage: validate-plugin.py [ROOT] [--self-test]

Checks: manifests parse and carry the version in VERSION; every skills/*/SKILL.md has frontmatter (name equals the
folder, kebab-case, <= 64 chars, description present, <= 1024 chars, no angle brackets, < 500 lines); every agents/*.md
has name, description, a tools LIST and a model; every commands/*.md has description and allowed-tools; no CLAUDE.md at
the root; relative markdown links resolve; and hygiene: no personal data, absolute paths, machine names or course
names anywhere in tracked text files. --self-test proves the checks still fire on a deliberately broken tree.
"""
import json, os, re, sys, tempfile, shutil

TEXT = ('.md', '.json', '.py', '.sh', '.yml', '.yaml', '.mmd', '.csv', '.txt')
# patterns that must never appear in the repository (built from parts so this file does not trip itself)
FORBIDDEN = [
    (re.compile('/' + 'Users/'), 'absolute macOS home path'),
    (re.compile('/' + r'home/[a-z]'), 'absolute Linux home path'),
    (re.compile(r'[A-Za-z]:\\' + 'Users'), 'absolute Windows user path'),
    (re.compile('private' + '/tmp|/var/' + 'folders'), 'scratch or temp path'),
    (re.compile(r'[\w.+-]+@(?:gmail|hotmail|outlook|yahoo)\.com'), 'personal email address'),
    (re.compile('(?i)aig' + r'p\b|ia' + r'pp\b'), 'course or certification name from a private course'),
]
FRONT = re.compile(r'\A---\n(.*?)\n---\n', re.S)


def frontmatter(text):
    m = FRONT.match(text)
    return (m.group(1), text[m.end():]) if m else (None, text)


def keys(fm):
    return dict((m.group(1), m.group(2)) for m in re.finditer(r'(?m)^([A-Za-z][\w-]*):\s*(.*)$', fm))


def desc_text(fm):
    m = re.search(r'(?ms)^description:\s*(>|\|)?\s*\n?(.*?)(?=^\w[\w-]*:|\Z)', fm)
    return re.sub(r'\s+', ' ', m.group(2)).strip().strip('"') if m else ''


def files(root):
    for d, ds, fs in os.walk(root):
        ds[:] = [x for x in ds if x not in ('.git', '__pycache__', 'node_modules')]
        for f in fs:
            if f.endswith(TEXT) or f in ('VERSION', '.gitignore', '.gitattributes', 'LICENSE'):
                yield os.path.join(d, f)


def validate(root):
    errs = []
    def e(msg): errs.append(msg)
    ver = open(os.path.join(root, 'VERSION')).read().strip() if os.path.exists(os.path.join(root, 'VERSION')) else None
    if not ver: e('VERSION file missing')
    for m in ('.claude-plugin/plugin.json', '.claude-plugin/marketplace.json'):
        p = os.path.join(root, m)
        try: j = json.load(open(p))
        except Exception as x: e(f'{m}: {x}'); continue
        if ver and j.get('version') != ver: e(f'{m}: version {j.get("version")} != VERSION {ver}')
    if os.path.exists(os.path.join(root, 'CLAUDE.md')): e('CLAUDE.md at the repository root (not loaded by plugins; use AGENTS.md)')
    sk = os.path.join(root, 'skills')
    for name in sorted(os.listdir(sk)) if os.path.isdir(sk) else []:
        p = os.path.join(sk, name, 'SKILL.md')
        if not os.path.exists(p): continue
        t = open(p, encoding='utf-8').read(); fm, _ = frontmatter(t)
        if fm is None: e(f'{p}: frontmatter must start on line 1'); continue
        k = keys(fm)
        if k.get('name', '').strip('"') != name: e(f'{p}: name must equal the folder "{name}"')
        if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', name) or len(name) > 64: e(f'{p}: folder name not kebab-case or > 64')
        d = desc_text(fm)
        if not d: e(f'{p}: description missing')
        if len(d) > 1024: e(f'{p}: description {len(d)} chars (> 1024)')
        if '<' in d or '>' in d: e(f'{p}: description has angle brackets')
        if not re.search(r'(?i)use when', d): e(f'{p}: description should say "Use when ..."')
        if t.count('\n') >= 500: e(f'{p}: {t.count(chr(10))} lines (limit 500)')
    ag = os.path.join(root, 'agents')
    for f in sorted(os.listdir(ag)) if os.path.isdir(ag) else []:
        if not f.endswith('.md'): continue
        p = os.path.join(ag, f); fm, _ = frontmatter(open(p, encoding='utf-8').read())
        if fm is None: e(f'{p}: no frontmatter'); continue
        k = keys(fm)
        if k.get('name', '').strip('"') != f[:-3]: e(f'{p}: name must equal the file name')
        if not desc_text(fm): e(f'{p}: description missing')
        if not re.search(r'(?m)^tools:\s*\n(\s+- \S+\n?)+', fm + '\n'): e(f'{p}: tools must be a YAML list')
        if 'model' not in k: e(f'{p}: model missing')
    cm = os.path.join(root, 'commands')
    for f in sorted(os.listdir(cm)) if os.path.isdir(cm) else []:
        if not f.endswith('.md'): continue
        p = os.path.join(cm, f); fm, _ = frontmatter(open(p, encoding='utf-8').read())
        if fm is None: e(f'{p}: no frontmatter'); continue
        k = keys(fm)
        for need in ('description', 'allowed-tools'):
            if need not in k or not k[need].strip(): e(f'{p}: {need} missing')
    own = os.path.abspath(__file__)
    for p in files(root):
        if os.path.abspath(p) == own: continue
        try: t = open(p, encoding='utf-8').read()
        except Exception: continue
        rel = os.path.relpath(p, root)
        for rx, why in FORBIDDEN:
            if rx.search(t): e(f'{rel}: {why}')
        if p.endswith('.md') and not rel.startswith('templates' + os.sep):  # templates hold example links on purpose
            body = re.sub(r'`[^`\n]*`', '', re.sub(r'```.*?```', '', t, flags=re.S))  # links inside code spans are examples
            for m in re.finditer(r'\]\(([^)\s#]+)(?:#[^)]*)?\)', body):
                tgt = m.group(1)
                if tgt.startswith(('http', 'mailto:', '<', '$')) or '{' in tgt: continue
                if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(p), tgt))): e(f'{rel}: broken link {tgt}')
    return errs


def self_test():
    T = tempfile.mkdtemp()
    try:
        for d in ('skills/x', 'agents', 'commands', '.claude-plugin'): os.makedirs(os.path.join(T, d))
        open(T + '/VERSION', 'w').write('1.0.0\n')
        json.dump({'version': '9.9.9'}, open(T + '/.claude-plugin/plugin.json', 'w'))
        json.dump({'version': '1.0.0'}, open(T + '/.claude-plugin/marketplace.json', 'w'))
        open(T + '/skills/x/SKILL.md', 'w').write('---\nname: y\ndescription: <bad> no trigger\n---\n')
        open(T + '/agents/a.md', 'w').write('---\nname: a\ndescription: d\ntools: Read, Grep\n---\n')
        open(T + '/commands/c.md', 'w').write('---\ndescription: d\n---\n')
        open(T + '/CLAUDE.md', 'w').write('x')
        open(T + '/README.md', 'w').write('see [gone](missing.md) and ' + '/' + 'Users/someone/x and a@gmail' + '.com\n')
        errs = '\n'.join(validate(T))
        for needle in ('version 9.9.9', 'CLAUDE.md', 'name must equal', 'angle brackets', 'Use when', 'tools must be a YAML list', 'model missing', 'allowed-tools missing', 'broken link', 'absolute macOS', 'personal email'):
            if needle not in errs: print('SELF-TEST FAIL: did not catch:', needle); return 1
        print('self-test OK: every check fires on a broken tree'); return 0
    finally:
        shutil.rmtree(T, ignore_errors=True)


if __name__ == '__main__':
    if '--self-test' in sys.argv: sys.exit(self_test())
    root = next((a for a in sys.argv[1:] if not a.startswith('-')), '.')
    errs = validate(os.path.abspath(root))
    for x in errs: print('FAIL', x)
    print('RESULT: OK' if not errs else f'RESULT: {len(errs)} problem(s)')
    sys.exit(1 if errs else 0)
