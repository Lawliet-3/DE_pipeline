from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import duckdb

REQUIRED_COLUMNS = {
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "passenger_count",
    "trip_distance",
    "PULocationID",
    "DOLocationID",
    "payment_type",
    "fare_amount",
    "total_amount",
}


@dataclass(frozen=True)
class QualityReport:
    row_count: int
    missing_columns: tuple[str, ...]
    invalid_timestamp_rows: int
    negative_distance_rows: int

    @property
    def passed(self) -> bool:
        return not self.missing_columns and self.row_count > 0


def validate_source(path: Path) -> QualityReport:
    if not path.exists():
        raise FileNotFoundError(f"Source partition not found: {path}")

    connection = duckdb.connect()
    escaped = str(path).replace("'", "''")
    columns = {
        row[0]
        for row in connection.execute(
            f"DESCRIBE SELECT * FROM read_parquet('{escaped}')"
        ).fetchall()
    }
    missing = tuple(sorted(REQUIRED_COLUMNS - columns))
    if missing:
        return QualityReport(0, missing, 0, 0)

    row = connection.execute(
        f"""
        SELECT
            count(*) AS row_count,
            count(*) FILTER (
                WHERE tpep_pickup_datetime IS NULL
                   OR tpep_dropoff_datetime IS NULL
                   OR tpep_dropoff_datetime < tpep_pickup_datetime
            ) AS invalid_timestamp_rows,
            count(*) FILTER (WHERE trip_distance < 0) AS negative_distance_rows
        FROM read_parquet('{escaped}')
        """
    ).fetchone()
    return QualityReport(int(row[0]), missing, int(row[1]), int(row[2]))

