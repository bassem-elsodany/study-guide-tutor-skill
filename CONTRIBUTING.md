# Contributing to study-guide-tutor-skill

Thanks for helping. The skill is refined by real use: if a lesson came out as a slide dump, a quiz leaked its answer, a gate misreported, or the intake asked the wrong question, fixing that is the most valuable contribution.

## Ground rules

- **English only**, one idea per file, tables over prose, every claim checkable.
- **Generic by construction.** The skill must work for any subject and any learner. No course names, no personal details, no absolute paths, no machine or account names (`scripts/validate-plugin.py` fails on them). Examples in docs use neutral topics.
- **Original text only.** Do not copy third-party text unless its licence allows it; list reused material in `NOTICE.md`. Never commit someone's lecture slides or a generated course built from them.
- **Scripts**: Python standard library only, macOS and Linux, read-only or dry-run where they can destroy data, never write outside the folder they are given, `--help` that works, a docstring that starts with a one-line summary.
- **No AI attribution trailers** in commits unless the maintainer asks; use conventional commits (`feat(quiz): ...`).

## Authoring standards

- **Frontmatter first.** `SKILL.md` starts with `---`; `name` equals the directory (kebab-case, at most 64 characters), `description` is third person, says what the skill does first and then "Use when ...", has no angle brackets and is at most 1,024 characters. Only recognised keys.
- **Under 500 lines per `SKILL.md`; progressive disclosure.** The decision guide first; depth in `references/`. A reference file should stand on its own.
- **Teach the why.** Rules come with the reason and the failure they prevent. Gates come with the script that enforces them.
- **Paths.** In `SKILL.md` and commands use `${CLAUDE_SKILL_DIR}/...` or `${CLAUDE_PLUGIN_ROOT}/...`; never an absolute path.
- **Agents** (`agents/*.md`): frontmatter with `name`, a dispatch-oriented `description`, `tools:` as a YAML list and a `model`. Every `.md` in `agents/` is loaded as an agent: keep helper documents elsewhere.
- **Commands** (`commands/*.md`): frontmatter with `description` and `allowed-tools` scoped to what the command runs.
- **Manifests**: `version` in `plugin.json` and `marketplace.json` must equal `VERSION`; bump it for every user-visible release. No `CLAUDE.md` at the repository root (operating instructions live in `AGENTS.md`).

## Before you open a pull request

```bash
scripts/quality-check.sh && python3 -I scripts/validate-plugin.py --self-test && python3 -I scripts/validate-plugin.py .
```

`quality-check.sh` compiles every script, runs each with `--help`, and runs the gates against the example and fixture courses (`examples/` and `tests/fixtures/`). If you have the Claude Code CLI: `claude plugin validate . --strict`.

Diagrams in `docs/how-it-works.md` are Mermaid: edit `docs/diagrams/*.mmd`, paste into that page, and keep them in sync.

## Proposing a change to the method

Open an issue first with: the situation where the skill produced weak study material, a real example (anonymised), what the skill should do instead, and which existing reference file is closest. A rule that cannot be checked by a gate or a reviewer prompt should say how it will be judged.

## Reporting problems

Include: the prompt or command, the script or reference file involved, what you expected, what happened, your OS and `python3 --version`. Security problems: see [SECURITY.md](SECURITY.md).

By contributing you agree your contribution is licensed under the repository's MIT licence.
