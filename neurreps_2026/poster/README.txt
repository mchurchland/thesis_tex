NeurReps 2026 poster — MC200 sketch revision

poster.pdf is the one-page 61 x 85 cm portrait print master.
poster_preview.png is a screen preview.
poster.tex and assets/ are the editable LaTeX source.
neurreps_overleaf.zip is the self-contained Overleaf project (pdfLaTeX).

Layout: two-pane methods/sign-sweep band; three MC panels;
NARMA, critics' corner and conclusions below. The sign diagram shows one
five-node network realization in a Kamada–Kawai layout at 0%, 20% and 50% inhibitory edges.
All AUCs are ordinary performance AUCs; there are no win-percentage AUC plots.
Panel 1 uses a linear MC axis and displays input strengths 0.01 and 0.5.
Panel 4's CE/ER curves average all 24 input/radius/leak settings.

Compile here:
  latexmk -pdf -interaction=nonstopmode -halt-on-error poster.tex
Or run pdflatex twice to resolve the TikZ page anchors.

Regenerate six PNG figures from the full research repository:
  OPENBLAS_NUM_THREADS=1 python build_figures.py
Figure generation reuses checksum-verified stored MC200/NARMA summaries;
it does not run simulations. Overleaf uses the included PNGs directly.

MC200: delays 1-200; 5000 test samples. NARMA10: archived 500-sample test.
Both retain 1500 train, 500 validation and 500 washout samples.
SOURCES.md and poster_sources.json describe sources and analysis choices.
poster_validation.json records the final artifact checks.
The previous poster is archived under
archive/before_sketch_mc200_2026-11-22/.
