#!/usr/bin/env python3
"""Convert Markdown papers to DOCX using Pandoc and bundled md2docx assets."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
ASSETS = SKILL_DIR / "assets"
CSL_DIR = ASSETS / "citation-styles"
TEMPLATE_DIR = ASSETS / "docx-templates"

CSL_ALIASES = {
    "apa": "apa.csl",
    "ieee": "ieee.csl",
    "chicago": "chicago-author-date.csl",
    "chicago-author-date": "chicago-author-date.csl",
    "mla": "modern-language-association.csl",
    "modern-language-association": "modern-language-association.csl",
    "vancouver": "vancouver.csl",
    "nature": "nature.csl",
}

TEMPLATE_ALIASES = {
    "academic": "academic-reference.docx",
    "manuscript": "manuscript-reference.docx",
    "report": "report-reference.docx",
    "compact": "compact-reference.docx",
}


def resolve_asset(value: str | None, aliases: dict[str, str], directory: Path) -> Path | None:
    if not value:
        return None
    key = value.lower()
    filename = aliases.get(key, value)
    path = Path(filename)
    if not path.is_absolute():
        path = directory / filename
    if not path.exists():
        raise SystemExit(f"Asset not found: {path}")
    return path


def pandoc_command() -> list[str]:
    env_pandoc = os.environ.get("PANDOC")
    if env_pandoc:
        return [env_pandoc]
    found = shutil.which("pandoc")
    if found:
        return [found]
    conda = shutil.which("conda")
    if conda:
        return [conda, "run", "-n", "doc", "pandoc"]
    raise SystemExit("Pandoc not found. Install it or set PANDOC=/path/to/pandoc.")


def has_filter(name: str) -> bool:
    if shutil.which(name) is not None:
        return True
    env_pandoc = os.environ.get("PANDOC")
    return bool(env_pandoc and (Path(env_pandoc).expanduser().parent / name).exists())


def build_command(args: argparse.Namespace) -> tuple[list[str], Path]:
    md = Path(args.markdown).resolve()
    if not md.exists():
        raise SystemExit(f"Markdown file not found: {md}")
    if md.suffix.lower() not in {".md", ".markdown"}:
        raise SystemExit(f"Expected a Markdown file, got: {md}")

    out = Path(args.output).resolve() if args.output else md.with_suffix(".docx")
    template = resolve_asset(args.template, TEMPLATE_ALIASES, TEMPLATE_DIR)
    csl = resolve_asset(args.csl, CSL_ALIASES, CSL_DIR)
    bibliography = Path(args.bibliography).resolve() if args.bibliography else None
    if bibliography and not bibliography.exists():
        raise SystemExit(f"Bibliography not found: {bibliography}")

    cmd = pandoc_command() + [
        str(md.name),
        "--from=markdown+yaml_metadata_block+implicit_figures+pipe_tables",
    ]

    if args.crossref:
        if not has_filter("pandoc-crossref"):
            raise SystemExit("pandoc-crossref not found. See references/pandoc-crossref.md.")
        cmd.extend(["--filter", "pandoc-crossref"])

    cmd.append("--citeproc")

    if args.number_sections:
        cmd.append("--number-sections")
    if args.toc:
        cmd.append("--toc")
    if template:
        cmd.append(f"--reference-doc={template}")
    if csl:
        cmd.append(f"--csl={csl}")
    if bibliography:
        cmd.append(f"--bibliography={bibliography}")

    cmd.extend(["-o", str(out)])
    return cmd, md.parent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("markdown", help="Input Markdown paper")
    parser.add_argument("-o", "--output", help="Output DOCX path")
    parser.add_argument("--template", default="academic", help="Template alias or path")
    parser.add_argument("--csl", help="CSL alias or path. Omit to use Markdown YAML metadata.")
    parser.add_argument("--bibliography", help="BibTeX/BibLaTeX path. Omit to use Markdown YAML metadata.")
    parser.add_argument("--number-sections", action="store_true", default=True)
    parser.add_argument("--no-number-sections", action="store_false", dest="number_sections")
    parser.add_argument("--toc", action="store_true")
    parser.add_argument("--crossref", action="store_true", help="Enable pandoc-crossref filter")
    parser.add_argument("--check-only", action="store_true", help="Print command and validate paths without running Pandoc")
    args = parser.parse_args()

    cmd, cwd = build_command(args)
    print("Working directory:", cwd)
    print("Command:")
    print(" ".join(str(part) for part in cmd))

    if args.check_only:
        return 0

    result = subprocess.run(cmd, cwd=cwd)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
