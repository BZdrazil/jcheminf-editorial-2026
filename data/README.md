# Raw data

## `pubmed-JournalofC-set_1.nbib`

PubMed citation export covering all *Journal of Cheminformatics* articles
indexed between 1 January 2015 and 31 December 2025.

**Source.** PubMed (https://pubmed.ncbi.nlm.nih.gov)

**Query used:**
```
"Journal of Cheminformatics"[Journal] AND 2015:2025[dp]
```

**Export format.** PubMed Citation Manager format (`.nbib`), retrieved via
*Send to → Citation manager*.

**Retrieval date.** June 9, 2026

**Record count.** 1,050 records with abstracts (after dropping records
without an abstract field or publication year).

## Reproduction

PubMed indexing has some lag, so re-running this query at a later date may
yield slightly more 2025 records. To reproduce the figure exactly, use the
included `.nbib` file rather than re-querying PubMed.

## Terms of use

PubMed data is in the public domain in the United States. International
users should consult the NCBI terms of use:
https://www.ncbi.nlm.nih.gov/home/about/policies/

This includes attribution of the underlying journal publishers (in this
case, *Journal of Cheminformatics* / Springer Nature) for the
bibliographic content.
