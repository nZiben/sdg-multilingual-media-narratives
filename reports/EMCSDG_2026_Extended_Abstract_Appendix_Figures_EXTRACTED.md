# Extracted text from EMCSDG_2026_Extended_Abstract_Appendix_Figures.docx

Appendix: Figures example

Note: This study presents findings from a focused, three-month data sample, which served to validate the core methodology and pipeline. The subsequent full paper will expand upon this foundation with a comprehensive analysis across an extended timeframe and a significantly larger multilingual corpus, accompanied by a complete set of visualizations.

Figure A1. SDG counts by language (top languages & SDGs)

Caption. Heatmap of SDG mention counts by language for the most frequent languages and most frequent SDGs in the pilot corpus.

Interpretation (pilot):

Across all displayed language communities, SDG 17 (Partnerships for the Goals) is the dominant category, suggesting that SDG discourse in news is frequently framed through cooperation, funding, and international coordination narratives.

English shows the broadest SDG portfolio, with substantial visibility not only for SDG 17 but also SDG 3 (Good Health and Well-Being) and smaller but non-trivial coverage of SDG 11 (Sustainable Cities), SDG 7 (Clean Energy), and SDG 8 (Decent Work).

Spanish coverage is also strongly concentrated in SDG 17, with comparatively lower counts for the other goals shown, indicating a narrower topical footprint within this pilot sample.

Lower-frequency languages in the pilot exhibit sparse counts across non-SDG17 goals; this may reflect both genuine agenda differences and sampling effects (source availability, query bias), motivating supervised validation and expanded data collection.

Figure A2. Semantic map (top languages)

Caption. Two-dimensional semantic projection of article representations for the most frequent languages (baseline TF–IDF + SVD embeddings with a 2D projection). Each point is an article; colors indicate language.

Interpretation (pilot):

The semantic space exhibits partial separation by language: English forms a dense region, while Spanish occupies a visually distinct region, suggesting systematic differences in lexical framing or coverage focus across language communities.

A shared “spine” of overlap near the center indicates that multilingual SDG discourse also shares common frames and vocabulary (e.g., institutional cooperation and public policy), consistent with a globalized news agenda for SDG-related content.

This visualization motivates quantitative cross-language divergence measures (e.g., cluster-distribution Jensen–Shannon divergence) and the use of multilingual sentence embeddings in the full paper to reduce language-specific vectorization artifacts.
