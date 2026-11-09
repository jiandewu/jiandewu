# pandoc-crossref Notes

Use `pandoc-crossref` when the paper needs automatic figure/table/equation numbering and text references such as `Figure 1` or `Table 2`.

## Markdown labels

```markdown
![Workflow](figures/workflow.png){#fig:workflow width=80%}

Table: Dataset summary {#tbl:data}

| Dataset | Rows |
|---|---:|
| Example | 1000 |
```

## Text references

```markdown
As shown in @fig:workflow, the model has two stages.
Table @tbl:data summarizes the dataset.
```

## Pandoc command order

Run `pandoc-crossref` before `--citeproc`:

```bash
pandoc paper.md --filter pandoc-crossref --citeproc -o paper.docx
```

## Local installation notes

The conda-forge package may be unavailable. A GitHub release binary must match both CPU architecture and Pandoc version.

Check the architecture first:

```bash
uname -m
pandoc --version
```

- Use an ARM64 release for `aarch64` or `arm64`.
- Use an X64 release for `x86_64` or `amd64`.
- A mismatched binary can fail with `cannot execute binary file: Exec format error`.
- Prefer a `pandoc-crossref` release built for the installed Pandoc version.

If `tar` cannot extract `.tar.xz`, install `xz` in the conda environment that provides Pandoc:

```bash
conda install -n <env> -c conda-forge xz
```
