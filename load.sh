#!/bin/sh
# Load a Make Data Count data citations CSV release into Parquet and DuckDB.
#
# Usage: ./load.sh 202610
#   reads   data_citations_<release>.csv
#   writes  parquet/data_citations_<release>.parquet
#   loads   mdc.duckdb (table `citations`; re-running replaces that release)
set -eu

release="$1"
csv="data_citations_${release}.csv"
parquet="parquet/data_citations_${release}.parquet"
db="mdc.duckdb"

mkdir -p parquet

# DuckDB's sniffer misses the quote character (quoted fields with commas
# only appear ~95k rows in), so the CSV dialect and types are set explicitly.
duckdb "$db" <<SQL
COPY (
    SELECT *
    FROM read_csv('${csv}',
        header = true, delim = ',', quote = '"', escape = '"',
        columns = {
            'publication_doi': 'VARCHAR',
            'dataset_id':      'VARCHAR',
            'dataset_id_type': 'VARCHAR',
            'repository':      'VARCHAR',
            'citation_type':   'VARCHAR',
            'release':         'INTEGER'
        })
    ORDER BY repository, dataset_id, publication_doi
) TO '${parquet}' (FORMAT parquet, COMPRESSION zstd);

CREATE TABLE IF NOT EXISTS citations (
    publication_doi VARCHAR NOT NULL,
    dataset_id      VARCHAR NOT NULL,
    dataset_id_type VARCHAR NOT NULL,
    repository      VARCHAR NOT NULL,
    citation_type   VARCHAR NOT NULL,
    release         INTEGER NOT NULL
);

BEGIN;
DELETE FROM citations WHERE release = ${release};
INSERT INTO citations SELECT * FROM read_parquet('${parquet}');
COMMIT;

-- Raw rows are kept as published; this view drops exact duplicate rows and
-- records whose publication DOI is the dataset DOI (repository self-links).
CREATE OR REPLACE VIEW citations_clean AS
SELECT DISTINCT *
FROM citations
WHERE publication_doi <> dataset_id;

SELECT release, count(*) AS rows FROM citations GROUP BY release ORDER BY release;
SQL
