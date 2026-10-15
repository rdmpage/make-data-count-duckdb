# Make Data Count data citations in DuckDB

Exploratory analysis of the Make Data Count (MDC) data citations dump,
release `202610` (`data_citations_202610.csv`, 650 MB, 8,712,962 rows).

## Setup

```sh
./load.sh 202610        # CSV -> parquet/data_citations_202610.parquet + mdc.duckdb
duckdb -readonly mdc.duckdb
```

- Table `citations`: the raw rows, columns `publication_doi, dataset_id,
  dataset_id_type, repository, citation_type, release`. Re-running `load.sh`
  for a release replaces it, so future releases can sit alongside.
- View `citations_clean`: drops 5 exact duplicate rows and 6,743 rows where
  `publication_doi = dataset_id` (repository self-links); 8,706,219 rows.
- CSV gotcha: DuckDB's sniffer misses the quote character (first quoted field
  with a comma is ~95k rows in), so `load.sh` sets the dialect explicitly.
- Open the database with `-readonly` if more than one session needs it; a
  read-write session locks the file. The Parquet file can always be queried
  directly.
- Digital Science also host this release on BigQuery
  (`ds-make-data-count.public.data_citations_202610`); not used here.

## Outputs

| File | What |
|---|---|
| `dataset_citation_frequency.csv` | Number of datasets cited exactly *k* times (total, DOI, accession) |
| `dataset_citation_frequency.png` | Log-log plot of the above (`uv run plot_frequency.py`) |
| `dataset_citation_bins.png` | Binned bar chart of the above (`uv run plot_bins.py`) |
| `once_cited_sample.csv` | 24 once-cited datasets, 4 per (DOI/accession × Primary/Secondary/Unclassified), for manual checking |
| `once_cited_secondary_repos_sample.csv` | 20 once-cited datasets, 4 each from UniProt, RefSeq, Ensembl, Pfam, Cellosaurus |

The sample CSVs have empty `my_judgement` and `notes` columns. Not yet checked.

A "dataset" below is a (repository, dataset_id) pair; "times cited" is the
number of distinct citing publications, from `citations_clean`.

## Findings

### Overview

- 2,073,909 publications, 4,492,391 datasets, 2,531 repositories.
- 84% of rows are accessions (7.33M), 16% DOIs (1.39M).
- Citation type: Secondary 6.21M, Primary 1.82M, Unclassified 684K.
- GenBank/ENA/DDBJ alone is 4.04M rows; then PDB 909K, UniProt 740K,
  RefSeq 608K, GEO 536K. Zenodo (126K) is the largest DOI repository.
- Publication DOIs carry no metadata (no year, journal, title). Joining
  OpenAlex/Crossref would be needed for time or journal analyses.
- Blog posts are not covered: no Rogue Scholar DOIs (`10.59350/`) at all.

### How often datasets are cited

| Times cited | Datasets | % |
|---|---|---|
| 1 | 3,425,427 | 76.2 |
| 2 | 534,939 | 11.9 |
| 3 | 193,772 | 4.3 |
| 4–5 | 156,920 | 3.5 |
| 6–10 | 109,591 | 2.4 |
| 11–20 | 45,176 | 1.0 |
| 21–50 | 19,491 | 0.4 |
| 51–100 | 4,499 | 0.1 |
| 101–1,000 | 2,539 | 0.06 |
| 1,001+ | 37 | 0.001 |

- Median 1, mean 1.94, 99th percentile 14, maximum 6,351 (GEO `GPL570`).
- DOI and accession datasets have the same distribution: mean 1.94 for both,
  75.6% vs 76.4% cited once, and roughly straight log-log lines with the same
  exponent (α ≈ 2.03, quick discrete MLE assuming x_min = 1; no proper
  power-law fit or comparison with alternatives such as lognormal).

### Datasets cited only once, by citation type

| Type | Datasets | % | DOI | Accession |
|---|---|---|---|---|
| Secondary | 1,492,952 | 43.6 | 980 | 1,491,972 |
| Primary | 1,427,121 | 41.7 | 340,719 | 1,086,402 |
| Unclassified | 505,350 | 14.8 | 195,286 | 310,064 |

- Once-cited DOI datasets are almost never Secondary (980 of ~537K).
- Once-cited datasets account for about four-fifths of all Primary rows:
  most "Primary" citations are a paper linked to its own data that is never
  cited again.

### Citation type is assigned per repository

- 15 repositories (≥100 rows) are 100% Secondary: UniProt, RefSeq, Ensembl,
  Pfam, Cellosaurus, Human Protein Atlas, InterPro, Reactome, ChEMBL, Rfam,
  RNAcentral, UniParc, adoe.repo, IntAct, datacite.services.
- Mostly curated/derived databases, so Secondary is a reasonable default,
  but RefSeq includes records derived from authors' own GenBank submissions.
- DOI repositories that host supplementary files are mostly Primary:
  figshare.ars 80%, Dryad 81%, Mendeley Data 75%. All 105,587 figshare.ars
  rows are `10.6084/m9.figshare.*` DOIs; top citing publishers Nature,
  Elsevier, Royal Society. These look like paper → own supplement links,
  not reuse.

Citation patterns in the always-Secondary repositories differ from the rest
(all others: mean 1.81, 77.4% cited once):

| Repository | Datasets | Mean | % once | Max |
|---|---|---|---|---|
| RefSeq | 236,487 | 2.57 | 66.7 | 2,484 |
| UniProt | 223,235 | 3.31 | 66.6 | 3,710 |
| Ensembl | 80,177 | 1.42 | 80.5 | 57 |
| Pfam | 9,282 | 6.08 | 36.9 | 597 |
| Cellosaurus | 6,104 | 7.63 | 52.4 | 2,785 |

Top identifiers are reference material: SARS-CoV-2 genome, qPCR
housekeeping genes (GAPDH `NM_002046`, `NM_017008.4`; β-actin `NM_007393`),
protein kinase domain `PF00069`, common cell lines, TP53/GAPDH in Ensembl.

### Data quality problems

Follow-up to [The Data Citation Corpus revisited](https://doi.org/10.59350/wvwva-v7125)
(iPhylo, 8 Oct 2024, corpus v2):

- Compound codes still matched as GenBank/ENA/DDBJ accessions: PD173074
  (1,353 publications), CGS21680 (1,277), GW501516 (1,093), LY341495 (963),
  LY294002 (963, down from 9,983 in v2), PD184352 (932), S63845 (916).
  C34554, C10337, C34557 (1,100–1,400 each) are suspicious but unchecked.
- A549 no longer appears as a sequence accession (Cellosaurus `CVCL_0023`
  is, correctly, a cell line).
- Separately spelled "Figshare" and "figshare" from v2 are gone; repositories
  now use DataCite client IDs.
- Non-data "datasets": GEO platform `GPL570` (Affymetrix U133 Plus 2.0 array)
  is the most-cited dataset (6,350 Secondary, 1 Primary from
  `10.1186/1471-2164-10-197`, which cannot be right for a commercial array).
- UniProt `P36930`, `P36931`, `P36935`, `P36934` (1,675–3,710 publications
  each) are consecutive accessions; looks like a matching artefact. Unchecked.
- Version suffixes not normalised: `NC_045512.2` (2,484) and `NC_045512`
  (1,154) are counted as separate datasets.
- Many DOI "datasets" appear to be journal articles registered with DataCite
  by journal-hosting repositories, e.g. `10.17169/fqs-1.2.1089` (935),
  `10.17179/excli2017-480` (848), and most DOI examples in
  `once_cited_sample.csv`. Based on identifiers only; not resolved.
- Some publications cite huge numbers of accessions, e.g.
  `10.1016/j.ygeno.2006.06.011` → 21,102; several top ones are fungal
  taxonomy (*Studies in Mycology*, *Journal of Fungi*, *Mycology*).

## Possible next steps

- Check the two sample CSVs by hand to measure how often Primary/Secondary
  labels are right.
- Quantify false-positive accessions: GenBank/ENA/DDBJ IDs cited far more
  than typical sequence records, classified as compound codes vs real IDs.
- Resolve the `P36930` group against UniProt.
- Measure what share of DOI "datasets" are articles (DataCite resource type).
- Measure version-suffix splitting across RefSeq and GenBank.
- Biodiversity subset (Pensoft, *Studies in Mycology*, GBIF, PANGAEA) joined
  against the local biodiversity data lake.
