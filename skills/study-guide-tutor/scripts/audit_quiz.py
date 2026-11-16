#!/usr/bin/env python3
"""Audit the quizzes of a study bundle.

Usage:
  audit_quiz.py ROOT [--target-low 0.20] [--target-high 0.40] [--margin 0.08] [--allow-easy]

ROOT is a domain folder (containing chapter-*/ and optionally 00-overview/) or a course
folder containing several domain-*/ folders.

Checks, per quiz file and key file pair:
  structure   four options A-D per question, labels, the "N questions" header matches
  key         key table rows and explanation blocks match the questions one to one
  why-wrong   every wrong option has an explanation bullet (grouped bullets such as
              "A, C and D ..." count), and every explanation has a "- Hint:" line
  difficulty  labels are Medium or Hard (use --allow-easy to permit Easy)
  letters     key letters are spread (no letter far from an equal share; no run of three)
  length      share of questions where the key is strictly the longest option stays within
              [target-low, target-high]; flags questions where the key is at least
              `margin` longer than the longest wrong option (a tell)
Exit code 1 when any ERROR is found; warnings do not fail.
"""
import argparse, glob, os, re, sys
from collections import Counter

Q_RX = re.compile(r'\n\*\*Q(\d+) \(([^)]*)\)\.\*\* ')
OPT_RX = re.compile(r'^- ([A-D])\. (.+)$', re.M)
KEYROW_RX = re.compile(r'^\| (\d+) \| \*\*([A-D])\*\* \|', re.M)
KEYBLK_RX = re.compile(r'\*\*Q(\d+): ([A-D])\.\*\* (.*?)(?=\n\n(?:<a id="q\d+"></a>\n)?\*\*Q|\n\n---|\Z)', re.S)
BULLET_RX = re.compile(r'^- ([A-D](?:(?:,\s*| and | & )[A-D])*)(?=[:\s])', re.M)


def parse_quiz(path):
    s = open(path).read()
    parts = Q_RX.split(s)
    hdr = re.search(r'^(\d+) questions', s, re.M)
    out = {}
    for i in range(1, len(parts), 3):
        n, label, body = int(parts[i]), parts[i + 1], parts[i + 2]
        out[n] = (label.split(',')[0].strip(), dict(OPT_RX.findall(body)))
    return out, (int(hdr.group(1)) if hdr else None)


def parse_key(path):
    s = open(path).read()
    rows = {int(a): b for a, b in KEYROW_RX.findall(s)}
    blocks = {}
    for m in KEYBLK_RX.finditer(s):
        body = m.group(3)
        letters = set()
        for g in BULLET_RX.findall(body):
            letters |= set(re.findall(r'[A-D]', g))
        blocks[int(m.group(1))] = (m.group(2), letters, '- Hint:' in body)
    return rows, blocks


def find_pairs(root):
    pairs = []
    domains = sorted(glob.glob(os.path.join(root, 'domain-*/')))
    bases = [d.rstrip('/') for d in domains] or [root.rstrip('/')]
    for b in bases:
        for c in sorted(glob.glob(os.path.join(b, 'chapter-*/'))):
            q = next((c + n for n in ('03-quiz.md', 'quiz.md') if os.path.exists(c + n)), c + '03-quiz.md')
            k = next((c + n for n in ('04-answer-key.md', 'answer-key.md') if os.path.exists(c + n)), c + '04-answer-key.md')
            pairs.append((q, k, True))
        for q, k in (('03-final-quiz.md', '04-final-quiz-key.md'), ('07-domain-exam.md', '08-domain-exam-key.md'), ('final-quiz.md', 'final-quiz-key.md')):
            qp = os.path.join(b, '00-overview', q)
            if os.path.exists(qp):
                pairs.append((qp, os.path.join(b, '00-overview', k), False))
        for m in sorted(glob.glob(os.path.join(b, '00-overview', 'mock-exam-*.md'))):
            if m.endswith('-key.md'):
                continue
            pairs.append((m, m.replace('.md', '-key.md'), False))
    return pairs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root')
    ap.add_argument('--target-low', type=float, default=0.20)
    ap.add_argument('--target-high', type=float, default=0.40)
    ap.add_argument('--margin', type=float, default=0.08)
    ap.add_argument('--allow-easy', action='store_true')
    a = ap.parse_args()
    errors, warns = [], []
    total = strict = 0
    letters = Counter(); diff = Counter(); flagged = []
    for qp, kp, is_chapter in find_pairs(a.root):
        rel = os.path.relpath(qp, a.root)
        if not os.path.exists(kp):
            errors.append((rel, 'missing key file ' + os.path.basename(kp))); continue
        q, hdr = parse_quiz(qp); rows, blocks = parse_key(kp)
        if is_chapter and hdr is not None and hdr != len(q):
            errors.append((rel, f'header says {hdr} questions, file has {len(q)}'))
        if set(q) != set(rows):
            errors.append((rel, f'key table rows {sorted(rows)} != questions {sorted(q)}'))
        if set(q) != set(blocks):
            errors.append((rel, f'key explanations {sorted(blocks)} != questions {sorted(q)}'))
        seq = []
        for n, (label, opts) in sorted(q.items()):
            if sorted(opts) != list('ABCD'):
                errors.append((rel, f'Q{n}: options are {sorted(opts)}')); continue
            if label not in ('Medium', 'Hard') and not (a.allow_easy and label == 'Easy'):
                errors.append((rel, f'Q{n}: difficulty label "{label}"'))
            diff[label] += 1
            key = rows.get(n)
            if key is None:
                continue
            if n in blocks and blocks[n][0] != key:
                errors.append((rel, f'Q{n}: table key {key} != explanation key {blocks[n][0]}'))
            if n in blocks:
                wrong = set('ABCD') - {key}
                missing = wrong - blocks[n][1]
                if missing or key in blocks[n][1]:
                    errors.append((rel, f'Q{n}: why-wrong coverage wrong (missing {sorted(missing)})'))
                if not blocks[n][2]:
                    errors.append((rel, f'Q{n}: no hint line'))
            L = {x: len(t) for x, t in opts.items()}
            longest_wrong = max(v for x, v in L.items() if x != key)
            total += 1; letters[key] += 1; seq.append(key)
            if L[key] > longest_wrong:
                strict += 1
                if L[key] >= longest_wrong * (1 + a.margin):
                    flagged.append((rel, n, key, L[key], longest_wrong))
        for i in range(len(seq) - 2):
            if seq[i] == seq[i + 1] == seq[i + 2]:
                warns.append((rel, f'run of three key letters "{seq[i]}" at Q{i + 1}-Q{i + 3}')); break
    print(f'questions {total}  difficulty {dict(diff)}  key letters {dict(sorted(letters.items()))}')
    share = strict / total if total else 0
    print(f'key strictly longest in {strict} ({share:.0%}); target {a.target_low:.0%}-{a.target_high:.0%}; '
          f'>= {a.margin:.0%} longer than the longest wrong option: {len(flagged)}')
    if total and not (a.target_low <= share <= a.target_high):
        warns.append(('ALL', f'key-longest share {share:.0%} outside target band'))
    if total:
        ideal = total / 4
        for L_, c in letters.items():
            if abs(c - ideal) > max(3, 0.25 * ideal):
                warns.append(('ALL', f'key letter {L_} appears {c} times (equal share would be {ideal:.0f})'))
    for f in flagged[:40]:
        warns.append((f[0], f'Q{f[1]}: key {f[2]} is {f[3]} chars vs longest wrong {f[4]} (length tell)'))
    for w in warns:
        print('WARN ', *w)
    for e in errors:
        print('ERROR', *e)
    print('RESULT:', 'FAIL' if errors else 'OK', f'({len(errors)} errors, {len(warns)} warnings)')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
