# NeurReps 2026 extended abstract

This folder contains a complete anonymous submission draft for the NeurReps 2026 non-archival Extended Abstract Track. The manuscript is a direct four-page condensation of `../thesis.tex`, rather than a separately reframed paper.

## Submission artifact

- `paper.pdf` -- anonymous review PDF: four pages of scientific content plus two pages of references.
- `submission_fields.md` -- title, plain-text abstract, TL;DR, relevance statement, keywords, and upload notes.

## Source and figures

- `paper.tex` -- single-file manuscript source, as requested by the official template.
- `references.bib` -- bibliography source.
- `figures/architecture_tradeoff.png` -- the architecture comparison used in `thesis.tex` (`thesis/architecture/50per.png`).
- `figures/raw_rho_performance_summary.pdf` -- the raw-spectral-radius summary used in `thesis.tex` (`thesis/raw_rho/raw_rho_performance_summary.pdf`).
- `jmlr.cls` and `jmlrutils.sty` -- local copies of the official template dependencies.
- `template/` -- the downloaded official template package and its instructions.

## Rebuild

From this directory:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error paper.tex
```

## Relationship to the full paper

- The title and abstract are taken directly from `thesis.tex`.
- The introduction, methods, result ordering, caveats, and limitations compress the corresponding sections of `thesis.tex`.
- Both figures are existing main-text figures from `thesis.tex`; neither was re-plotted for the workshop draft.
- The final NeurReps paragraph is the only workshop-specific framing.

## Review-version checks

- Uses `\documentclass[mlabstract,onecolumn]{jmlr}` from the official NeurReps 2026 template.
- Preserves the required Extended Abstract Track watermark.
- Contains no author block or PDF author metadata.
- Uses only the packages loaded or explicitly required by the official template.
- Keeps all prose, equations, and figures within four pages; the bibliography begins after an explicit page break.

Before submission, confirm the current requirements on the [official NeurReps website](https://neurreps.org/) and inspect the final PDF once more after any edits.
