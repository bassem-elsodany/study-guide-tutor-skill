#!/usr/bin/env python3
"""Print a dated spaced-review plan.

Usage: review_schedule.py --start 2026-11-17 --exam 2026-12-20 [--chapters 43] [--per-day 2]

Study days walk through the chapters (lesson, quiz, review). Each chapter's misses come back the
next day, 3 days later, a week later and two weeks later (retake with fresh variants). The last
10 days before the exam are reserved for cumulative quizzes, domain exams, one mock exam and the
revisit list. Output is Markdown; paste it into score-tracker.md or the domain README.
"""
import argparse, datetime as dt

ap = argparse.ArgumentParser()
ap.add_argument('--start', required=True); ap.add_argument('--exam', required=True)
ap.add_argument('--chapters', type=int, default=20); ap.add_argument('--per-day', type=int, default=2)
a = ap.parse_args()
s = dt.date.fromisoformat(a.start); e = dt.date.fromisoformat(a.exam)
days = (e - s).days
if days < 7: raise SystemExit('Less than a week: use cram mode (cram sheet, flashcards, one mock exam, revisit list).')
tail = min(10, days // 3)
study_days = days - tail
need = -(-a.chapters // a.per_day)
if need > study_days: print(f'Note: {a.chapters} chapters at {a.per_day}/day needs {need} days but only {study_days} are available; raise --per-day.\n')
plan = {}
def add(d, t): plan.setdefault(d, []).append(t)
for i in range(a.chapters):
    d0 = s + dt.timedelta(days=min(i // a.per_day, study_days - 1))
    c = i + 1
    add(d0, f'Chapter {c}: read the lesson at-a-glance block, quiz, review misses (full lesson only if unclear)')
    for off, what in ((1, 'retake misses (fresh variants)'), (3, 'retake misses + flashcards'), (7, 'cumulative mixed quiz including chapter'), (14, 'flashcards of misses')):
        d = d0 + dt.timedelta(days=off)
        if d < e - dt.timedelta(days=tail): add(d, f'Chapter {c}: {what}')
for k in range(tail):
    d = e - dt.timedelta(days=tail - k)
    task = ['Domain exam (timed) for the first domain', 'Review the exam key; update the revisit list', 'Domain exam (timed) for the next domain',
            'Revisit list and revisit flashcards', 'Cram sheet pass', 'Mock exam (all domains, timed)', 'Review the mock exam key',
            'Revisit list again', 'Light review: cram sheets only', 'Rest, short flashcard pass'][k % 10]
    add(d, task)
print('| Date | Do |\n|---|---|')
d = s
while d <= e:
    print(f"| {d.isoformat()} | {'; '.join(plan.get(d, ['Rest or catch-up'])) if d != e else 'EXAM DAY'} |")
    d += dt.timedelta(days=1)
