# EMCSDG 2026 Paper (Camera‑Ready)

This folder contains a submission-ready LaTeX paper with figures and tables generated from the repository outputs.

## Quick start (Overleaf recommended)
1. Create a new Overleaf project and upload the entire `paper/` folder contents (**only** `paper/`, not the whole repo).
2. Set the main file to `paper/main.tex`.
3. Use **pdfLaTeX** and **Biber** (Overleaf auto-detects this for `biblatex`).
4. Recompile twice after bibliography changes.

### If Overleaf says “compile timed out”
This usually happens when the Overleaf project contains large, non-LaTeX artifacts (e.g., `data/processed/*.parquet`, `.npy`, etc.) and the build takes too long just copying files.

Fix:
- Make a fresh Overleaf project that contains only:
  - `main.tex`
  - `references.bib`
  - `figures/*.pdf` (or `*.png`)
- Or, delete large folders/files from the Overleaf project (keep only `paper/`).

## Local compile (requires TeX Live + Biber)
From the repo root:

```bash
cd paper
pdflatex main.tex
biber main
pdflatex main.tex
pdflatex main.tex
```

## Regenerate tables / figures (optional)
This repo is set up so the system Python on macOS works out of the box:

```bash
/usr/bin/python3 scripts/export_paper_tables.py
MPLCONFIGDIR=/tmp/mplconfig /usr/bin/python3 scripts/regenerate_paper_figures.py
/usr/bin/python3 scripts/wordcount_tex.py
```

Notes:
- `scripts/regenerate_paper_figures.py` forces a headless-safe Matplotlib backend (`Agg`), but setting `MPLCONFIGDIR` avoids cache permission warnings in sandboxed environments.
- If you run `python3` via `pyenv`, you may not have `pandas/pyarrow/matplotlib/seaborn` installed; prefer `/usr/bin/python3`.
