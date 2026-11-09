# Markdown Paper Authoring Patterns

## YAML metadata

Use a YAML block at the top of the paper:

```yaml
---
title: "Paper Title"
author:
  - "Author One"
date: "2026-07-16"
abstract: |
  Write the abstract here.
bibliography: ../papers.bib
csl: ../styles/apa.csl
reference-section-title: References
link-citations: true
---
```

When using `scripts/md2docx_convert.py`, omit `csl:` or use a document-local path and select a bundled style with `--csl apa`.

## Sections

Use `#`, `##`, and `###`. Do not manually write section numbers when using Pandoc `--number-sections`.

## Tables

```markdown
Table: Comparison of methods {#tbl:methods}

| Method | Parameters | Use |
|---|---:|---|
| Full fine-tuning | 100% | High-resource settings |
| Adapter | <5% | Modular adaptation |
```

## Figures

```markdown
![Adapter workflow](figures/adapter-workflow.png){#fig:adapter width=80%}
```

## Citations

Use Pandoc citation syntax:

```markdown
Parameter-efficient tuning is widely used [@houlsby2019parameter].
@houlsby2019parameter introduced adapter-based tuning.
This method was later adapted to multimodal settings [-@zhang-etal-2023-video].
```

Use `nocite` for references that should appear even if not cited:

```yaml
nocite: |
  @*
```

## Defaults file caveat

Pandoc resolves `reference-doc` in defaults files relative to the current working directory, not necessarily the defaults file location. Prefer the bundled converter, or run from a known document directory with an explicitly resolved path.
