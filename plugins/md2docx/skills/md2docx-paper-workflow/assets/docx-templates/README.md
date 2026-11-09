# DOCX reference templates for Pandoc

These `.docx` files are Pandoc `--reference-doc` templates. Pandoc reads their Word styles and applies them to generated `.docx` files; template body text is not copied into the output.

## Templates

| File | Purpose |
|---|---|
| `academic-reference.docx` | Standard academic paper style, Times New Roman, 12 pt, formal spacing |
| `manuscript-reference.docx` | Submission draft style, Times New Roman, 12 pt, double spacing |
| `report-reference.docx` | Project report style, Arial, clear heading hierarchy |
| `compact-reference.docx` | Compact handout or internal note style, smaller type and margins |

## Provenance and license

All four files are modified copies of Pandoc's default reference document
(`pandoc -o reference.docx --print-default-data-file reference.docx`, Copyright
John MacFarlane). Their Word styles and sample text were changed; the
`report` template was also re-saved in Microsoft Word. They are distributed
under the GNU General Public License, version 2 or later, the license of
Pandoc's data files; see `COPYING.md` in this directory. This license applies
to these `.docx` files only, not to the rest of the plugin.

## Usage

Prefer the bundled converter, which resolves these files by alias:

```bash
python <skill-dir>/scripts/md2docx_convert.py paper.md --template academic --csl apa -o paper.docx
```

Or call Pandoc directly from the Markdown file's directory:

```bash
pandoc paper.md \
  --citeproc \
  --reference-doc=<skill-dir>/assets/docx-templates/academic-reference.docx \
  --csl=<skill-dir>/assets/citation-styles/apa.csl \
  -o paper.docx
```

`<skill-dir>` is the `md2docx-paper-workflow` skill directory.
