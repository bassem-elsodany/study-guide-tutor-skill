#!/usr/bin/env bash
# quality-check - compile every script, run each with --help, and run the gates on both sample courses
# (a flat course with no units, a course grouped into modules, and a Spanish course with its own labels).
# Read-only except for a temporary copy of the sample course. Works with macOS bash 3.2 and Linux.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SK="$ROOT/skills/study-guide-tutor/scripts"
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

step "layout discovery: flat course, grouped course, and a chapter folder in another language"
UN="$(python3 -I -c "
import sys; sys.path.insert(0, '$SK'); import _layout, os
F = '$ROOT/tests/fixtures/'
f = _layout.find_units(F + 'sample-course'); g = _layout.find_units(F + 'sample-grouped-course'); s = _layout.find_units(F + 'sample-spanish-course')
names = lambda us: ' '.join(os.path.basename(c) for u in us for c in _layout.chapters_of(u))
print(len(f), len(g), len(s), '|', names(g), '|', names(s))")"
if [[ "$UN" == "1 2 1 | chapter-01-the-water-cycle lecture-1-the-water-cycle | capitulo-01-el-ciclo-del-agua" ]]; then echo "ok   flat=1 unit, grouped=2 units; chapter folders found by content under any name (chapter-01-..., lecture-1-..., capitulo-01-...)"; else echo "FAIL unit/chapter discovery: $UN"; fail=1; fi

for FIX in sample-course sample-grouped-course sample-spanish-course; do
  step "gates pass on tests/fixtures/$FIX"
  SRC="$ROOT/tests/fixtures/$FIX"
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
