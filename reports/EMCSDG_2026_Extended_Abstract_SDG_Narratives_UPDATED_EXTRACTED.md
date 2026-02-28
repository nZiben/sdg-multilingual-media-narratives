# Extracted text from EMCSDG_2026_Extended_Abstract_SDG_Narratives_UPDATED.docx

Extended Abstract

The United Nations’ Sustainable Development Goals (SDGs) provide a shared roadmap for sustainable and inclusive development, but public engagement and policy legitimacy depend on how SDGs are communicated in everyday media ecosystems. Comparative work on sustainability-related media agendas shows substantial cross-national variation in issue salience rather than a single global trend (Barkemeyer et al., 2013). Large-scale SDG monitoring using world news likewise reports very low overall SDG visibility and substantial regional differences in tone and attention (Czvetkó et al., 2021). These findings motivate a renewed cross-cultural, multilingual account of SDG narratives in digital media.

This study develops and evaluates a reproducible multilingual pipeline for mapping SDG-related coverage in global digital news and for detecting cross-cultural narrative differences at scale. The project aligns with the symposium theme of “Emerging Media for Communicating SDGs” by treating platform-distributed online news as an emerging, computationally measurable media layer: news flows are shaped by digital distribution, and they can be analyzed with scalable retrieval and NLP-based measurements to identify communication asymmetries relevant to SDG 10 (Reduced Inequalities) and SDG 17 (Partnerships for the Goals).

We address three research questions:
RQ1: Which SDGs receive the most attention in multilingual news, and how does the SDG distribution differ across language communities?
RQ2: What narrative themes (topics and lexical frames) co-occur with high-salience SDGs, and which themes appear stable versus punctuated over time?
RQ3: What biases arise from keyword-based SDG tagging in multilingual corpora, and how can supervised datasets improve measurement equivalence across languages?

Data are collected from The GDELT Project, which continuously monitors online news and provides structured metadata (including publication time and language), enabling scalable communication research (Leetaru & Schrodt, 2013; GDELT Project, 2015; Hopp et al., 2019). In an initial three-month pilot corpus of 56,000 deduplicated news records retrieved using SDG-relevant query terms across multiple languages, we apply text cleaning and quality filters (e.g., removing empty/low-information snippets and extreme short-length records). We then apply a weakly supervised SDG tagging step and compute descriptive and comparative statistics by SDG, time, and language.

Pilot results show a sharply uneven SDG attention landscape. In the pilot, 17,795 articles receive at least one SDG label, producing 20,782 article–SDG mentions (mean 1.17 SDGs per SDG-relevant article). SDG 17 (Partnerships for the Goals) dominates the discourse (11,722 mentions; ~56% of SDG mentions), followed by SDG 3 (Good Health and Well-Being; 2,200 mentions) and SDG 13 (Climate Action; 887 mentions). A cross-language salience heatmap for top languages and SDGs (Appendix Figure A1) indicates that SDG 17 is consistently the most prevalent goal across language communities, while English-language coverage exhibits a broader SDG portfolio (notably SDG 3, plus smaller visibility for SDG 7/8/11) compared to the more concentrated SDG profiles in the other high-volume languages in the pilot.

Temporal analysis of SDG mentions (aggregated monthly) suggests punctuated attention for some goals. SDG 17 remains high-volume throughout the pilot, whereas SDG 5 (Gender Equality) increases markedly in the latest month of the pilot (from 139 to 321 mentions), consistent with event-driven surges that can be detected even in a short window. Such punctuations are substantively important because they may reflect shocks (policy debates, crises, campaigns) that temporarily reshape public narratives and perceived SDG urgency.

To move beyond counts toward “how SDGs are talked about,” we add a cross-lingual semantic framing layer. We compute document embeddings (baseline TF–IDF + SVD), project them to a two-dimensional semantic map, and cluster the space (k-means; k=60) to approximate recurring lexical frames. The semantic map by language (Appendix Figure A2) reveals partial separation by language (e.g., a dense English region and a distinct Spanish region) alongside a shared manifold where multiple languages overlap near a central “spine,” suggesting shared thematic structure but language-conditioned framing and sourcing. Cluster top-terms further surface interpretable frame families (e.g., public health, climate, clean energy, water) as well as language-specific lexical markers that can bias unsupervised models if not controlled.

Language coverage in the pilot is multilingual but imbalanced: SDG-related mentions are most frequent in English (13,227) and Spanish (3,175), followed by German (1,230), French (802), Italian (543), Indonesian (337), Portuguese (306), Romanian (218), Chinese (203), and Turkish (120), with additional low-frequency languages. This imbalance implies that observed differences between “language communities” cannot be interpreted as cultural differences alone; they may also reflect source availability, query bias, and language-specific tagging sensitivity, underscoring the need for measurement-equivalence checks.

Ongoing work expands the corpus to a broader time horizon and increases analytic depth in three directions. First, we will implement supervised multilingual SDG tagging using openly available labeled corpora (OSDG-CD and SDGi Corpus) and quantify agreement with the keyword baseline to improve cross-language comparability (OSDG, UNDP IICPSD SDG AI Lab, & PPMI, 2022; Skrynnyk et al., 2024; United Nations Development Programme, 2024). Second, we will implement multilingual sentiment and framing analysis with careful validation to distinguish substantive narrative differences from translation/tooling artifacts. Third, we will build SDG co-mention and actor networks (countries, organizations, themes) to identify which partnerships are communicated, who is centered, and where communication gaps align with global inequality patterns. (Appendix Figures A1–A2 report pilot-only visualizations; full-year analyses will be reported in the full paper.)

Keywords: SDG 17 Partnerships for the Goals; SDG 10 Reduced Inequalities; multilingual content analysis; GDELT; cross-lingual semantic framing; SDG tagging & validation

References

Alsuhaibani, M., Gaanoun, K., & Qamar, A. M. (2025). Artificial intelligence-driven insights into Arab media’s sustainable development goals coverage. PeerJ Computer Science, 11, e3071. https://doi.org/10.7717/peerj-cs.3071

Barkemeyer, R., Figge, F., & Holt, D. (2013). Sustainability-related media coverage and socioeconomic development: A regional and North–South perspective. Environment and Planning C: Government and Policy, 31(4), 716–740. https://doi.org/10.1068/c11176j

Blei, D. M., Ng, A. Y., & Jordan, M. I. (2003). Latent Dirichlet Allocation. Journal of Machine Learning Research, 3, 993–1022.

Czvetkó, T., Honti, G., Sebestyén, V., & Abonyi, J. (2021). The intertwining of world news with Sustainable Development Goals: An effective monitoring tool. Heliyon, 7(2), e06174. https://doi.org/10.1016/j.heliyon.2021.e06174

Fankhauser, T., & Clematide, S. (2024). SDG classification using instruction-tuned LLMs. In Proceedings of the 9th edition of the Swiss Text Analytics Conference (pp. 148–156). Association for Computational Linguistics. https://aclanthology.org/2024.swisstext-1.13.pdf

GDELT Project. (2015). The GDELT Global Knowledge Graph (GKG) 2.1 Codebook [Technical documentation]. https://data.gdeltproject.org/documentation/GDELT-Global_Knowledge_Graph_Codebook-V2.1.pdf

Hopp, F. R., Fisher, J. T., Cornell, D., Huskey, R., & Weber, R. (2019). iCoRe: The GDELT interface for the advancement of communication research. Computational Communication Research, 1(1), 13–44. https://doi.org/10.5117/CCR2019.1.002.HOPP

Leetaru, K., & Schrodt, P. A. (2013). GDELT: Global data on events, location, and tone, 1979–present. Paper presented at the International Studies Association Annual Convention.

OSDG, UNDP IICPSD SDG AI Lab, & PPMI. (2022). OSDG Community Dataset (OSDG-CD) (2022.01) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.5792547

Pukelis, L., Bautista-Puig, N., Statulevičiūtė, G., Stančiauskas, V., Dikmener, G., & Akylbekova, D. (2022). OSDG 2.0: A multilingual tool for classifying text data by UN Sustainable Development Goals (SDGs). arXiv. https://doi.org/10.48550/arXiv.2211.11252

Skrynnyk, M., Disassa, G., Krachkov, A., & DeVera, J. (2024). SDGi Corpus: A comprehensive multilingual dataset for text classification by Sustainable Development Goals. In Proceedings of the 2nd Symposium on NLP for Social Good 2024 (CEUR Workshop Proceedings, Vol. 3764, Paper 3). https://ceur-ws.org/Vol-3764/paper3.pdf

United Nations Development Programme. (2024). SDGi Corpus [Data set]. Hugging Face. https://huggingface.co/datasets/UNDP/sdgi-corpus
