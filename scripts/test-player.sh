#!/usr/bin/env bash
# test-player - build the interactive study player from the sample courses (the flat course, one module of the grouped
# course, the Spanish course, and the Spanish course set to Arabic to check right-to-left) with the scripted self-test appended,
# open it in a headless Chrome/Chromium, and fail unless every scripted click-through check passes.
# Skips (exit 0) when no Chrome/Chromium is installed. Writes only to a temporary directory.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CH=""
for c in "google-chrome" "google-chrome-stable" "chromium" "chromium-browser" \
         "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" "/Applications/Chromium.app/Contents/MacOS/Chromium"; do
  if command -v "$c" >/dev/null 2>&1 || [[ -x "$c" ]]; then CH="$c"; break; fi
done
if [[ -z "$CH" ]]; then echo "SKIP: no Chrome or Chromium found (the player self-test needs one)"; exit 0; fi
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
run_one() {  # run_one NAME UNIT_DIR [EXPECTED_HTML_TAG_TEXT]
  python3 "$ROOT/skills/study-guide-tutor/scripts/make_player.py" "$2" --out "$T/$1.html" --selftest >/dev/null
  OUT="$("$CH" --headless=new --disable-gpu --no-sandbox --virtual-time-budget=6000 --dump-dom "file://$T/$1.html" 2>/dev/null || true)"
  RES="$(printf '%s' "$OUT" | python3 -c "
import sys,re,html
d=sys.stdin.read(); m=re.search(r'<pre id=\"selftest\">(.*?)</pre>',d,re.S)
print(html.unescape(m.group(1)) if m else 'NO SELFTEST OUTPUT')")"
  echo "== $1"; echo "$RES"
  [[ "${RES%%$'\n'*}" == "SELFTEST OK" ]] || { echo "FAIL: first line was not SELFTEST OK"; return 1; }
  if [[ -n "${3:-}" ]]; then [[ "$OUT" == *"$3"* ]] || { echo "FAIL expected $3 in the page"; return 1; }; echo "ok   page has $3"; fi
}
run_one flat "$ROOT/tests/fixtures/sample-course"
run_one grouped-module "$ROOT/tests/fixtures/sample-grouped-course/module-2"
run_one spanish "$ROOT/tests/fixtures/sample-spanish-course" 'lang="es" dir="ltr"'
# the same course declared as Arabic must flip the page to right-to-left
cp -R "$ROOT/tests/fixtures/sample-spanish-course" "$T/arabic-course"
python3 - "$T/arabic-course/course.json" <<'PY'
import json, sys
p = sys.argv[1]; j = json.load(open(p, encoding='utf-8')); j['language'] = 'ar'
json.dump(j, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
PY
run_one arabic-direction "$T/arabic-course" 'lang="ar" dir="rtl"'
