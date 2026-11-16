#!/usr/bin/env bash
# quality-check - compile every script, run each with --help, and run the gates on the sample course.
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

step "gates pass on the sample course"
SRC="$ROOT/tests/fixtures/sample-course"
if [[ -d "$SRC" ]]; then
  T="$(mktemp -d)"; cp -R "$SRC" "$T/course"; C="$T/course"
  for g in "add_toc.py $C --check" "audit_quiz.py $C" "check_bundle.py $C" "check_dump.py $C" "check_tricky.py $C" "check_findable.py $C"; do
    # shellcheck disable=SC2086
    if python3 -I "$SK/${g%% *}" ${g#* } >/tmp/sgt-gate.out 2>&1; then echo "ok   ${g%% *}"; else echo "FAIL ${g%% *}"; cat /tmp/sgt-gate.out; fail=1; fi
  done
  rm -rf "$T" /tmp/sgt-gate.out
else
  echo "no sample course found (tests/fixtures/sample-course)"; fail=1
fi

step "interactive player self-test (skips without Chrome or Chromium)"
if ! "$ROOT/scripts/test-player.sh" >/tmp/sgt-player.out 2>&1; then cat /tmp/sgt-player.out; fail=1; else head -1 /tmp/sgt-player.out; fi
rm -f /tmp/sgt-player.out

[[ $fail -eq 0 ]] && echo "RESULT: OK" || { echo "RESULT: FAILED"; exit 1; }
