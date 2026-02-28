# Cross-Cultural Media Narratives of the SDGs: A Multilingual Analysis of Global Digital News

*Draft paper text expanded from the provided extended abstract + appendix figure notes. Replace bracketed placeholders (e.g., `[PILOT_START–PILOT_END]`) with your final study details.*

## Abstract (polished)
The United Nations Sustainable Development Goals (SDGs) provide a shared framework for sustainable and inclusive development, yet public engagement and policy legitimacy depend on how SDGs are communicated within everyday media ecosystems. Prior research shows substantial cross-national variation in sustainability-related issue salience rather than a single global trend, and large-scale monitoring suggests low overall SDG visibility with pronounced regional differences in attention and tone. Building on these insights, this paper develops and evaluates a reproducible multilingual pipeline for mapping SDG-related coverage in global digital news and for detecting cross-cultural narrative differences at scale. Using a three-month pilot corpus of **56,000** deduplicated news records collected from GDELT and filtered for text quality, we apply a weakly supervised, multilingual SDG-tagging baseline and then quantify variation by SDG, language community, and time. In the pilot, **17,795** articles receive at least one SDG label, yielding **20,782** article–SDG mentions (mean **1.17** SDGs per SDG-relevant article). Attention is sharply uneven: **SDG 17 (Partnerships)** accounts for **11,722** mentions (**56.4%**), followed by **SDG 3 (Health)** with **2,200** (**10.6%**) and **SDG 13 (Climate)** with **887** (**4.3%**). A cross-lingual semantic framing layer (TF–IDF + SVD embeddings, 2D projection, k-means clustering with *k* = 60) reveals partial language separation alongside a shared manifold of overlapping frames, motivating quantitative divergence measures and supervised validation. We conclude with a roadmap for scaling the pipeline to longer time horizons, improving cross-language measurement equivalence using labeled SDG datasets, and extending analysis to sentiment, framing, and actor/co-mention networks relevant to SDG 10 (Reduced Inequalities) and SDG 17 (Partnerships).

**Keywords:** SDG 17 Partnerships for the Goals; SDG 10 Reduced Inequalities; multilingual content analysis; GDELT; cross-lingual semantic framing; SDG tagging & validation

## 1. Introduction
The SDGs are a globally recognized agenda, but their effectiveness depends on how they are translated into public meaning and political legitimacy through communication. Digital news—distributed via online platforms and indexed at scale—constitutes an increasingly measurable “emerging media” layer through which SDG narratives circulate. Yet comparative sustainability-communication research consistently finds that issue salience varies across regions and countries, while global-scale monitoring suggests that SDG-related coverage can be both low overall and highly uneven across contexts. These patterns motivate a multilingual approach that can (a) map what SDGs are visible in news at scale and (b) characterize how SDGs are framed across language communities.

This paper contributes a reproducible multilingual pipeline that links (i) scalable news retrieval, (ii) baseline SDG tagging, and (iii) cross-lingual narrative mapping via embeddings and clustering. The pipeline is designed to support comparative questions central to SDG 10 and SDG 17: which SDG topics receive attention, which populations or regions may be under-represented in dominant narratives, and whether “partnership” discourse is communicated as concrete cooperation versus abstract institutional signaling.

## 2. Research questions
We address three research questions (RQs):

- **RQ1 (Agenda distribution):** Which SDGs receive the most attention in multilingual news, and how does the SDG distribution differ across language communities?
- **RQ2 (Narratives over time):** What narrative themes (topics and lexical frames) co-occur with high-salience SDGs, and which themes appear stable versus punctuated over time?
- **RQ3 (Measurement equivalence):** What biases arise from keyword-based SDG tagging in multilingual corpora, and how can supervised datasets improve cross-language comparability?

## 3. Data and corpus construction
### 3.1 Data source
We use **GDELT** as the primary source for global digital news metadata and text snippets. GDELT continuously monitors online news and provides structured fields such as publication time and language, enabling large-scale computational communication research.

### 3.2 Pilot sampling and preprocessing
The pilot study uses a focused **three-month window** (`[PILOT_START–PILOT_END]`) as a validation step for the end-to-end methodology. We retrieve a deduplicated corpus of **56,000** news records via SDG-relevant query terms across languages, then apply text cleaning and quality filters (e.g., removing empty/low-information snippets and extremely short records).

**Operational note for reproducibility (optional to include):** In the accompanying codebase, GDELT DOC 2.0 collection is implemented via windowed queries (e.g., 90-day windows) with deduplication by URL.

## 4. SDG tagging (weak supervision baseline)
### 4.1 Motivation
A publication-quality SDG classifier typically requires annotated training data and cross-language validation. As a baseline, we implement **weakly supervised SDG tagging** via multilingual keyword matching. This provides fast, transparent labels suitable for exploratory analysis while also enabling explicit measurement-bias auditing (RQ3).

### 4.2 Procedure
Each record’s analysis text is constructed as `title + ". " + snippet`, normalized for whitespace and encoding. SDG keyword sets are compiled into case-insensitive regular expressions and applied to each document. Labels are **multi-label**: a single article can map to multiple SDGs.

### 4.3 Pilot labeling yield
In the pilot, **17,795** articles receive at least one SDG label (≈ **31.8%** of retrieved records), producing **20,782** article–SDG mentions (mean **1.17** SDGs per SDG-relevant article). The sizable “retrieved but unlabeled” remainder highlights the importance of (i) expanding multilingual lexicons, (ii) handling morphological variation and polysemy, and (iii) moving toward supervised multilingual tagging.

## 5. Cross-lingual semantic framing and narrative divergence
### 5.1 Rationale
Counts alone cannot capture *how* SDGs are discussed. To measure narrative structure across languages, we add a cross-lingual semantic framing layer that maps documents into a shared vector space and compares language-conditioned distributions over narrative clusters.

### 5.2 Embeddings, 2D semantic map, and clustering (pilot)
For each document, we compute embeddings using a lightweight, reproducible baseline:

- **Vectorization:** TF–IDF with bounded feature size (e.g., up to 200k features; 1–2 grams; `min_df = 3`).
- **Dimensionality reduction (embeddings):** TruncatedSVD to **256** dimensions with L2 normalization.
- **2D projection:** UMAP if available; otherwise PCA to 2D for visualization.
- **Clustering:** HDBSCAN if available; otherwise **k-means** with *k* = **60** (pilot uses the k-means fallback).

Clusters are interpreted using within-cluster TF–IDF top terms. In the pilot semantic framing run, prominent cluster families include public health (e.g., “public health”, “health care”, “mental health”), climate (e.g., “climate change”), clean energy (e.g., “clean energy”, “energy transition”), and water (e.g., “drinking water”, “water quality”), alongside language- and outlet-driven “general news” clusters.

### 5.3 Divergence metric
To quantify cross-language narrative differences, we compute **Jensen–Shannon divergence (JSD)** between each pair of languages’ cluster-distribution vectors (over the shared set of narrative clusters). JSD values closer to 0 indicate similar distributions; larger values indicate more distinct narrative cluster mixes. Because language sample sizes are often imbalanced, JSD results should be reported alongside per-language sample sizes and (ideally) permutation tests or bootstrap confidence intervals.

## 6. Results (pilot)
### 6.1 SDG attention is sharply uneven (RQ1)
Pilot SDG mentions are concentrated in a small number of goals:

- **Total SDG mentions:** 20,782
- **SDG 17 (Partnerships):** 11,722 (**56.4%**)
- **SDG 3 (Health):** 2,200 (**10.6%**)
- **SDG 13 (Climate):** 887 (**4.3%**)
- **All other SDGs combined:** 5,973 (**28.7%**)

This pattern suggests that SDG discourse in news is frequently framed through cooperation, funding, and international coordination narratives (SDG 17), with health and climate forming secondary high-salience anchors.

### 6.2 Language coverage is multilingual but imbalanced (RQ1)
SDG-related mentions are concentrated in a small number of languages (pilot counts):

- **English:** 13,227 (**63.7%** of all SDG mentions)
- **Spanish:** 3,175 (**15.3%**)
- **German:** 1,230 (**5.9%**)
- **French:** 802 (**3.9%**)
- **Italian:** 543 (**2.6%**)
- **Indonesian:** 337 (**1.6%**)
- **Portuguese:** 306 (**1.5%**)
- **Romanian:** 218 (**1.0%**)
- **Chinese:** 203 (**1.0%**)
- **Turkish:** 120 (**0.6%**)
- **Other languages (combined):** 621 (**3.0%**)

This imbalance implies that cross-language differences cannot be interpreted as “cultural differences” alone: they can also reflect source availability, query bias, and language-specific tagging sensitivity. Measurement-equivalence checks are therefore a core component of the full paper’s design.

### 6.3 Temporal dynamics show punctuated attention (RQ2)
Monthly aggregation of SDG mentions indicates punctuated attention for some goals. In the pilot window, SDG 17 remains high-volume throughout, while SDG 5 (Gender Equality) increases markedly in the latest month, rising from **139** to **321** mentions (Δ = **+182**, **+131%**, 2.31×). Even in a short window, these punctuations are substantively important because they may reflect shocks (policy debates, crises, campaigns) that temporarily reshape SDG urgency in public narratives.

### 6.4 Semantic maps reveal partial separation plus shared frames (RQ2)
The pilot semantic map (Appendix Figure A2) shows partial separation by language: English forms a dense region, Spanish occupies a distinct extended region, and multiple languages overlap along a shared “spine” near the center. This structure is consistent with (i) shared global frames (institutional cooperation and policy discourse) and (ii) language-conditioned framing and sourcing that differentiates coverage even when discussing similar SDG themes.

As an illustration of divergence magnitudes, cluster-distribution JSD values (pilot framing run) vary substantially across language pairs (e.g., **English–Spanish JSD ≈ 0.635**; **English–German JSD ≈ 0.387**; **Spanish–Portuguese JSD ≈ 0.477**). These should be interpreted as exploratory indicators pending sample-size controls and supervised measurement validation.

## 7. Discussion
The pilot results point to three substantive implications for SDG communication research.

First, the dominance of SDG 17 suggests that SDG coverage may be “meta-framed” through partnerships, institutions, and coordination rather than through goal-specific problem/solution narratives. This raises the possibility that public-facing SDG discourse is driven by institutional reporting cycles, funding announcements, and diplomatic coordination, potentially crowding out problem-centered narratives for lower-visibility goals.

Second, language imbalances and partial semantic separation underscore that multilingual “coverage differences” can encode both genuine agenda variation and infrastructural asymmetries (media supply, indexing coverage, and query sensitivity). For SDG 10 and SDG 17, this matters because communication gaps can mirror inequality patterns—some communities may be consistently under-represented in the mediated SDG agenda.

Third, the semantic-framing layer demonstrates a tractable path from descriptive monitoring (“how much attention?”) to narrative measurement (“what frames?”). The combination of embedding spaces, interpretable clusters, and divergence statistics allows researchers to identify where languages converge on shared frames and where they diverge into distinct narrative regions.

## 8. Limitations
Key limitations that the full paper should address explicitly:

- **Keyword-tagging bias:** Multilingual lexicons are incomplete and uneven across languages; polysemy and morphology can drive false positives/negatives.
- **Sampling/query bias:** Retrieval terms may over-represent certain themes (e.g., “climate change”) and under-represent SDG discourse expressed without canonical SDG terminology.
- **Text granularity:** Snippets and titles may omit context; outlet practices differ by language.
- **Language imbalance:** Differences in volume complicate cross-language comparison; results must be normalized and validated.
- **Model artifacts:** TF–IDF + SVD can reflect language-specific surface forms; multilingual sentence embeddings may reduce but not eliminate such artifacts.

## 9. Conclusion and roadmap for the full paper
This study proposes a reproducible multilingual pipeline for SDG media monitoring and cross-cultural narrative comparison. The pilot validates core components—retrieval, filtering, baseline SDG tagging, and semantic framing—and reveals a strongly uneven SDG attention landscape dominated by SDG 17 and mediated through multilingual but imbalanced news flows.

The full paper will expand the corpus to a broader time horizon and increase analytic depth in three directions:

1. **Supervised multilingual SDG tagging:** Train/evaluate classifiers using open labeled corpora (e.g., OSDG Community Dataset and SDGi Corpus) and quantify agreement with the keyword baseline to improve cross-language comparability.
2. **Validated sentiment and framing:** Implement multilingual sentiment/framing analysis with careful validation to separate substantive narrative differences from translation/tooling artifacts.
3. **Co-mention and actor networks:** Build SDG co-mention and actor networks (countries, organizations, themes) to identify which partnerships are communicated, who is centered, and where communication gaps align with global inequality patterns.

## Appendix: Pilot data points (copy/paste)
## Paper-ready figure captions (pilot)
**Figure A1. SDG counts by language (top languages & SDGs).** Heatmap of SDG mention counts by language for the most frequent languages and SDGs in the pilot corpus. *Interpretation:* (i) SDG 17 is dominant across all displayed language communities, consistent with partnership/funding/coordination narratives; (ii) English shows a broader SDG portfolio, including notable visibility for SDG 3 and non-trivial coverage for SDG 11/7/8; (iii) Spanish is more concentrated in SDG 17 with comparatively lower counts for other goals; (iv) lower-frequency languages show sparse counts outside SDG 17, motivating supervised validation and expanded sampling.

**Figure A2. Semantic map (top languages).** Two-dimensional semantic projection of article representations for the most frequent languages (TF–IDF + SVD embeddings with a 2D projection). Each point is an article; colors indicate language. *Interpretation:* the semantic space exhibits partial separation by language (e.g., English forms a dense region while Spanish occupies a distinct extended region), alongside a shared overlap “spine” near the center consistent with common global frames (institutional cooperation and public policy). This motivates quantitative divergence measures (e.g., cluster-distribution Jensen–Shannon divergence) and the use of multilingual sentence embeddings in the full paper to reduce language-specific vectorization artifacts.

### A. Corpus + SDG summary (pilot)
- Retrieved deduplicated records: **56,000**
- SDG-labeled articles: **17,795**
- Article–SDG mentions: **20,782**
- Mean SDGs per SDG-relevant article: **1.17**

### B. SDG mention counts (pilot)
| SDG | Mentions | Share of all SDG mentions |
|---|---:|---:|
| SDG 17 Partnerships for the Goals | 11,722 | 56.4% |
| SDG 3 Good Health and Well-Being | 2,200 | 10.6% |
| SDG 13 Climate Action | 887 | 4.3% |
| Other SDGs (combined) | 5,973 | 28.7% |

### C. SDG 5 monthly punctuations (pilot; monthly aggregation)
| Month index in pilot window | SDG 5 mentions |
|---:|---:|
| Month 1 | 139 |
| Month 3 (latest) | 321 |

### D. SDG mention counts by language (pilot)
| Language | Mentions | Share of all SDG mentions |
|---|---:|---:|
| English | 13,227 | 63.7% |
| Spanish | 3,175 | 15.3% |
| German | 1,230 | 5.9% |
| French | 802 | 3.9% |
| Italian | 543 | 2.6% |
| Indonesian | 337 | 1.6% |
| Portuguese | 306 | 1.5% |
| Romanian | 218 | 1.0% |
| Chinese | 203 | 1.0% |
| Turkish | 120 | 0.6% |
| Other languages (combined) | 621 | 3.0% |

### E. Narrative divergence examples (pilot; JSD over cluster distributions)
| Language A | Language B | JSD (example) |
|---|---|---:|
| English (`en`) | Spanish (`spani`) | 0.635 |
| English (`en`) | German (`germa`) | 0.387 |
| Spanish (`spani`) | Portuguese (`portu`) | 0.477 |

### F. Narrative clusters (pilot; interpretability summary)
Top clusters (by size) from the pilot semantic-framing run are summarized in `data/processed/04_cluster_terms.csv` (clusters below the minimum size threshold are omitted in that file). A compact, paper-friendly excerpt:

| Cluster ID | Articles (n) | Share (approx.) | Example top terms |
|---:|---:|---:|---|
| 9 | 4,742 | 26.7% | new; news; poverty; 2024; united; says |
| 4 | 1,022 | 5.7% | calls; women; funding; solar; education |
| 2 | 1,016 | 5.7% | state; union; address; biden; poverty |
| 5 | 972 | 5.5% | county; india; schools; global; children |
| 23 | 935 | 5.3% | world; united states; country; industry; women |
| 26 | 769 | 4.3% | public health; health care; mental health; emergency |
| 58 | 572 | 3.2% | climate change; fight; heat; impact; farmers |
| 35 | 254 | 1.4% | clean energy; solar; energy transition; green |
| 43 | 239 | 1.3% | drinking water; river; water quality; colorado |

*(These terms are intended as interpretability aids for narrative “frame families”; the full paper should report robustness checks and label clusters cautiously.)*

## References (from the extended abstract)
- Alsuhaibani, M., Gaanoun, K., & Qamar, A. M. (2025). Artificial intelligence-driven insights into Arab media’s sustainable development goals coverage. *PeerJ Computer Science, 11*, e3071. https://doi.org/10.7717/peerj-cs.3071
- Barkemeyer, R., Figge, F., & Holt, D. (2013). Sustainability-related media coverage and socioeconomic development: A regional and North–South perspective. *Environment and Planning C: Government and Policy, 31*(4), 716–740. https://doi.org/10.1068/c11176j
- Blei, D. M., Ng, A. Y., & Jordan, M. I. (2003). Latent Dirichlet Allocation. *Journal of Machine Learning Research, 3*, 993–1022.
- Czvetkó, T., Honti, G., Sebestyén, V., & Abonyi, J. (2021). The intertwining of world news with Sustainable Development Goals: An effective monitoring tool. *Heliyon, 7*(2), e06174. https://doi.org/10.1016/j.heliyon.2021.e06174
- Fankhauser, T., & Clematide, S. (2024). SDG classification using instruction-tuned LLMs. In *Proceedings of the 9th edition of the Swiss Text Analytics Conference* (pp. 148–156). Association for Computational Linguistics.
- GDELT Project. (2015). *The GDELT Global Knowledge Graph (GKG) 2.1 Codebook* [Technical documentation]. https://data.gdeltproject.org/documentation/GDELT-Global_Knowledge_Graph_Codebook-V2.1.pdf
- Hopp, F. R., Fisher, J. T., Cornell, D., Huskey, R., & Weber, R. (2019). iCoRe: The GDELT interface for the advancement of communication research. *Computational Communication Research, 1*(1), 13–44. https://doi.org/10.5117/CCR2019.1.002.HOPP
- Leetaru, K., & Schrodt, P. A. (2013). GDELT: Global data on events, location, and tone, 1979–present. Paper presented at the International Studies Association Annual Convention.
- OSDG, UNDP IICPSD SDG AI Lab, & PPMI. (2022). *OSDG Community Dataset (OSDG-CD) (2022.01)* [Data set]. Zenodo. https://doi.org/10.5281/zenodo.5792547
- Pukelis, L., Bautista-Puig, N., Statulevičiūtė, G., Stančiauskas, V., Dikmener, G., & Akylbekova, D. (2022). OSDG 2.0: A multilingual tool for classifying text data by UN Sustainable Development Goals (SDGs). *arXiv*. https://doi.org/10.48550/arXiv.2211.11252
- Skrynnyk, M., Disassa, G., Krachkov, A., & DeVera, J. (2024). SDGi Corpus: A comprehensive multilingual dataset for text classification by Sustainable Development Goals. In *Proceedings of the 2nd Symposium on NLP for Social Good 2024* (CEUR Workshop Proceedings, Vol. 3764, Paper 3).
- United Nations Development Programme. (2024). *SDGi Corpus* [Data set]. Hugging Face.
