# SDG Multilingual Media Narratives — Notebooks

This folder contains a minimal, reproducible notebook pipeline based on the project description in:
"Cross-Cultural Media Narratives: A Multilingual Analysis of SDG Coverage" (user-provided docx).

## Notebooks
- 00_setup_and_config.ipynb — folders, helpers, SDG keyword JSON
- 01_collect_gdelt_news.ipynb — collect news via GDELT DOC 2.0 API
- 02_preprocess_and_sdg_tagging.ipynb — clean, normalize, keyword-tag SDGs (multi-label)
- 03_analysis_trends_topics_networks.ipynb — trends, LDA topics (baseline), SDG↔country edge list + simple network plot
- 04_social_media_collection_scaffold.ipynb — scaffold for X/Weibo/etc.

## Quickstart
1) Create env:
   python -m venv .venv && source .venv/bin/activate
2) Install:
   pip install -r requirements.txt
3) Run notebooks in order.

## Notes
- Keyword tagging is a baseline; for publication-quality results, consider a multilingual classifier and manual validation.
- For large graphs, export edge lists to Gephi or similar tools.
