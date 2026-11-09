#!/usr/bin/env python3
"""Read-only change inventory for every Git repository in a workspace."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path


PRUNED_DIRECTORY_NAMES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "node_modules",
}
WINDOWS_ABSOLUTE_PATH = re.compile(r"^[A-Za-z]:[\\/]")


def git(path: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(
        ["git", "-c", "core.quotepath=false", "-C", str(path), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(message or f"git {' '.join(args)} failed")
    return result


def text(result: subprocess.CompletedProcess[bytes]) -> str:
    return result.stdout.decode("utf-8", errors="replace").strip()


def nul_paths(result: subprocess.CompletedProcess[bytes]) -> list[str]:
    raw = result.stdout.decode("utf-8", errors="surrogateescape")
    return [item for item in raw.split("\0") if item]


def resolve_repo(candidate: str) -> Path:
    path = Path(candidate).expanduser().resolve()
    top = text(git(path, "rev-parse", "--show-toplevel"))
    return Path(top).resolve()


def strip_jsonc_comments(source: str) -> str:
    output: list[str] = []
    index = 0
    in_string = False
    escaped = False

    while index < len(source):
        char = source[index]
        following = source[index + 1] if index + 1 < len(source) else ""

        if in_string:
            output.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue

        if char == '"':
            in_string = True
            output.append(char)
            index += 1
            continue

        if char == "/" and following == "/":
            index += 2
            while index < len(source) and source[index] not in "\r\n":
                index += 1
            continue

        if char == "/" and following == "*":
            index += 2
            while index < len(source):
                if index + 1 < len(source) and source[index : index + 2] == "*/":
                    index += 2
                    break
                if source[index] in "\r\n":
                    output.append(source[index])
                index += 1
            continue

        output.append(char)
        index += 1

    return "".join(output)


def strip_jsonc_trailing_commas(source: str) -> str:
    output: list[str] = []
    index = 0
    in_string = False
    escaped = False

    while index < len(source):
        char = source[index]
        if in_string:
            output.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue

        if char == '"':
            in_string = True
            output.append(char)
            index += 1
            continue

        if char == ",":
            lookahead = index + 1
            while lookahead < len(source) and source[lookahead].isspace():
                lookahead += 1
            if lookahead < len(source) and source[lookahead] in "]}":
                index += 1
                continue

        output.append(char)
        index += 1

    return "".join(output)


def workspace_file_roots(
    workspace_file: str,
) -> tuple[list[Path], list[dict[str, str]]]:
    workspace_path = Path(workspace_file).expanduser().resolve()
    if not workspace_path.is_file():
        raise RuntimeError(f"workspace file not found: {workspace_path}")

    try:
        source = workspace_path.read_text(encoding="utf-8")
        payload = json.loads(
            strip_jsonc_trailing_commas(strip_jsonc_comments(source))
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"cannot parse workspace file {workspace_path}: {exc}") from exc

    folders = payload.get("folders")
    if not isinstance(folders, list):
        raise RuntimeError(f"workspace file has no folders list: {workspace_path}")

    roots: list[Path] = []
    skipped: list[dict[str, str]] = []
    for entry in folders:
        if isinstance(entry, str):
            raw_path = entry
        elif isinstance(entry, dict) and isinstance(entry.get("path"), str):
            raw_path = entry["path"]
        else:
            skipped.append(
                {
                    "path": str(entry),
                    "reason": f"unsupported folder entry in {workspace_path}",
                }
            )
            continue

        if "${" in raw_path:
            skipped.append(
                {
                    "path": raw_path,
                    "reason": f"unresolved workspace variable in {workspace_path}",
                }
            )
            continue
        if os.name != "nt" and WINDOWS_ABSOLUTE_PATH.match(raw_path):
            skipped.append(
                {
                    "path": raw_path,
                    "reason": f"non-native Windows path in {workspace_path}",
                }
            )
            continue

        folder = Path(raw_path).expanduser()
        if not folder.is_absolute():
            folder = workspace_path.parent / folder
        roots.append(folder.resolve())

    return roots, skipped


def discover_repositories(workspace_root: Path) -> list[Path]:
    root = workspace_root.expanduser().resolve()
    if not root.exists():
        return []

    repositories: list[Path] = []
    seen: set[Path] = set()

    def add(candidate: Path) -> None:
        try:
            repo = resolve_repo(str(candidate))
        except (OSError, RuntimeError):
            return
        if repo not in seen:
            repositories.append(repo)
            seen.add(repo)

    add(root)
    if not root.is_dir():
        return repositories

    for current, directories, files in os.walk(root, followlinks=False):
        directories.sort()
        directories[:] = [
            name
            for name in directories
            if name not in PRUNED_DIRECTORY_NAMES
            and not (Path(current) / name).is_symlink()
        ]
        if ".git" in files or (Path(current) / ".git").is_dir():
            add(Path(current))

    return repositories


def parse_status_entries(raw: bytes) -> list[dict[str, str]]:
    tokens = [item for item in raw.split(b"\0") if item]
    entries: list[dict[str, str]] = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        code = token[:2].decode("ascii", errors="replace")
        path = token[3:].decode("utf-8", errors="surrogateescape")
        entry = {"status": code, "path": path}
        if "R" in code or "C" in code:
            index += 1
            if index < len(tokens):
                entry["original_path"] = tokens[index].decode(
                    "utf-8", errors="surrogateescape"
                )
        entries.append(entry)
        index += 1
    return entries


def worktree_signature(
    tracked_patch: bytes, status_raw: bytes, repo: Path, untracked_files: list[str]
) -> str:
    digest = hashlib.sha256()
    digest.update(tracked_patch)
    digest.update(b"\0STATUS\0")
    digest.update(status_raw)
    digest.update(b"\0UNTRACKED\0")
    for path in sorted(untracked_files):
        candidate = repo / path
        digest.update(path.encode("utf-8", errors="surrogateescape"))
        digest.update(b"\0")
        if candidate.is_symlink():
            digest.update(
                os.readlink(candidate).encode("utf-8", errors="surrogateescape")
            )
        elif candidate.is_file():
            with candidate.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
        digest.update(b"\0")
    return digest.hexdigest()


def inspect(repo: Path) -> dict[str, object]:
    has_head = git(repo, "rev-parse", "--verify", "HEAD", check=False).returncode == 0
    branch = text(git(repo, "symbolic-ref", "--short", "-q", "HEAD", check=False))
    if not branch:
        branch = text(git(repo, "rev-parse", "--short", "HEAD")) if has_head else "(unborn)"

    staged_patch = git(repo, "diff", "--cached", "--binary", "--no-ext-diff").stdout
    unstaged_patch = git(repo, "diff", "--binary", "--no-ext-diff").stdout
    tracked_patch = (
        git(repo, "diff", "HEAD", "--binary", "--no-ext-diff").stdout
        if has_head
        else staged_patch + b"\0UNSTAGED\0" + unstaged_patch
    )
    staged_files = nul_paths(
        git(repo, "diff", "--cached", "--name-only", "-z", "--no-ext-diff")
    )
    unstaged_files = nul_paths(
        git(repo, "diff", "--name-only", "-z", "--no-ext-diff")
    )
    untracked_files = nul_paths(
        git(repo, "ls-files", "--others", "--exclude-standard", "-z")
    )
    status_raw = git(
        repo, "status", "--porcelain=v1", "-z", "--untracked-files=all"
    ).stdout
    status_entries = parse_status_entries(status_raw)
    changed_paths = set(staged_files) | set(unstaged_files) | set(untracked_files)
    for entry in status_entries:
        changed_paths.add(entry["path"])
        if "original_path" in entry:
            changed_paths.add(entry["original_path"])
    diff_check = git(repo, "diff", "--cached", "--check", check=False)
    has_changes = bool(status_entries)

    return {
        "repo": str(repo),
        "branch": branch,
        "has_head": has_head,
        "has_changes": has_changes,
        "worktree_signature_sha256": (
            worktree_signature(tracked_patch, status_raw, repo, untracked_files)
            if has_changes
            else None
        ),
        "status_entries": status_entries,
        "changed_paths": sorted(changed_paths),
        "partially_staged_files": sorted(set(staged_files) & set(unstaged_files)),
        "has_staged_changes": bool(staged_files),
        "staged_signature_sha256": (
            hashlib.sha256(staged_patch).hexdigest() if staged_files else None
        ),
        "staged_files": staged_files,
        "staged_stat": text(
            git(repo, "diff", "--cached", "--stat", "--no-ext-diff")
        ),
        "staged_diff_check_ok": diff_check.returncode == 0,
        "staged_diff_check_output": (
            diff_check.stdout + diff_check.stderr
        ).decode("utf-8", errors="replace").strip(),
        "unstaged_files": unstaged_files,
        "untracked_files": untracked_files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Discover workspace Git repositories and inventory all staged, "
            "unstaged, and untracked paths without modifying Git."
        )
    )
    parser.add_argument(
        "repos",
        nargs="*",
        help="Explicit Git repository roots.",
    )
    parser.add_argument(
        "--workspace-root",
        action="append",
        default=[],
        help=(
            "Explicit IDE workspace folder to search for Git repositories. "
            "May be repeated."
        ),
    )
    parser.add_argument(
        "--workspace-file",
        action="append",
        default=[],
        help=(
            "VS Code .code-workspace file whose folder entries should be searched. "
            "May be repeated."
        ),
    )
    args = parser.parse_args()

    repos: list[Path] = []
    seen: set[Path] = set()
    skipped_workspace_paths: list[dict[str, str]] = []
    workspace_roots: list[Path] = [
        Path(value).expanduser().resolve() for value in args.workspace_root
    ]

    if not args.repos and not workspace_roots and not args.workspace_file:
        print(
            json.dumps(
                {
                    "error": (
                        "workspace scope is required; pass every IDE folder with "
                        "--workspace-root, a .code-workspace file with "
                        "--workspace-file, or explicit repository roots"
                    )
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

    try:
        for workspace_file in args.workspace_file:
            roots, skipped = workspace_file_roots(workspace_file)
            workspace_roots.extend(roots)
            skipped_workspace_paths.extend(skipped)

        for candidate in args.repos:
            repo = resolve_repo(candidate)
            if repo not in seen:
                repos.append(repo)
                seen.add(repo)

        unique_workspace_roots: list[Path] = []
        seen_workspace_roots: set[Path] = set()
        for root in workspace_roots:
            if root in seen_workspace_roots:
                continue
            unique_workspace_roots.append(root)
            seen_workspace_roots.add(root)

            if not root.exists():
                skipped_workspace_paths.append(
                    {"path": str(root), "reason": "workspace path does not exist"}
                )
                continue

            discovered = discover_repositories(root)
            if not discovered:
                skipped_workspace_paths.append(
                    {
                        "path": str(root),
                        "reason": "no Git repository found under workspace path",
                    }
                )
            for repo in discovered:
                if repo not in seen:
                    repos.append(repo)
                    seen.add(repo)

        inventory = [inspect(repo) for repo in repos]
    except (OSError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    print(
        json.dumps(
            {
                "workspace_inputs": {
                    "explicit_repositories": args.repos,
                    "workspace_roots": [str(path) for path in unique_workspace_roots],
                    "workspace_files": [
                        str(Path(path).expanduser().resolve())
                        for path in args.workspace_file
                    ],
                    "skipped_workspace_paths": skipped_workspace_paths,
                },
                "repositories": inventory,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
