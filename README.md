# jcheminf-editorial-2026

Code and data underlying **Figure 1** of the editorial:

> Zdrazil, B. & Martinez-Mayorga, K. (2026)
> *Cheminformatics as a core driver of molecular discovery and design.*
> *Journal of Cheminformatics* [in press].

[![License: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](LICENSE)
[![License: CC BY 4.0](https://img.shields.io/badge/Docs%20%26%20Figures-CC%20BY%204.0-lightgrey.svg)](LICENSE-docs)

---

## What is in this repository

A topic-evolution analysis of all *Journal of Cheminformatics* articles published between 2015 and 2025 (n = 1,050), and the script that produces Figure 1 of the editorial from it.

| Path | Description |
|---|---|
| `src/figure1_topics.py` | Self-contained script that parses the PubMed `.nbib` export, fits an NMF topic model, and produces the figure. |
| `data/pubmed-JournalofC-set_1.nbib` | Raw PubMed export, used as input to the analysis. |
| `output/figure1.png` / `figure1.pdf` | Published figure (raster and vector). |
| `output/jcheminf_topic_counts.csv` | Per-year, per-topic article counts behind the figure. |
| `METHODS.md` | Extended methods description, including all parameter choices and limitations. |

---

## Quick start

```bash
git clone https://github.com/<your-username>/jcheminf-editorial-2026.git
cd jcheminf-editorial-2026
pip install -r requirements.txt
python src/figure1_topics.py data/pubmed-JournalofC-set_1.nbib output/figure1.png
```

With `random_state=42` and the package versions pinned in `requirements.txt`, the script reproduces Figure 1 bit-for-bit.

---

## How the figure was made — in one paragraph

Bibliographic records for all *Journal of Cheminformatics* articles published 2015–2025 were retrieved from PubMed using the query `"Journal of Cheminformatics"[Journal] AND 2015:2025[dp]`. Titles (weighted 2×) and abstracts were combined into a TF-IDF representation (1–2-grams, `min_df=8`, `max_df=0.5`). Non-negative matrix factorisation with k = 9 components clustered the corpus into nine topics; each article was assigned to its dominant topic. Cluster labels were assigned post-hoc by inspection of the fourteen most characteristic terms per cluster. The full rationale, the complete top-term lists, and the per-year-per-topic counts are in [`METHODS.md`](METHODS.md).

---

## Reproducing or extending the analysis

The pipeline is deliberately small and modular. Common modifications:

- **Different number of topics.** Edit `N_TOPICS` in `src/figure1_topics.py`. The script will print the top terms for each cluster — use those to update the `TOPIC_LABELS` dictionary.
- **Different time window.** Edit `YEAR_RANGE` and re-export from PubMed with the matching query.
- **Different journal.** Re-export the `.nbib` file from any PubMed-indexed journal; the rest of the pipeline is journal-agnostic.

If you reproduce or extend this analysis, we would be glad to hear about it (issues and pull requests welcome).

---

## Citation

If you use this code or analysis, please cite the editorial:

```bibtex
@article{Zdrazil2026,
  author  = {Zdrazil, Barbara and Martinez-Mayorga, Karina },
  title   = {Cheminformatics as a core driver of molecular discovery and design},
  journal = {Journal of Cheminformatics},
  year    = {2026},
  note    = {In press}
}
```

A `CITATION.cff` file is provided for tools that consume it.

This repository itself is archived at [Zenodo DOI — to be added on deposit].

---

## License

- **Code** (`src/`, `requirements.txt`): [MIT](LICENSE)
- **Documentation, figures, and data products** (`METHODS.md`, `README.md`, `output/`): [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE-docs)
- **Raw PubMed export** (`data/`): see `data/README.md` for provenance; redistribution is permitted under PubMed's terms of use.

---

## Authors

- **Barbara Zdrazil** — European Molecular Biology Laboratory, European Bioinformatics Institute (EMBL-EBI), Hinxton, UK ([ORCID 0000-0001-9395-1515](https://orcid.org/0000-0001-9395-1515))
- **Karina Martinez-Mayorga** — Institute of Chemistry, National Autonomous University of Mexico (UNAM), Campus Mérida, Yucatán, Mexico

