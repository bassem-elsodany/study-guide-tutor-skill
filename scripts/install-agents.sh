#!/usr/bin/env bash
# install-agents - install study-guide-tutor for agents other than Claude Code (Codex, Cursor, Gemini CLI, GitHub Copilot,
# OpenCode, Windsurf/Devin, Kiro, ...) WITHOUT their plugin systems.
#
#   scripts/install-agents.sh [--scope project|user] [--dest DIR] [--mode link|copy] [--kiro]
#                             [--agents-md [FILE]] [--dry-run] [--uninstall]
#
# These tools discover skills as folders containing SKILL.md in a shared location (`.agents/skills/` in a project,
# `~/.agents/skills/` per user; Kiro uses `.kiro/skills/`). The skill folder is self-contained (its scripts and
# references live inside it), so
#   link mode (default)  symlinks the skill folder to this clone (keep the clone in place)
#   copy mode            copies the skill folder, and the agent prompts and templates into <dest>/../study-guide-tutor-bundle
# and (optionally) writes a managed block into AGENTS.md that tells the agent where the skill and agent prompts are.
#
# Safe by design: never overwrites a path it did not create; --uninstall removes only what it created; --dry-run prints.
# Slash commands and agents are Claude Code features and are NOT installed here (the prompts are plain files you can paste).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCOPE=project; DEST=""; MODE=link; KIRO=0; AGENTS_MD=""; WANT_MD=0; DRY=0; UNINSTALL=0
while [[ $# -gt 0 ]]; do case "$1" in
  --scope) SCOPE="$2"; shift 2;; --dest) DEST="$2"; shift 2;; --mode) MODE="$2"; shift 2;; --kiro) KIRO=1; shift;;
  --agents-md) WANT_MD=1; if [[ $# -gt 1 && "$2" != --* ]]; then AGENTS_MD="$2"; shift 2; else shift; fi;;
  --dry-run) DRY=1; shift;; --uninstall) UNINSTALL=1; shift;;
  -h|--help) sed -n 2,22p "$0"; exit 0;; *) echo "unknown argument $1" >&2; exit 2;; esac; done
[[ "$SCOPE" == project || "$SCOPE" == user ]] || { echo "--scope must be project or user" >&2; exit 2; }
[[ "$MODE" == link || "$MODE" == copy ]] || { echo "--mode must be link or copy" >&2; exit 2; }
if [[ -z "$DEST" ]]; then [[ "$SCOPE" == user ]] && DEST="$HOME/.agents/skills" || DEST="$PWD/.agents/skills"; fi
if (( WANT_MD )) && [[ -z "$AGENTS_MD" ]]; then
  [[ "$SCOPE" == project ]] && AGENTS_MD="$PWD/AGENTS.md" || { echo "--agents-md needs a FILE with --scope user" >&2; exit 2; }
fi
BUNDLE_COPY="$(dirname "$DEST")/study-guide-tutor-bundle"
MARK=".study-guide-tutor-installed"
START="<!-- study-guide-tutor:start (managed by scripts/install-agents.sh; remove with --uninstall) -->"; END="<!-- study-guide-tutor:end -->"
run() { if (( DRY )); then echo "  [dry-run] $*"; else "$@"; fi; }
say() { echo "$@"; }

targets=("$DEST"); (( KIRO )) && { [[ "$SCOPE" == user ]] && targets+=("$HOME/.kiro/skills") || targets+=("$PWD/.kiro/skills"); }
skills=(); for d in "$ROOT"/skills/*/; do [[ -f "$d/SKILL.md" ]] && skills+=("$(basename "$d")"); done
[[ ${#skills[@]} -gt 0 ]] || { echo "no skills found under $ROOT/skills" >&2; exit 1; }

strip_block() { # strip_block FILE  - remove the managed block, keep the rest
  local f="$1"; [[ -f "$f" ]] || return 0
  awk -v s="$START" -v e="$END" 'index($0,"<!-- study-guide-tutor:start")==1{skip=1} !skip{print} index($0,e)==1{skip=0}' "$f" > "$f.sgt-tmp" && mv "$f.sgt-tmp" "$f"
}

if (( UNINSTALL )); then
  for t in "${targets[@]}"; do
    [[ -d "$t" ]] || continue
    for s in "${skills[@]}"; do
      p="$t/$s"
      if [[ -L "$p" && "$(readlink "$p")" == "$ROOT/skills/$s" ]]; then say "remove link  $p"; run rm "$p"
      elif [[ -d "$p" && -f "$p/$MARK" ]]; then say "remove copy  $p"; run rm -rf "$p"; fi
    done
  done
  if [[ -d "$BUNDLE_COPY" && -f "$BUNDLE_COPY/$MARK" ]]; then say "remove bundle copy $BUNDLE_COPY"; run rm -rf "$BUNDLE_COPY"; fi
  if [[ -n "$AGENTS_MD" && -f "$AGENTS_MD" ]] && grep -q "study-guide-tutor:start" "$AGENTS_MD"; then say "strip managed block from $AGENTS_MD"; (( DRY )) || strip_block "$AGENTS_MD"; fi
  say "uninstall complete (only items created by this script were touched)"; exit 0
fi

BR="$ROOT"
if [[ "$MODE" == copy ]]; then
  BR="$BUNDLE_COPY"
  say "bundle copy -> $BR (agents, templates)"
  if [[ -e "$BR" && ! -f "$BR/$MARK" ]]; then echo "refusing: $BR exists and was not created by this script" >&2; exit 1; fi
  run mkdir -p "$BR"
  for d in agents templates; do [[ -d "$ROOT/$d" ]] && { (( DRY )) && echo "  [dry-run] copy $d" || { rm -rf "$BR/$d"; cp -R "$ROOT/$d" "$BR/$d"; }; }; done
  (( DRY )) || echo "study-guide-tutor bundle support files copied from $ROOT" > "$BR/$MARK"
fi

skipped=0
for t in "${targets[@]}"; do
  installed=0
  say "install into $t ($MODE)"; run mkdir -p "$t"
  for s in "${skills[@]}"; do
    p="$t/$s"
    if [[ -L "$p" && "$(readlink "$p")" == "$ROOT/skills/$s" ]]; then installed=$((installed+1)); continue; fi      # already ours
    if [[ -d "$p" && -f "$p/$MARK" ]]; then (( DRY )) || rm -rf "$p"; fi                                          # our old copy: refresh
    if [[ -e "$p" || -L "$p" ]]; then echo "  skip $s: $p exists and is not ours" >&2; skipped=$((skipped+1)); continue; fi
    if [[ "$MODE" == link ]]; then run ln -s "$ROOT/skills/$s" "$p"
    else (( DRY )) && echo "  [dry-run] copy $s" || { cp -R "$ROOT/skills/$s" "$p"; echo "copied from $ROOT/skills/$s" > "$p/$MARK"; }; fi
    installed=$((installed+1))
  done
  say "  skills installed here: $installed"
done
[[ $skipped -gt 0 ]] && say "skipped (not ours, left untouched): $skipped"

if (( WANT_MD )); then
  say "write managed block into $AGENTS_MD"
  if (( ! DRY )); then
    touch "$AGENTS_MD"; strip_block "$AGENTS_MD"
    { [[ -s "$AGENTS_MD" ]] && echo ""
      cat <<EOF
$START
## study-guide-tutor (study material to tutoring course)

Skill installed in \`$DEST/study-guide-tutor\`. When the user shares study material or asks to study, learn, be quizzed or prepare for an exam, first read \`$DEST/study-guide-tutor/SKILL.md\` and follow it.

- **Skill folder:** read \`\${CLAUDE_SKILL_DIR}\` in the skill text as \`$DEST/study-guide-tutor\`; read \`\${CLAUDE_PLUGIN_ROOT}\` as \`$BR\`. Scripts are in \`\${CLAUDE_SKILL_DIR}/scripts/\` (Python standard library only).
- **Agent prompts** (teacher-writer, student-reviewer) are plain files in \`$BR/agents/\`: paste one into a sub-agent or follow it yourself. Slash commands are Claude Code only.
- **Always:** intake before generating, read all material before teaching, material-only facts, lessons that teach rather than dump, 2-4 tricky-part hints per lesson, audited quizzes, and run the gates (\`add_toc.py --check\`, \`audit_quiz.py\`, \`check_bundle.py\`, \`check_dump.py\`, \`check_tricky.py\`, \`check_findable.py\`) before delivering.
$END
EOF
    } >> "$AGENTS_MD"
  fi
fi
say "done. Restart the agent (or reload skills) so it rediscovers $DEST."
[[ "$MODE" == link ]] && say "link mode: keep this clone in place ($ROOT); the links point into it."
exit 0
