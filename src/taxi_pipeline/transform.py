from __future__ import annotations

from pathlib import Path

import duckdb

from .config import PipelineConfig


def _sql(name: str) -> str:
    return (Path(__file__).parent / "sql" / name).read_text(encoding="utf-8")


def build_warehouse(config: PipelineConfig) -> dict[str, int]:
    config.database.parent.mkdir(parents=True, exist_ok=True)
    source = str(config.raw_file).replace("'", "''")
    connection = duckdb.connect(str(config.database))
    try:
        connection.execute("CREATE SCHEMA IF NOT EXISTS raw")
        connection.execute("CREATE SCHEMA IF NOT EXISTS staging")
        connection.execute("CREATE SCHEMA IF NOT EXISTS marts")
        connection.execute(_sql("raw_trips.sql").replace("{{ source_path }}", source))
        connection.execute(_sql("stg_trips.sql"))
        connection.execute(_sql("mart_daily_trip_metrics.sql"))
        connection.execute(_sql("mart_payment_metrics.sql"))
        tables = ["raw.trips", "staging.trips", "marts.daily_trip_metrics", "marts.payment_metrics"]
        return {table: connection.execute(f"SELECT count(*) FROM {table}").fetchone()[0] for table in tables}
    finally:
        connection.close()


def export_marts(config: PipelineConfig) -> list[Path]:
    config.export_dir.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect(str(config.database), read_only=True)
    outputs: list[Path] = []
    try:
        for table in ("daily_trip_metrics", "payment_metrics"):
            output = config.export_dir / f"{table}.csv"
            escaped = str(output).replace("'", "''")
            connection.execute(
                f"COPY marts.{table} TO '{escaped}' (HEADER, DELIMITER ',')"
            )
            outputs.append(output)
    finally:
        connection.close()
    return outputs

