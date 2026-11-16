#!/usr/bin/env python3
"""Build one timed exam per unit (or for the whole flat course) that covers every chapter.

Usage: make_exam.py UNIT_DIR [--count 40] [--seed 7] [--minutes-per-question 1.5] [--kind exam|unit-exam|domain-exam]

Draws questions from the chapter quizzes (03-quiz.md + 04-answer-key.md) in UNIT_DIR (any folder that directly holds chapter folders: a flat course, a module, a week, a domain ...):
  * every chapter gets at least 2 questions, the rest are shared in proportion to how many
    questions each chapter has, keeping each chapter's Medium/Hard mix
  * questions are shuffled across chapters (no chapter labels in the exam itself)
  * option letters are kept as written, so the answer-key explanations stay correct
Writes 00-overview/07-exam.md and 00-overview/08-exam-key.md (--kind unit-exam or domain-exam writes the older file names) (key table with
chapter and source, then the explanation of every question). Add banners afterwards with
apply_banner.py and run audit_quiz.py. Re-running overwrites both files.
"""
import argparse, glob, math, os, random, re
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import _layout

Q_RX = re.compile(r'\n\*\*Q(\d+) \(([^)]*)\)\.\*\* ')
KEYROW_RX = re.compile(r'^\| (\d+) \| \*\*([A-D])\*\* \| ([^|]*) \| ([^|]*) \|', re.M)
KEYBLK_RX = re.compile(r'\*\*Q(\d+): ([A-D])\.\*\* (.*?)(?=\n\n(?:<a id="q\d+"></a>\n)?\*\*Q|\n\n---|\Z)', re.S)


def load_chapter(ch):
    qp = next((ch + n for n in ('03-quiz.md', 'quiz.md') if os.path.exists(ch + n)))
    kp = next((ch + n for n in ('04-answer-key.md', 'answer-key.md') if os.path.exists(ch + n)))
    s = open(qp).read(); parts = Q_RX.split(s)
    qs = {}
    for i in range(1, len(parts), 3):
        body = parts[i + 2]
        body = re.split(r'\n\n---', body)[0].strip('\n')
        qs[int(parts[i])] = (parts[i + 1].split(',')[0].strip(), body)
    k = open(kp).read()
    rows = {int(a): (b, d.strip(), src.strip()) for a, b, d, src in KEYROW_RX.findall(k)}
    blocks = {int(m.group(1)): m.group(3).rstrip() for m in KEYBLK_RX.finditer(k)}
    return [(n, d, body, rows[n][0], rows[n][2], blocks[n]) for n, (d, body) in sorted(qs.items())]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('unit'); ap.add_argument('--kind', choices=['exam', 'unit-exam', 'domain-exam'], default='exam'); ap.add_argument('--count', type=int, default=40)
    ap.add_argument('--seed', type=int, default=7); ap.add_argument('--minutes-per-question', type=float, default=1.5)
    a = ap.parse_args()
    L = _layout.labels(a.unit)   # wording of the exam text comes from the course's labels (course.json), English by default
    label = {'exam': L['exam_label'], 'unit-exam': 'Unit ' + L['exam_label'], 'domain-exam': 'Domain ' + L['exam_label']}[a.kind]
    qn, kn = {'exam': ('07-exam.md', '08-exam-key.md'), 'unit-exam': ('07-unit-exam.md', '08-unit-exam-key.md'), 'domain-exam': ('07-domain-exam.md', '08-domain-exam-key.md')}[a.kind]
    dom = a.unit.rstrip('/'); rnd = random.Random(a.seed)
    chapters = [c + '/' for c in _layout.chapters_of(dom)]
    data = {c: load_chapter(c) for c in chapters}
    total = sum(len(v) for v in data.values())
    count = min(a.count, total)
    alloc = {c: max(2, round(count * len(v) / total)) for c, v in data.items()}
    while sum(alloc.values()) > count:
        big = max(alloc, key=lambda c: alloc[c] - 2 * 0 if alloc[c] > 2 else -1); alloc[big] -= 1
    while sum(alloc.values()) < count:
        c = max(data, key=lambda c: len(data[c]) - alloc[c]); alloc[c] += 1
    picked = []
    for ci, (c, items) in enumerate(data.items(), 1):
        want = min(alloc[c], len(items))
        hard = [x for x in items if x[1] == L['hard']]; med = [x for x in items if x[1] != L['hard']]
        nh = round(want * len(hard) / len(items)); nm = want - nh
        sel = rnd.sample(hard, min(nh, len(hard))) + rnd.sample(med, min(nm, len(med)))
        rest = [x for x in items if x not in sel]
        while len(sel) < want and rest:
            sel.append(rest.pop(rnd.randrange(len(rest))))
        picked += [(ci, x) for x in sel]
    rnd.shuffle(picked)
    # avoid a run of three identical key letters by swapping with a later item
    for i in range(2, len(picked)):
        if picked[i][1][3] == picked[i - 1][1][3] == picked[i - 2][1][3]:
            for j in range(i + 1, len(picked)):
                if picked[j][1][3] != picked[i][1][3]:
                    picked[i], picked[j] = picked[j], picked[i]; break
    title = re.search(r'^# (.+)$', open(os.path.join(dom, 'README.md')).read(), re.M).group(1) if os.path.exists(os.path.join(dom, 'README.md')) else os.path.basename(dom)
    n = len(picked); minutes = int(math.ceil(n * a.minutes_per_question / 5.0) * 5)
    per = ', '.join(L['exam_coverage_item'].format(n=ci, count=sum(1 for c, _ in picked if c == ci)) for ci in range(1, len(chapters) + 1))
    ex = ' '.join(f'{i}{picked[i - 1][1][3]}' for i in range(1, 4))
    q = (f'# {title}: {label}\n\n' + L['exam_intro'].format(n=n, minutes=minutes, example=ex, key_file=kn) + '\n\n'
         + L['exam_mixed'].format(coverage=per) + '\n\n---\n')
    for i, (ci, (num, d, body, key, src, expl)) in enumerate(picked, 1):
        q += f'\n**Q{i} ({d}).** {body}\n\n---\n'
    cols = L['exam_key_columns'].split('|')
    k = (f'# {title}: {label} Key {L["exam_key_suffix"]}\n\n' + L['exam_key_intro'] + '\n\n'
         + '| ' + ' | '.join(cols) + ' |\n|---|---|---|---|\n')
    for i, (ci, (num, d, body, key, src, expl)) in enumerate(picked, 1):
        k += f'| {i} | **{key}** | {ci} | {src} |\n'
    k += '\n---\n'
    for i, (ci, (num, d, body, key, src, expl)) in enumerate(picked, 1):
        k += f'\n**Q{i}: {key}.** {expl}\n'
    out = os.path.join(dom, '00-overview'); os.makedirs(out, exist_ok=True)
    open(os.path.join(out, qn), 'w').write(q)
    open(os.path.join(out, kn), 'w').write(k)
    print(f'{dom}: {n} questions, {minutes} min; {per}')


if __name__ == '__main__':
    main()
