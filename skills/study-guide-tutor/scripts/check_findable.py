#!/usr/bin/env python3
"""Gate: can a student pass the quiz from the lesson's at-a-glance block, without the quiz teaching it?

Usage: check_findable.py ROOT_OR_CHAPTER_DIR [--min-glance 0.5] [--min-lesson 0.6] [--predict-overlap 0.25]

For every chapter (01-lesson.md + 03-quiz.md + 04-answer-key.md) it checks
  findable   the content words of each question's correct option appear in the at-a-glance block
             (at least --min-glance of them); a miss means the exam fact is not on the page a student reads first
  covered    the same words appear somewhere in the lesson (at least --min-lesson); a miss means the
             lesson does not teach it at all
  predicts   no Predict check in the lesson shares more than --predict-overlap of its 7-word phrases
             with the quiz (a copied scenario makes the quiz test memory of an answer just seen)
Heuristic by word overlap: paraphrased answers can false-alarm, so confirm by reading before rewriting.
Exit code 1 if anything fails.
"""
import argparse, glob, os, re, sys

STOP = set("the a an of to in and or is are was were be as for with by on at that this it its from which what who not no only than then into per vs".split())


def words(t): return set(w for w in re.findall(r"[a-z0-9][a-z0-9'%.-]+", t.lower()) if w not in STOP and len(w) > 2)
def norm(t): return re.findall(r"[a-z0-9][a-z0-9'%.-]*", re.sub(r'<[^>]+>|\*|`|\|', '', t.lower()))
def sh(w, n=7): return {tuple(w[i:i + n]) for i in range(max(0, len(w) - n + 1))}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('root')
    ap.add_argument('--min-glance', type=float, default=0.5); ap.add_argument('--min-lesson', type=float, default=0.6)
    ap.add_argument('--predict-overlap', type=float, default=0.25)
    a = ap.parse_args(); bad = total = 0
    root = a.root.rstrip('/')
    chapters = [root + '/'] if os.path.exists(os.path.join(root, '01-lesson.md')) else sorted(glob.glob(os.path.join(root, '**', 'chapter-*/'), recursive=True))
    for ch in chapters:
        if not all(os.path.exists(ch + f) for f in ('01-lesson.md', '03-quiz.md', '04-answer-key.md')): continue
        L = open(ch + '01-lesson.md').read(); q = open(ch + '03-quiz.md').read(); k = open(ch + '04-answer-key.md').read()
        g = re.search(r'<!-- glance -->.*?<!-- /glance -->', L, re.S)
        gw = words(g.group(0)) if g else set(); lw = words(L); qs = sh(norm(q))
        keys = dict(re.findall(r'\| (\d+) \| \*\*([A-D])\*\*', k)); name = os.path.basename(ch.rstrip('/'))[:30]
        for m in re.finditer(r'<summary><b>Predict:</b>(.*?)</summary>', L, re.S):
            s = sh(norm(m.group(1)))
            if s and len(s & qs) / len(s) > a.predict_overlap:
                bad += 1; print(f'COPIED PREDICT  {name}: {m.group(1).strip()[:70]}')
        for m in re.finditer(r'\*\*Q(\d+) \([^)]*\)\.\*\*(.*?)(?=\n---|\Z)', q, re.S):
            num, body = m.group(1), m.group(2); key = keys.get(num)
            o = re.search(r'(?m)^[-*]?\s*\*{0,2}' + key + r'[.)]\*{0,2}\s*(.+)$', body) if key else None
            if not o: continue
            total += 1; ow = words(o.group(1))
            if not ow: continue
            if len(ow & lw) / len(ow) < a.min_lesson: bad += 1; print(f'NOT TAUGHT      {name} Q{num}: {o.group(1)[:70]}')
            elif len(ow & gw) / len(ow) < a.min_glance: bad += 1; print(f'NOT IN GLANCE   {name} Q{num}: {o.group(1)[:70]}')
    if total == 0:
        print('RESULT: FAIL (0 questions found: wrong path, or the quiz/key files are missing)'); sys.exit(1)
    print(f'RESULT: {"FAIL" if bad else "OK"} ({bad} problems over {total} questions)'); sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
