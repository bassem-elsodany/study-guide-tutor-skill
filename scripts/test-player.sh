#!/usr/bin/env bash
# test-player - build the interactive study player from the sample course with the scripted self-test appended,
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
python3 "$ROOT/skills/study-guide-tutor/scripts/make_player.py" "$ROOT/tests/fixtures/sample-course/domain-1" --out "$T/p.html" --selftest >/dev/null
OUT="$("$CH" --headless=new --disable-gpu --no-sandbox --virtual-time-budget=5000 --dump-dom "file://$T/p.html" 2>/dev/null || true)"
RES="$(printf '%s' "$OUT" | python3 -c "
import sys,re,html
d=sys.stdin.read(); m=re.search(r'<pre id=\"selftest\">(.*?)</pre>',d,re.S)
print(html.unescape(m.group(1)) if m else 'NO SELFTEST OUTPUT')")"
echo "$RES"
printf '%s' "$RES" | head -1 | grep -q "SELFTEST OK"
