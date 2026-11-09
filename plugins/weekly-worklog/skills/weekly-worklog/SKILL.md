---
name: weekly-worklog
description: Create or update a concise weekly work log across one or more workspace repositories. Use when the user says "update work log", "end workday", "下班总结", "更新工作日志", or asks to summarize today's work. Write one file per ISO week under the configured worklog root, merge idempotently across multiple agent sessions, and summarize project STATUS files, today's commits, staged/uncommitted work, decisions, and next actions. Write headings and prose in Chinese by default unless the user explicitly requests English or another language. Do not stage, commit, or push unless separately requested.
---

# Weekly Worklog

## Purpose

Maintain one concise Markdown work log per week under the resolved worklog root. Resolve it in this order:

1. `WEEKLY_WORKLOG_ROOT`, when set.
2. The `worklog/` directory in the nearest `Notebook` ancestor of this skill's real path (useful when the skill lives inside a notes repository).
3. `$HOME/Notebook/worklog`.

Set `WEEKLY_WORKLOG_ROOT` when installing from a plugin marketplace, because the installed copy has no `Notebook` ancestor.

Each weekly file is named by the Monday date of that ISO week, for example `<worklog-root>/2026/20260720.md`.

Use this skill for end-of-day or checkpoint summaries that may span multiple agent sessions and multiple repositories. Keep project-specific handoff details in the relevant project `STATUS.md`; the weekly work log should be a high-level record for the user.

## Language

- Write headings and prose in Chinese by default.
- Use English or another language only when the user explicitly requests it.
- Keep repository names, paths, commands, technical terms, identifiers, and original commit messages in their source language.
- When rewriting an existing day section, keep its editable headings and prose internally consistent with the selected language.

## Workflow

1. Determine the work-log date and target path.
   - Use an explicit user-provided date if present; otherwise use the current runtime date.
   - Determine the Monday date of that date's ISO week.
   - Target `<worklog-root>/YYYY/YYYYMMDD.md`, using that ISO-week Monday date.
2. Resolve workspace repositories.
   - Take the complete root set from exactly one authoritative source, in this order:
     1. Roots the user explicitly lists.
     2. The active VS Code or code-server multi-root workspace: a `.code-workspace` file the user names, or on code-server the configuration identified by the single active `User/workspaceStorage/*/vscode.lock` under the session's `--user-data-dir` (read the sibling `meta.json` → `configuration`). Resolve every `folders[].path` relative to the workspace file's directory.
     3. The working directories the agent host lists for the current session (in Claude Code, the primary working directory plus every additional working directory).
   - Never use the shell cwd alone, terminal history, or a root list cached from an earlier session as the root set.
   - If no source yields a complete, readable list (for example, zero or several active `vscode.lock` files, or an invalid `folders` entry), stop before evidence gathering, ask the user for explicit roots, and do not write a partial work log.
   - For every candidate, determine whether that candidate root itself is a Git worktree and record the checked repositories and any non-repository roots. Do not recursively search candidates, their subdirectories, or their parent directories for nested Git repositories.
3. Gather concise evidence from every resolved workspace repository.
   - For each repository, inspect `git status --short`.
   - For each repository, inspect commits created on the work-log date with `git log --since=<date> --oneline --decorate` when useful.
   - Read root or subproject `STATUS.md` files that are relevant to the active work in that repository.
   - If a repository cannot be inspected, record it as unchecked; do not treat it as clean or omit it from the evidence scope.
   - Treat modifications to the target weekly log as expected output, not as handoff evidence.
   - Do not inspect sensitive file contents unless needed for the requested summary.
4. Read the existing weekly log if it exists.
   - Update only the current day section headed `## YYYY-MM-DD`.
   - Merge idempotently across multiple sessions and terminals on the same day; never replace the whole day section with one session's snapshot.
   - In the `### 项目` section, group all entries by project in first-seen order; if old entries are interleaved, consolidate them before adding new content.
   - For the same project, preserve the existing project bullet and append only new details; for a different project, preserve all existing project bullets and append the new project after them.
   - De-duplicate commit hashes, repeated project bullets, and repeated open items.
   - Remove any prior open item that only reports the target weekly log as modified or uncommitted.
5. Write a concise day section.
   - Write headings and prose in Chinese by default.
   - Use English or another language only when the user explicitly requests it.
   - Preserve code-like literals and original commit messages in their source language.
   - Keep bullets high-level and useful for recall.
   - Prefer project paths and commit hashes over long narrative.
   - Do not add meta-open-items such as “this work log is modified” or “this work-log update is not committed.”
   - Do not copy unpublished manuscript text, private email text, secrets, credentials, or long command logs.
6. Optionally check whether a project index is stale.
   - Use the file named by `WEEKLY_WORKLOG_PROJECTS_FILE`, else `profile/projects.md` in the worklog root's parent directory. Skip this step silently if neither exists.
   - Compare it with the projects in this week's log and the previous three weekly logs.
   - In the final reply to the user (not in the work log), list any project that appears in the logs but not in the index, and any indexed project with no log activity in those four weeks. Say nothing if there are no differences.
   - Do not edit the index unless the user asks.
7. Do not stage, commit, or push unless the user separately asks.

## Day Section Format

Use this structure for each day:

```markdown
## YYYY-MM-DD

### 总结

- ……

### 项目

- `repo-or-subproject`：……

### 提交

- `hash` `repo`：原始提交信息。

### 待办

- ……
```

This is the default Chinese structure. If the user explicitly requests another language, translate the editable headings and prose consistently. Omit empty sections if they add no value, but keep the summary and projects sections whenever possible.

## Helper Script

Use `scripts/update_worklog.py` to compute the weekly path and upsert the day section.

Print the target path:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/update_worklog.py --date YYYY-MM-DD --print-path
```

Create or replace the day's section from a temporary Markdown body file:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/update_worklog.py --date YYYY-MM-DD --content-file /tmp/day-worklog.md
```

Claude Code substitutes `${CLAUDE_SKILL_DIR}` with this skill's directory; in other agents, replace it with the directory that contains this `SKILL.md`. Use `--root <path>` to override the resolved root for one run. The helper preserves existing same-day content and merges the incoming update by section.

The content file may contain either the section body or a full `## YYYY-MM-DD` section. The script creates parent directories, creates the weekly file if missing, and replaces only the matching day section.

## Quality Bar

- The final log should help the user remember what happened today without becoming a transcript.
- If the same day already has a section, preserve useful prior bullets and integrate new ones rather than appending duplicates.
- If evidence is incomplete, say so briefly in the log instead of guessing.
- If there are uncommitted or untracked items, record them as open items only when they matter for handoff.
- Never claim workspace-wide coverage unless every candidate came from one complete root source in step 2.
- Never treat cwd, terminal history, or a cached workspace-root list as a substitute for that source.
- Never claim workspace-wide coverage after checking only cwd, one root, or a recursively discovered subset.
