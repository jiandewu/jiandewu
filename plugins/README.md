# Claude Code plugins

Agent skills for research writing and multi-repository Git workflows, published
as a Claude Code plugin marketplace. Each plugin contains one skill.

| Plugin | Skill | What it does |
| --- | --- | --- |
| `md2docx` | `md2docx-paper-workflow` | Converts research Markdown to DOCX with Pandoc, BibTeX, six bundled CSL styles (APA, IEEE, Chicago, MLA, Vancouver, Nature), four Word reference templates, and optional `pandoc-crossref`. |
| `workspace-commit` | `commit-staged-workspace` | Inventories every Git repository in a multi-root workspace, proposes logical commit units, and after explicit approval stages exact paths and commits them in order. Never uses `git add -A`, never pushes. |
| `weekly-worklog` | `weekly-worklog` | Writes one Markdown work log per ISO week from Git status, the day's commits, and `STATUS.md` files, merging updates from several sessions on the same day. Writes in Chinese by default. |

## Install

In Claude Code:

```text
/plugin marketplace add jiandewu/jiandewu
/plugin install md2docx@jiandewu
/plugin install workspace-commit@jiandewu
/plugin install weekly-worklog@jiandewu
```

Skills are then available as `/md2docx:md2docx-paper-workflow`,
`/workspace-commit:commit-staged-workspace`, and `/weekly-worklog:weekly-worklog`,
and also trigger automatically from their descriptions.

## Requirements

- Python 3 (tested with 3.14) and Git for all scripts.
- `md2docx`: Pandoc 3.x. The converter looks for `$PANDOC`, then `pandoc` on
  `PATH`, then `conda run -n doc pandoc`. `pandoc-crossref` is optional.
- `weekly-worklog`: set `WEEKLY_WORKLOG_ROOT` to the directory that should hold
  the logs, for example `export WEEKLY_WORKLOG_ROOT="$HOME/worklog"`.

## Other agents

Each skill also ships an `agents/openai.yaml` for Codex. Copy or symlink a skill
directory into the agent's skills folder and replace `${CLAUDE_SKILL_DIR}` in
`SKILL.md` commands with that directory.

## License

Code and documentation: MIT, see [LICENSE](LICENSE), except the third-party
files below, which keep their own licenses.

The Word templates in `md2docx/skills/md2docx-paper-workflow/assets/docx-templates/`
are modified copies of Pandoc's default `reference.docx` (Copyright John
MacFarlane), licensed under the GNU GPL version 2 or later; see the
[COPYING.md](md2docx/skills/md2docx-paper-workflow/assets/docx-templates/COPYING.md)
file beside them.

The CSL files in `md2docx/skills/md2docx-paper-workflow/assets/citation-styles/`
come from the [Citation Style Language styles repository](https://github.com/citation-style-language/styles)
and are licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/);
each file keeps its original author and license metadata.
