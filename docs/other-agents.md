# Using study-guide-tutor-skill with other coding agents

> What carries over: the **skill** (decision guide, references, scripts). What does not: Claude Code's **slash commands** and **agent definitions** (the two agent prompts are plain Markdown you can paste into any sub-agent). There are no hooks to lose.

## The short version

```bash
git clone https://github.com/bassem-elsodany/study-guide-tutor-skill.git ~/src/study-guide-tutor-skill
cd /path/to/your/study/folder
~/src/study-guide-tutor-skill/scripts/install-agents.sh --agents-md          # project scope: ./.agents/skills + a managed block in ./AGENTS.md
# or for every project of your user:
~/src/study-guide-tutor-skill/scripts/install-agents.sh --scope user --agents-md ~/AGENTS.md
```

Restart (or reload skills in) the agent. Remove everything the script created with the same command plus `--uninstall`.

| Option | Meaning |
|---|---|
| `--scope project` (default) / `user` | `./.agents/skills` or `~/.agents/skills` |
| `--mode link` (default) / `copy` | symlink the skill into the clone (keep the clone in place) / copy the skill folder, and the agent prompts and templates into `<dest>/../study-guide-tutor-skill-bundle` |
| `--kiro` | also install into `.kiro/skills` (Kiro's location) |
| `--agents-md [FILE]` | write (or refresh) a managed block telling the agent where the skill and the agent prompts are |
| `--dry-run` / `--uninstall` | preview / remove only what this script created |

The script never overwrites a path it did not create. It was tested by the maintainer on macOS in throw-away directories (link and copy modes, project and user scope, uninstall); the CI workflow repeats the link, uninstall and copy runs on Linux.

## Why a script and not just a copy?

The skill folder is self-contained: `SKILL.md`, `references/` and `scripts/` live inside `skills/study-guide-tutor-skill/`. A plain copy of that folder works. The script adds the safe link/copy/uninstall handling, the managed `AGENTS.md` block, and copies the two agent prompts and the templates, which sit outside the skill folder.

## Per tool: where skills are discovered

Skill folders containing a `SKILL.md` are discovered by Codex, Cursor, Gemini CLI, GitHub Copilot, OpenCode and Windsurf/Devin in `.agents/skills/` (project) or `~/.agents/skills/` (user); Kiro uses `.kiro/skills/`. These locations come from each vendor's public documentation and change over time; check the current docs of your tool. **Nothing here was run inside those agents**: only the installer itself was tested.

### Portability rules this repository enforces

`scripts/validate-plugin.py` (CI) checks what these tools need: `name` equals the folder name (lowercase, digits, hyphens, at most 64 characters), `description` is present and at most 1,024 characters, frontmatter starts on the first line, and `SKILL.md` stays under 500 lines.

## What to do manually without slash commands

| Claude Code command | Do this instead |
|---|---|
| `/study` | say "study this material" and point at the file; the skill runs the intake first |
| `/study-quiz` | ask "quiz me on chapter N", then answer as `1B 2D 3A` |
| `/study-cram` | say "I only have an hour" |
| `/study-weak` | say "quiz me on what I missed" |
| `/study-check` | run the scripts listed in `AGENTS.md` section 3 on your course folder |

The agent prompts are `agents/teacher-writer.md` and `agents/student-reviewer.md`: paste one into a sub-agent and fill the placeholders at the top.
