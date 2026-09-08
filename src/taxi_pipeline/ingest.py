from __future__ import annotations

import shutil
from pathlib import Path

import duckdb
import requests

from .config import PipelineConfig


def download_month(config: PipelineConfig, *, force: bool = False) -> Path:
    """Download one immutable source partition with an atomic final rename."""
    destination = config.raw_file
    if destination.exists() and not force:
        return destination

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".parquet.part")
    try:
        with requests.get(config.source_url, stream=True, timeout=(10, 120)) as response:
            response.raise_for_status()
            with temporary.open("wb") as output:
                shutil.copyfileobj(response.raw, output)
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    return destination


def generate_sample(config: PipelineConfig, *, rows: int = 12) -> Path:
    """Create deterministic source-shaped data for demos and CI without network access."""
    if rows < 1:
        raise ValueError("rows must be positive")
    config.raw_dir.mkdir(parents=True, exist_ok=True)
    destination = str(config.raw_file).replace("'", "''")
    start = f"{config.year}-{config.month:02d}-01 08:00:00"
    connection = duckdb.connect()
    try:
        connection.execute(
            f"""
            COPY (
                SELECT
                    CAST((i % 2) + 1 AS INTEGER) AS VendorID,
                    TIMESTAMP '{start}' + i * INTERVAL '2 hours' AS tpep_pickup_datetime,
                    TIMESTAMP '{start}' + i * INTERVAL '2 hours'
                        + (8 + i % 25) * INTERVAL '1 minute' AS tpep_dropoff_datetime,
                    CAST(1 + i % 4 AS DOUBLE) AS passenger_count,
                    round(0.8 + i * 0.35, 2) AS trip_distance,
                    CAST(1 AS DOUBLE) AS RatecodeID,
                    'N' AS store_and_fwd_flag,
                    CAST(100 + i % 5 AS INTEGER) AS PULocationID,
                    CAST(120 + i % 7 AS INTEGER) AS DOLocationID,
                    CAST(1 + i % 2 AS INTEGER) AS payment_type,
                    round(6.0 + i * 1.25, 2) AS fare_amount,
                    1.0 AS extra,
                    0.5 AS mta_tax,
                    round(1.0 + i * 0.2, 2) AS tip_amount,
                    0.0 AS tolls_amount,
                    1.0 AS improvement_surcharge,
                    round(9.5 + i * 1.45, 2) AS total_amount,
                    2.5 AS congestion_surcharge,
                    0.0 AS Airport_fee
                FROM range({rows}) source(i)
            ) TO '{destination}' (FORMAT PARQUET)
            """
        )
    finally:
        connection.close()
    return config.raw_file
