# Methods: topic model of *Journal of Cheminformatics*, 2015–2025

This document accompanies **Figure 1** of the editorial *"Cheminformatics as a core driver of molecular discovery and design"* (Martinez-Mayorga & Zdrazil, *J. Cheminform.* 2026). It describes how the figure was produced, the choices that were made, and the limitations the reader should keep in mind when interpreting it.

The full analysis is in [`figure1_topics.py`](src/figure1_topics.py); this document explains the *why* behind it.

---

## 1. Data

**Source.** Bibliographic records for all articles published in the *Journal of Cheminformatics* between 1 January 2015 and 31 December 2025 were retrieved from PubMed on [INSERT DATE] using the query:

```
"Journal of Cheminformatics"[Journal] AND 2015:2025[dp]
```

Records were exported via *Send to → Citation manager* in PubMed's `.nbib` format (the raw file is included in this repository at `data/pubmed-JournalofC-set_1.nbib`).

**Filtering.** Records lacking either a publication year or an English-language abstract were excluded. After filtering, the corpus comprised **1,050 articles**. The per-year breakdown is:

| Year | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Articles | 78 | 70 | 64 | 65 | 78 | 69 | 97 | 83 | 114 | 143 | 189 |

Publication-type breakdown (records may carry more than one type): *Journal Article* (1028), *Review* (24), *Letter* (16), *Editorial* (3), *Published Erratum* (3). We retained all of these; the conclusions are dominated by the journal-article population.

---

## 2. Text preprocessing

For each record, the document fed into the topic model was constructed as:

```
title + " " + title + " " + abstract
```

The title was duplicated to up-weight it relative to the abstract — a common convention in bibliographic text mining, motivated by the observation that titles carry the highest information density per token.

**Vocabulary construction** used a TF-IDF vectoriser (`sklearn.feature_extraction.text.TfidfVectorizer`) with the following parameters:

| Parameter | Value | Rationale |
|---|---|---|
| `ngram_range` | (1, 2) | Capture multi-word terms (*"graph neural network"*, *"chemical space"*, *"named entity"*) |
| `min_df` | 8 | Drop typos and idiosyncratic terms appearing in fewer than 8 articles |
| `max_df` | 0.5 | Drop terms appearing in more than half the corpus (genuinely uninformative) |
| `token_pattern` | `[A-Za-z][A-Za-z\-]{2,}` | Letters and hyphens only, minimum length 3; excludes pure numbers and short tokens |
| `stop_words` | sklearn English + 50-word domain list | See below |

**Domain-specific stopwords.** On top of sklearn's English stopword list, we added approximately 50 terms that are uninformative in this corpus: research boilerplate (*"approach"*, *"method"*, *"results"*, *"propose"*, *"novel"*), open-access licence text (*"open access"*, *"license"*, *"author"*), journal self-references (*"j cheminform"*, *"journal cheminformatics"*), supplementary-material language (*"figure"*, *"table"*, *"supplementary"*), and URL fragments (*"http"*, *"https"*, *"github"*). The complete list is in `figure1_topics.py` (see `EXTRA_STOPWORDS`).

These choices are not data-driven; they encode judgement about what counts as signal in this corpus. The pre-registration mindset for this kind of work is: write down the parameters before looking at clusters, then accept whatever the algorithm produces.

---

## 3. Topic model

We used **non-negative matrix factorisation (NMF)**, implemented in `sklearn.decomposition.NMF`, with the following parameters:

| Parameter | Value |
|---|---|
| `n_components` | 9 |
| `init` | `nndsvd` (Non-negative Double SVD; deterministic given the input) |
| `random_state` | 42 |
| `max_iter` | 600 |

NMF was chosen over LDA (Latent Dirichlet Allocation) for two reasons. First, NMF on TF-IDF features tends to produce more lexically coherent topics on short technical text — exactly the regime we are in. Second, NMF is deterministic given the seed, which makes reproduction straightforward.

**Choice of k = 9.** We did not select k by optimising a quantitative coherence metric (e.g. C_v, U_mass). Instead, we explored values in the range k ∈ {6, …, 12} and chose k = 9 as the smallest value at which each cluster was qualitatively distinct on inspection of its top fourteen terms. At k = 6, *generative models* and *machine learning* merged into a single broad "AI" cluster; at k = 12, the *drug discovery / QSAR / bioactivity* cluster split in ways that did not clearly map onto recognised sub-fields. Readers who prefer a different granularity can re-run with `N_TOPICS` set to another value; the script will print the resulting top-term lists.

This is the most consequential subjective choice in the pipeline. We note it explicitly.

---

## 4. From topics to labels

NMF returns two matrices:

- **W (1050 × 9)** — for each article, the loading on each topic
- **H (9 × |V|)** — for each topic, the loading on each vocabulary term

To label each topic, we sorted its row of H in descending order and inspected the top 14 terms. We then assigned a short human-readable label, written so that any reader of *J. Cheminform.* would map the term list to the same label. The full term lists for the published k = 9 model are:

| # | Label | Top terms |
|---|---|---|
| 0 | Drug discovery, QSAR & bioactivity | drug, discovery, prediction, drug discovery, targets, compounds, drugs, activity, target, qsar, learning, inhibitors, interactions, bioactivity |
| 1 | Infrastructure, databases & mass spectrometry | mass, chemical, software, spectra, structure, spectrometry, mass spectrometry, structures, workflow, analysis, chemistry, tools, database, fragmentation |
| 2 | Protein–ligand binding & docking | binding, protein, docking, protein-ligand, ligand, site, binding site, affinity, binding affinity, interactions, sites, binding sites, protein-ligand binding, proteins |
| 3 | Generative models & molecular design | generative, molecules, design, molecular, novo, generation, space, molecule, smiles, reinforcement, reinforcement learning, optimization, chemical space, drug design |
| 4 | Chemical text mining & entity recognition | recognition, entity, chemical, entity recognition, named entity, named, text, entities, biomedical, chemdner, chemical named, task, patents, biocreative |
| 5 | Reaction prediction & retrosynthesis | reaction, reactions, chemical reaction, chemical, synthesis, retrosynthesis, planning, chemical reactions, synthetic, synthesis planning, routes, prediction, conditions, yield |
| 6 | Virtual screening & similarity | screening, virtual, virtual screening, docking, libraries, similarity, ligand-based, scoring, library, hit, molecules, ligands, fingerprint, compounds |
| 7 | Machine learning & property prediction | molecular, prediction, learning, graph, neural, property, property prediction, networks, deep, neural networks, descriptors, molecular property, machine, representations |
| 8 | Natural products | natural, natural products, products, similarity, nps, fingerprints, database, fingerprint, natural product, product, databases, compounds, molecular, biological |

Two clusters share docking-related vocabulary but differ meaningfully on inspection of the assigned papers: cluster 2 is dominated by structure-based work on binding affinity and binding-site characterisation, while cluster 6 is dominated by ligand-based virtual screening and similarity methods.

---

## 5. Article-to-cluster assignment

Each article was assigned to its **dominant topic** — the topic with the largest entry in that article's row of W. This is a simplification: an article presenting a graph neural network for retrosynthesis genuinely contributes to two themes, but our figure forces it into one. We considered weighting each article fractionally across topics, but the resulting bubbles became visually difficult to read without making the underlying story any clearer.

The per-year, per-topic counts that feed the figure are:

| Topic | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Chemical text mining & NER | 15 | 4 | 0 | 8 | 5 | 4 | 5 | 6 | 1 | 4 | 3 |
| Virtual screening & similarity | 9 | 8 | 4 | 9 | 4 | 1 | 2 | 5 | 7 | 6 | 8 |
| Natural products | 5 | 6 | 5 | 2 | 3 | 8 | 9 | 5 | 7 | 4 | 8 |
| Infrastructure, databases & MS | 28 | 29 | 21 | 17 | 26 | 11 | 17 | 15 | 28 | 26 | 25 |
| Drug discovery, QSAR & bioactivity | 13 | 13 | 8 | 15 | 14 | 11 | 16 | 14 | 15 | 23 | 29 |
| Protein–ligand binding & docking | 5 | 5 | 11 | 3 | 9 | 6 | 14 | 5 | 7 | 19 | 20 |
| Reaction prediction & retrosynthesis | 0 | 1 | 5 | 4 | 1 | 2 | 2 | 7 | 7 | 15 | 16 |
| Generative models & molecular design | 1 | 2 | 5 | 2 | 9 | 13 | 16 | 13 | 19 | 18 | 28 |
| ML & property prediction | 2 | 2 | 5 | 5 | 7 | 13 | 16 | 13 | 23 | 28 | 52 |

These counts are also exported as `jcheminf_topic_counts.csv` for downstream re-use.

---

## 6. Plotting

The figure is a horizontal bubble plot with one row per topic and one column per year. Bubble area is linearly proportional to the article count for that (topic, year) cell. Rows are ordered to place established/legacy topics at the top and AI-era topics at the bottom, so the visual centre of gravity moves diagonally down and to the right as the eye traverses the decade — a deliberate choice to make the temporal shift legible at a glance. Colours encode topic family (grey/teal for foundational, blue for core infrastructure and bioactivity, orange for structure- and reaction-based, red for AI-era).

Output is produced at 200 DPI as both PNG and PDF; the PDF is the version suitable for journal submission.

---

## 7. Limitations and caveats

We list these explicitly because the editorial argues for transparent reporting of method choices, and this figure should be held to the same standard it advocates.

1. **PubMed coverage.** PubMed is comprehensive for biomedicine but may miss articles indexed only in chemistry-focused databases. We re-ran the analysis against a Scopus-derived corpus during development and observed the same qualitative trends; we used PubMed for the final figure because it is freely accessible and the query is fully reproducible.

2. **Abstract-only basis.** Topic modelling is over title and abstract only, not full text. Authors who emphasise different aspects of their work in the abstract than in the body will be classified by the abstract emphasis.

3. **Dominant-topic forcing.** As noted in §5, each article is forced into one topic. Papers that genuinely span two themes are misrepresented; this is a deliberate simplification for visual clarity.

4. **The k = 9 choice is consequential.** Different k values would produce a different figure. We have made our reasoning explicit (§3) so readers can judge it.

5. **Label assignment is interpretive.** The labels in the figure reflect our reading of the top-term lists. A different cheminformatician might prefer different wording; the underlying clusters would be unchanged.

6. **Newer years are still accruing.** PubMed indexing has some lag; the 2025 figures may rise slightly as late-2025 articles are indexed. We retrieved data on [INSERT DATE]; re-running later will produce slightly different counts for 2025.

7. **Statistical significance is not assessed.** This is descriptive bibliometrics, not a hypothesis test. Whether the rise in "Machine learning & property prediction" is "significant" is not the right question; the magnitude (a 26× increase from 2015 to 2025) is the point.

---

## 8. Reproduction

```bash
pip install numpy scikit-learn matplotlib
python figure1_topics.py data/pubmed-JournalofC-set_1.nbib output/figure1.png
```

Software versions used for the published figure:

- Python 3.12.3
- numpy 2.4.4
- scikit-learn 1.8.0
- matplotlib 3.10.8

With `random_state=42` and identical input, the resulting figure is bit-identical across runs on these versions. Substantially different versions of scikit-learn (in particular, anything that changes NMF's `nndsvd` initialisation) may produce different topic indices, in which case the `TOPIC_LABELS` dictionary in `figure1_topics.py` will need to be re-checked against the top-term output the script prints.

---

## 9. Citation

If you use this code or analysis, please cite the editorial:

> Zdrazil B., Martinez-Mayorga K. (2026) Cheminformatics as a core driver of molecular discovery and design. *J. Cheminform.* [in press].

The repository itself is archived at https://doi.org/10.5281/zenodo.21474527.

---

## License

Code: MIT.
Methods description and figures: CC BY 4.0, consistent with the open-access licence of *Journal of Cheminformatics*.
