CREATE OR REPLACE TABLE raw.trips AS
SELECT *, current_timestamp AS _ingested_at
FROM read_parquet('{{ source_path }}');

