# Installing study-guide-tutor-skill

The short version is in the [README](../README.md). This page has every option, the requirements and the fixes for common problems.

## Requirements

| Needed | Check | Used for |
|---|---|---|
| Claude Code (recent; plugin support) | `claude --version` | the plugin: skill, agents, commands |
| `python3` 3.9 or newer (developed on 3.13; CI runs 3.11) | `python3 --version` | every script (standard library only) |
| `git` | `git --version` | installing from a repository |
| *Optional:* `pdftotext` (poppler) | `pdftotext -v` | extracting text from PDFs (`brew install poppler` / `apt install poppler-utils`); without it the scripts fall back to `pypdf`, `PyPDF2` or PyMuPDF if installed |
| *Optional:* `mmdc` (Mermaid CLI) | `mmdc --version` | validating the diagrams in lessons and drawing them in the practice page's Lesson tab (`npm i -g @mermaid-js/mermaid-cli`); without it diagrams are written but not validated |

Tested on macOS (Apple silicon) with Claude Code. Linux is expected to work. Windows is untested: use WSL. Image-only slides cannot be read by `pdftotext`: the skill transcribes them once and caches the result.

## Claude Code

<details open>
<summary><b>From a hosted repository (recommended)</b></summary>

Inside a Claude Code session:

```
/plugin marketplace add bassem-elsodany/study-guide-tutor-skill
/plugin install study-guide-tutor-skill@study-guide-tutor-skill
/reload-plugins
```

or from your shell:

```bash
claude plugin marketplace add bassem-elsodany/study-guide-tutor-skill
claude plugin install study-guide-tutor-skill@study-guide-tutor-skill            # --scope user (default) | project | local
```

`bassem-elsodany/study-guide-tutor-skill` can also be a full git URL (`https://github.com/bassem-elsodany/study-guide-tutor-skill.git`, GitLab, a self-hosted host) or an SSH address.

**`Permission denied (publickey)`?** The marketplace is cloned with git. Either add an SSH key to your host, or use the HTTPS URL:

```
/plugin marketplace add https://github.com/bassem-elsodany/study-guide-tutor-skill.git
```

</details>

<details>
<summary><b>From a local clone (also the way to try changes)</b></summary>

```bash
git clone https://github.com/bassem-elsodany/study-guide-tutor-skill.git ~/src/study-guide-tutor-skill

# A) install it (persistent)
claude plugin marketplace add ~/src/study-guide-tutor-skill
claude plugin install study-guide-tutor-skill@study-guide-tutor-skill

# B) or load it for ONE session only, nothing installed
claude --plugin-dir ~/src/study-guide-tutor-skill
```

After editing the clone, `/reload-plugins` picks up skill and command changes in a running session.

</details>

<details>
<summary><b>Just the skill, without the plugin system</b></summary>

Copy (or symlink) the folder `skills/study-guide-tutor-skill/` to `~/.claude/skills/study-guide-tutor-skill/` (all projects) or `<project>/.claude/skills/study-guide-tutor-skill/` (one project). You get the skill and its scripts; the agents and slash commands come with the plugin.

</details>

<details>
<summary><b>For a whole team (project scope)</b></summary>

```bash
claude plugin marketplace add bassem-elsodany/study-guide-tutor-skill --scope project
claude plugin install study-guide-tutor-skill@study-guide-tutor-skill --scope project
git add .claude/settings.json && git commit -m "chore: enable study-guide-tutor-skill for the team"
```

Settings are shared through git, but each teammate still adds the marketplace and runs the install command once in their own clone.

</details>

## Other agents (the skill only: no agents or slash commands)

Codex, Cursor, Gemini CLI, GitHub Copilot, OpenCode, Windsurf/Devin and Kiro discover skills as folders containing `SKILL.md`, most of them in a shared `.agents/skills/` location (Kiro: `.kiro/skills/`).

```bash
git clone https://github.com/bassem-elsodany/study-guide-tutor-skill.git ~/src/study-guide-tutor-skill
cd /path/to/your/study/folder
~/src/study-guide-tutor-skill/scripts/install-agents.sh --agents-md        # ./.agents/skills + a managed block in ./AGENTS.md
#   --scope user --agents-md ~/AGENTS.md   all your projects   ·   --kiro   also .kiro/skills
#   --mode copy   self-contained copy       ·   --dry-run  preview   ·   --uninstall  remove only what it created
```

Restart the agent so it rediscovers the skill. **What was tested:** the installer itself (link and copy modes, project and user scope, uninstall) on macOS in throw-away directories. **What was not:** the agents themselves. Details: [docs/other-agents.md](other-agents.md).

## Troubleshooting

| Symptom | Fix |
|---|---|
| `/study` says unknown command | commands are namespaced: `/study-guide-tutor-skill:study`; type `/study` and pick from the menu; run `/reload-plugins` after installing |
| The skill never triggers | `/plugin` → *Errors* tab; make sure the plugin is enabled in this project's scope; say it explicitly: "use the study-guide-tutor-skill skill to teach me this PDF" |
| Text from a PDF is empty or garbled | install `pdftotext` (poppler); for scanned or image-only slides the skill transcribes each slide once (the cache is `<name>.slides.txt` beside the original) |
| A script path shows a literal `${CLAUDE_SKILL_DIR}` | you installed the skill outside Claude Code: read it as the folder that contains `SKILL.md` |
| `check_findable.py` flags an answer that is in the lesson | it compares words, so a paraphrase can false-alarm; read the answer and the lesson, then reword one of them |
| Lessons run over the reading budget | `reading_load.py` shows which; trim a section, or relax the budget in your profile and say so ("fine to read 15 minutes") |
| `python3: command not found` | install Python 3 (Xcode CLT on macOS, `apt install python3`) |
| Still stuck | `claude --debug` shows plugin loading; then open an issue ([CONTRIBUTING.md](../CONTRIBUTING.md)) |

---
