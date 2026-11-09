---
name: commit-staged-workspace
description: Discover all Git repositories and changed files across the current IDE or multi-root workspace, propose one or more logical commits per repository, then after explicit approval automatically stage each approved unit and commit it in order. Use when the user asks to commit workspace changes, commit staged or unstaged files, split changes into logical commits, prepare commit messages, or commit all workspace repositories. Never silently fall back to the current repository, never use broad staging, preserve explicitly excluded work, and never push unless separately requested.
---

# Commit Workspace Changes

Inspect the complete workspace, plan logical commit units, and after approval stage and commit each unit deterministically.

## Safety Rules

- Resolve and inspect the complete workspace before planning.
- Treat each repository independently and allow multiple logical commits per repository.
- Include staged, unstaged, deleted, renamed, and untracked paths in the inventory.
- Never stage ignored files or anything outside the approved plan.
- Never use `git add -A`, `git add .`, `git commit -a`, `git commit --all`, `git commit --include`, `git commit --only`, `git reset --hard`, or `git stash`.
- Use `git add -- <exact-paths>` only after approval.
- Do not push unless the user separately asks.
- Stop on ambiguity, changed worktree state, failed validation, unsafe hunk boundaries, hook-induced changes, or partial failure.

## 1. Resolve the Workspace

Use the complete IDE or multi-root workspace folder list, an active VS Code `.code-workspace` file, the working directories the agent host exposes for this session (in Claude Code, the primary working directory plus every additional working directory), or workspace roots explicitly supplied by the user. Never assume the current shell repository is the whole workspace.

Pass every exposed folder to the read-only inventory script:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/inspect_staged.py \
  --workspace-root <workspace-folder-1> \
  --workspace-root <workspace-folder-2>
```

For a VS Code workspace file:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/inspect_staged.py \
  --workspace-file <workspace.code-workspace>
```

Explicit repository roots may be combined with workspace discovery:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/inspect_staged.py <repo-root> [<repo-root> ...]
```

Claude Code substitutes `${CLAUDE_SKILL_DIR}` with this skill's directory; in other agents, replace it with the directory that contains this `SKILL.md`.

The script refuses to run without explicit scope, discovers nested repositories only under those roots, and reports unavailable workspace paths. Reuse the exact invocation during pre-commit revalidation.

## 2. Inspect All Changes

For every discovered repository:

1. Review the branch, staged paths, unstaged paths, untracked paths, status entries, and full worktree signature.
2. Inspect tracked changes with `git -C <repo> diff HEAD --no-ext-diff`.
3. Inspect untracked file contents only as needed to classify them and check for secrets, credentials, generated artifacts, large binaries, or accidental files.
4. Identify rename pairs and file dependencies that must remain in the same commit.
5. Treat submodules, merge conflicts, partially staged files, and repositories without `HEAD` as special cases requiring an explicit safe plan.

The script hashes untracked file bytes locally to detect changes between planning and execution, but it does not print their contents. Do not mutate the index while inspecting or planning.

## 3. Form Logical Commit Units

Group changes by purpose, dependency, and reversibility rather than merely by file type. Prefer the smallest commits that remain coherent and independently valid.

For each unit, record:

- repository and branch;
- purpose and proposed conventional-style message;
- exact repository-relative paths;
- whether any path is partially staged or shared with another unit;
- validation to run after staging;
- paths intentionally excluded.

Assign each path to exactly one unit unless an explicit hunk-level split is safe. Keep a file in one unit when its changes are interdependent. If one file contains unrelated changes, split it only when the hunks can be selected deterministically without editing the worktree; otherwise explain the constraint and ask the user how to proceed.

## 4. Present the Approval Plan

Before staging or committing anything, present one workspace-wide plan containing:

- workspace inputs and complete discovered repository set;
- ordered commit units for each repository;
- exact paths and proposed message for every unit;
- staged, unstaged, and untracked changes accounted for;
- excluded paths;
- shortened worktree signature for each repository;
- validation and any warnings.

Ask for explicit approval of the repository order, unit order, paths, and messages. Do not treat the original request as approval of the generated plan.

## 5. Revalidate After Approval

Immediately before mutation:

1. Rerun the exact inventory command.
2. Compare the repository set, full worktree signatures, status entries, and changed path lists with the approved plan.
3. Stop and present a revised plan if anything changed.
4. Run relevant read-only validation that does not require staged content.

## 6. Stage and Commit Each Unit

Process one repository at a time in the approved order.

If the existing index exactly matches the first approved unit, retain it. Otherwise, disclose the index rebuild in the plan and, after approval, clear it once before the first unit:

```bash
git -C <repo> reset --mixed HEAD
```

Use this only after approval, only when `HEAD` exists, and only to clear the index while preserving working-tree content. If rebuilding would alter deliberately excluded staged state, stop unless that index change was explicitly approved. For a repository without `HEAD`, stop and use an explicitly approved initial-commit plan.

For each approved unit:

1. Stage only its exact paths:

   ```bash
   git -C <repo> add -- <path-1> <path-2>
   ```

2. Verify `git diff --cached --name-status`, inspect the full cached patch, and run `git diff --cached --check`.
3. Confirm no excluded or future-unit path is staged.
4. Run the unit's approved validation.
5. Commit without a pathspec:

   ```bash
   git -C <repo> commit -m "<approved-message>"
   ```

6. Verify the commit and inventory the remaining worktree before staging the next unit.

For an approved hunk-level split, use an interactive or patch-based staging method only when exact hunk boundaries are clear and verifiable. Never edit the working file merely to manufacture a split.

## 7. Verify and Report

After every commit:

1. Inspect `git -C <repo> show --stat --oneline --decorate HEAD`.
2. Confirm the committed paths and message match the approved unit.
3. Check `git -C <repo> status --short` and ensure remaining changes match later units or exclusions.
4. Stop if hooks modify files, stage unexpected content, or invalidate the remaining plan.

Finish with a per-repository table listing each commit hash, message, committed paths, and remaining changes. Report skipped clean repositories and excluded paths. Never push unless separately requested.
