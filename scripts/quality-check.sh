#!/usr/bin/env bash
# quality-check - compile every script, run each with --help, and run the gates on every example and fixture course
# (a flat course, a course grouped by module, one grouped by week with lecture folders, one nested term/week/session,
# and a Spanish course grouped by unidad with its own labels).
# Read-only except for a temporary copy of the sample course. Works with macOS bash 3.2 and Linux.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SK="$ROOT/skills/study-guide-tutor-skill/scripts"
fail=0
step() { echo "== $*"; }

step "python syntax"
python3 -m py_compile "$SK"/*.py "$ROOT"/scripts/*.py
find "$ROOT" -name "__pycache__" -type d -prune -exec rm -rf {} + 2>/dev/null || true

step "shell syntax"
for f in "$ROOT"/scripts/*.sh; do bash -n "$f"; done

step "every skill script answers --help"
for f in "$SK"/*.py; do
  if ! python3 -I "$f" --help >/dev/null 2>&1; then echo "FAIL --help: $f"; fail=1; fi
done

step "source readers: pdf (when an extractor is installed), pptx, docx, md, txt, html, epub, srt, vtt, images"
if python3 -I "$ROOT/tests/test-sources.py" >/tmp/sgt-src.out 2>&1; then echo "ok   $(grep -c '^PASS' /tmp/sgt-src.out) source checks passed ($(grep -c '^SKIP' /tmp/sgt-src.out) skipped)"; else cat /tmp/sgt-src.out; fail=1; fi
rm -f /tmp/sgt-src.out

step "course.json: language, labels and the gates that read them"
if python3 -I "$ROOT/tests/test-labels.py" >/tmp/sgt-lab.out 2>&1; then echo "ok   $(grep -c '^PASS' /tmp/sgt-lab.out) label checks passed"; else cat /tmp/sgt-lab.out; fail=1; fi
rm -f /tmp/sgt-lab.out
if python3 -I "$ROOT/scripts/gen-course-template.py" --check; then :; else fail=1; fi

step "lesson renderer: markdown to safe html"
if python3 -I "$ROOT/tests/test-markdown.py" >/tmp/sgt-md.out 2>&1; then echo "ok   $(grep -c '^ok' /tmp/sgt-md.out) lesson renderer checks passed"; else cat /tmp/sgt-md.out; fail=1; fi
rm -f /tmp/sgt-md.out

step "player data: independent of build order, example counts"
if python3 -I "$ROOT/tests/test-player-data.py" >/tmp/sgt-pd.out 2>&1; then echo "ok   $(grep -c '^PASS' /tmp/sgt-pd.out) player data checks passed"; else cat /tmp/sgt-pd.out; fail=1; fi
rm -f /tmp/sgt-pd.out

step "layout discovery: five different folder structures, found by content"
python3 -I - "$ROOT" "$SK" <<'PY' || fail=1
import os, sys
root, sk = sys.argv[1], sys.argv[2]
sys.path.insert(0, sk)
import _layout
want = {  # course -> {unit (relative): [chapter folders]}
    'examples/water-cycle/course': {'.': ['chapter-01-the-four-stages', 'chapter-02-where-the-water-goes']},
    'tests/fixtures/by-module': {'module-1': ['chapter-01-the-four-stages'], 'module-2': ['chapter-01-where-the-water-goes']},
    'tests/fixtures/by-week-and-lecture': {'week-01': ['lecture-01-the-four-stages'], 'week-02': ['lecture-01-where-the-water-goes']},
    'tests/fixtures/nested-terms': {'term-1/week-01': ['session-1-the-four-stages'], 'term-1/week-02': ['session-1-where-the-water-goes']},
    'tests/fixtures/spanish-course': {'unidad-1': ['capitulo-01-el-ciclo-del-agua']},
}
bad = 0
for course, expect in want.items():
    base = os.path.join(root, course)
    got = {os.path.relpath(u, base): [os.path.basename(c) for c in _layout.chapters_of(u)] for u in _layout.find_units(base)}
    ok = got == expect
    print(('ok   ' if ok else 'FAIL ') + course + ': ' + ', '.join(f'{k} -> {len(v)} chapter(s)' for k, v in got.items()))
    bad += not ok
sys.exit(1 if bad else 0)
PY

for FIX in examples/water-cycle/course tests/fixtures/by-module tests/fixtures/by-week-and-lecture tests/fixtures/nested-terms tests/fixtures/spanish-course; do
  step "gates pass on $FIX"
  SRC="$ROOT/$FIX"
  T="$(mktemp -d)"; cp -R "$SRC" "$T/course"; C="$T/course"
  for g in "add_toc.py $C --check" "audit_quiz.py $C" "check_bundle.py $C" "check_dump.py $C" "check_tricky.py $C" "check_findable.py $C"; do
    # shellcheck disable=SC2086
    if python3 -I "$SK/${g%% *}" ${g#* } >/tmp/sgt-gate.out 2>&1; then echo "ok   ${g%% *}"; else echo "FAIL ${g%% *}"; cat /tmp/sgt-gate.out; fail=1; fi
  done
  rm -rf "$T" /tmp/sgt-gate.out
done

step "interactive player self-test (skips without Chrome or Chromium)"
if ! "$ROOT/scripts/test-player.sh" >/tmp/sgt-player.out 2>&1; then cat /tmp/sgt-player.out; fail=1; else echo "ok   $(grep -c "SELFTEST OK" /tmp/sgt-player.out) player self-test(s) passed (or skipped without a browser)"; fi
rm -f /tmp/sgt-player.out

[[ $fail -eq 0 ]] && echo "RESULT: OK" || { echo "RESULT: FAILED"; exit 1; }
