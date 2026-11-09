---
name: md2docx-paper-workflow
description: Convert academic or research Markdown papers into DOCX with Pandoc, BibTeX bibliographies, CSL citation styles, Word reference-doc templates, figures, tables, and optional pandoc-crossref figure/table references. Use when working on Markdown-to-DOCX paper/report workflows, Pandoc YAML metadata, .bib citations, .csl styles, reference-doc templates, or troubleshooting the Pandoc installation.
---

# MD to DOCX Paper Workflow

## Purpose

Use this skill to write, validate, and convert research Markdown into DOCX with reproducible Pandoc settings. Prefer the bundled assets and scripts before inventing new commands.

## Bundled Assets

- `assets/citation-styles/`: APA, IEEE, Chicago author-date, MLA, Vancouver, and Nature CSL files.
- `assets/docx-templates/`: Pandoc `--reference-doc` templates: academic, manuscript, report, compact.
- `scripts/md2docx_convert.py`: deterministic converter around Pandoc and the bundled assets.
- `references/paper-markdown.md`: Markdown paper authoring patterns.
- `references/pandoc-crossref.md`: figure/table cross-reference and ARM64 installation notes.

## Workflow

1. Inspect the Markdown file and its directory.
2. Confirm YAML metadata includes the needed fields: `title`, `author`, `bibliography`, `csl`, and `reference-section-title` when citations are needed.
3. Prefer Pandoc citation syntax: `[@bib-key]`, `@bib-key`, and `[-@bib-key]`.
4. Keep bibliography data in `.bib`; do not copy full reference entries into Markdown unless the user explicitly wants static references.
5. Use a bundled CSL path when the target style is known, or leave an existing valid `csl:` metadata path alone.
6. Use a bundled Word template through `--reference-doc` when generating DOCX.
7. Run a smoke conversion before reporting completion whenever Pandoc is available.

## Quick Commands

From the Markdown file directory:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/md2docx_convert.py paper.md --template academic --csl apa -o paper.docx
```

Claude Code substitutes `${CLAUDE_SKILL_DIR}` with this skill's directory; in other agents, replace it with the directory that contains this `SKILL.md`.

The converter finds Pandoc in this order: the `PANDOC` environment variable, `pandoc` on `PATH`, then `conda run -n doc pandoc`.

To use a specific Pandoc executable:

```bash
PANDOC=/path/to/pandoc python ${CLAUDE_SKILL_DIR}/scripts/md2docx_convert.py paper.md --template academic -o paper.docx
```

If the Markdown already has correct YAML `bibliography:` and `csl:` fields, do not add duplicate CLI `--bibliography` or `--csl` options unless overriding is intentional.

## Path Rules

Pandoc resolves most document-local relative paths from the current working directory. Run Pandoc from the Markdown file's directory unless the user has a reason not to.

For templates and CSL files, let the converter resolve bundled assets relative to its own real path. This works when the skill is installed through a symbolic link.

## Citation Styles

Supported CSL shortcuts for `scripts/md2docx_convert.py --csl`:

- `apa`
- `ieee`
- `chicago-author-date`
- `mla` or `modern-language-association`
- `vancouver`
- `nature`

Supported template shortcuts for `--template`:

- `academic`
- `manuscript`
- `report`
- `compact`

## Cross References

For automatic figure/table numbering, use `pandoc-crossref` and labels such as `#fig:workflow` or `#tbl:methods`. Read `references/pandoc-crossref.md` before installing or troubleshooting it. Match the binary to the machine architecture and Pandoc version.

## Validation

Before final response, prefer:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/md2docx_convert.py paper.md --template academic --check-only
```

For generated DOCX, verify Pandoc exits successfully. If `soffice` and `pdftoppm` are unavailable, state that visual rendering was not performed.
