#!/usr/bin/env python3
"""Create or update a day section in a weekly Markdown work log."""

from __future__ import annotations

import argparse
import os
import re
from datetime import date, timedelta
from pathlib import Path


def default_root() -> Path:
    configured = os.environ.get("WEEKLY_WORKLOG_ROOT")
    if configured:
        return Path(configured).expanduser()

    script_path = Path(__file__).resolve()
    for parent in script_path.parents:
        if parent.name == "Notebook":
            return parent / "worklog"

    return Path.home() / "Notebook" / "worklog"


DEFAULT_ROOT = default_root()


def parse_day(value: str | None) -> date:
    if value:
        return date.fromisoformat(value)
    return date.today()


def monday_for(day: date) -> date:
    return day - timedelta(days=day.weekday())


def weekly_path(root: Path, day: date) -> Path:
    monday = monday_for(day)
    return root / f"{monday:%Y}" / f"{monday:%Y%m%d}.md"


def default_body() -> str:
    return """### 总结

-

### 项目

-

### 提交

-

### 待办

-
"""


def build_section(day: date, content: str) -> str:
    title = f"## {day.isoformat()}"
    stripped = content.strip()
    if not stripped:
        stripped = default_body().strip()

    if stripped.startswith(title):
        section = stripped
    else:
        section = f"{title}\n\n{stripped}"
    return section.rstrip() + "\n"


def initial_week_text(day: date) -> str:
    monday = monday_for(day)
    return f"# 工作日志：{monday:%Y-%m-%d} 当周\n\n"


def _section_body(section: str) -> str:
    return re.sub(r"^## \d{4}-\d{2}-\d{2}\n?", "", section, count=1).strip()


def _heading_blocks(body: str) -> list[tuple[str, list[str]]]:
    matches = list(re.finditer(r"^### (.+)$", body, re.MULTILINE))
    if not matches:
        return [("", body.splitlines())]

    blocks: list[tuple[str, list[str]]] = []
    if matches[0].start() > 0:
        blocks.append(("", body[: matches[0].start()].splitlines()))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        blocks.append((match.group(1).strip(), body[match.end() : end].splitlines()))
    return blocks


def _clean_lines(lines: list[str]) -> list[str]:
    return [line.rstrip() for line in lines if line.strip() and line.strip() != "-"]


def _project_key(line: str) -> str | None:
    match = re.match(r"^\s*-\s+`([^`]+)`(?:：|:)\s*", line)
    return match.group(1).strip() if match else None


def _project_detail(line: str) -> str:
    return re.sub(r"^\s*-\s+`[^`]+`(?:：|:)\s*", "", line)


def _merge_lines(existing: list[str], incoming: list[str], *, projects: bool = False) -> list[str]:
    result: list[str] = []

    def add_line(line: str) -> None:
        key = _project_key(line) if projects else None
        if key:
            matching = next((index for index, old in enumerate(result) if _project_key(old) == key), None)
            if matching is not None:
                old = result[matching]
                # Append only clauses not already recorded, so re-running the
                # same update is idempotent.
                known = {part.strip() for part in _project_detail(old).split("；")}
                new_parts = [
                    part.strip()
                    for part in _project_detail(line).split("；")
                    if part.strip() and part.strip() not in known
                ]
                if new_parts:
                    result[matching] = "；".join([old.rstrip(), *new_parts])
                return
        if line not in result:
            result.append(line)

    # Normalize the existing project section first, so old interleaved entries
    # are grouped before the new terminal/session update is added.
    for line in _clean_lines(existing):
        add_line(line)
    for line in _clean_lines(incoming):
        add_line(line)
    return result


def merge_day_sections(existing: str, incoming: str) -> str:
    """Merge a new update without deleting another session's same-day work."""
    old_blocks = _heading_blocks(_section_body(existing))
    new_blocks = _heading_blocks(_section_body(incoming))
    # Normalize every existing block, including ones the incoming update does not
    # touch, so untouched sections do not keep stray blank lines or placeholders.
    merged: dict[str, list[str]] = {
        heading: _merge_lines(lines, [], projects=heading == "项目")
        for heading, lines in old_blocks
    }
    order = [heading for heading, _ in old_blocks]
    for heading, lines in new_blocks:
        if heading not in merged:
            merged[heading] = []
            order.append(heading)
        merged[heading] = _merge_lines(merged[heading], lines, projects=heading == "项目")

    parts: list[str] = []
    for heading in order:
        lines = merged[heading]
        if heading:
            parts.append(f"### {heading}\n\n" + "\n".join(lines))
        elif lines:
            parts.append("\n".join(lines))
    return "\n\n".join(parts).strip()


def upsert_section(text: str, day: date, section: str) -> str:
    day_heading = re.escape(day.isoformat())
    pattern = re.compile(
        rf"^## {day_heading}\n.*?(?=^## \d{{4}}-\d{{2}}-\d{{2}}\n|\Z)",
        re.MULTILINE | re.DOTALL,
    )

    if pattern.search(text):
        def replace(match: re.Match[str]) -> str:
            merged = merge_day_sections(match.group(0), section)
            return build_section(day, merged).rstrip() + "\n\n"

        updated = pattern.sub(replace, text).rstrip() + "\n"
    else:
        updated = text.rstrip() + "\n\n" + section.rstrip() + "\n"
    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", help="Work-log date as YYYY-MM-DD. Defaults to today.")
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="Work-log root directory.")
    parser.add_argument("--content-file", help="Markdown body or full day section to upsert.")
    parser.add_argument("--print-path", action="store_true", help="Print the target weekly file path and exit.")
    args = parser.parse_args()

    day = parse_day(args.date)
    root = Path(args.root).expanduser()
    path = weekly_path(root, day)

    if args.print_path:
        print(path)
        return 0

    if args.content_file:
        content = Path(args.content_file).read_text(encoding="utf-8")
    else:
        content = default_body()

    path.parent.mkdir(parents=True, exist_ok=True)
    text = path.read_text(encoding="utf-8") if path.exists() else initial_week_text(day)
    section = build_section(day, content)
    path.write_text(upsert_section(text, day, section), encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
