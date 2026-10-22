# Quantum Error Correction and Machine-Learning Decoders

A self-contained Quarto graduate textbook, from binary algebra and quantum channels to conventional and machine-learning decoding. Research edition: 23 October 2026.

**Read online:** https://xing-phys.github.io/quantum-error-correction-ml-decoding/

The book contains 17 numbered teaching chapters, an introduction, a notation appendix, a complete bibliography, worked exercises, interactive laboratories, and a combined PDF. Frontier preprints and published results are distinguished explicitly. The coverage is a broad authored synthesis, not an exhaustive systematic literature review.

## Build

Install Quarto 1.10.18 and a working LuaLaTeX distribution (or use `quarto install tinytex`). Inkscape converts SVG figures for PDF; matching PDF/PNG originals are provided in `figs/`.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python scripts/merge_bibliography.py
quarto render
.venv/bin/python scripts/verify.py
```

Open `_site/index.html`, serve `_site/`, or run `quarto preview --no-browser`. The preview command reports its URL. The combined offline edition is `_site/qec-ml-textbook.pdf`. Builds use checked-in data and do not execute numerical examples.

## Reproduce the laboratories

```bash
julia --startup-file=no --project=. examples/exact_decoding.jl
.venv/bin/python examples/neural_coset.py
.venv/bin/python examples/surface_memory.py --shots 20000
.venv/bin/python scripts/make_figures.py
.venv/bin/python scripts/verify.py
```

Julia 1.12.6 and Python 3.12.3 were used for the recorded run. Julia numerics use standard libraries only. `requirements-lock.txt` records all installed Python versions; `requirements.txt` lists direct dependencies. The surface experiment has 300,000 total shots and records explicit seeds and Wilson intervals. Its decode timing is a machine-dependent batch measurement. The neural example is an exact-oracle-checked seven-qubit teaching problem, not a scalability result.

## Layout and maintenance

- Root `.qmd` files: introduction, 17 chapters, appendix, bibliography.
- `_quarto.yml`: chapter order, metadata, responsive HTML and combined PDF settings.
- `assets/refs-*.bib`: verified source fragments; merge into `assets/bibliography.bib`.
- `assets/macros.sty` and `assets/mathjax-config.html`: equivalent PDF/HTML math macros.
- `assets/styles.css`, themes, and `interactives.js`: reading design and browser-local widgets.
- `examples/`, `data/`, `scripts/`, `figs/`: reproducible computational sources and original diagrams.
- `.github/workflows/publish.yml`: render, verification, and GitHub Pages deployment.

When updating scientific claims, verify primary papers and their versions, retain noise and metric assumptions, and update the literature-audit date only after a new search. After changes to equations, citations, figures, navigation, or shared styling, render both formats, run verification, and visually inspect representative HTML and PDF pages.

Publication is authorized by the project request. GitHub Pages deploys from `main` through Actions. Generated `_site/` and local environments are ignored by Git.
