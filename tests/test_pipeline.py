from pathlib import Path

import duckdb

from taxi_pipeline.config import PipelineConfig
from taxi_pipeline.ingest import generate_sample
from taxi_pipeline.quality import validate_source
from taxi_pipeline.transform import build_warehouse, export_marts


def test_pipeline_end_to_end(tmp_path: Path) -> None:
    config = PipelineConfig(tmp_path, 2024, 1)
    source = generate_sample(config, rows=12)

    report = validate_source(source)
    assert report.passed
    assert report.row_count == 12
    assert report.invalid_timestamp_rows == 0

    counts = build_warehouse(config)
    assert counts["raw.trips"] == 12
    assert counts["staging.trips"] == 12
    assert counts["marts.daily_trip_metrics"] == 2
    assert counts["marts.payment_metrics"] == 2

    exports = export_marts(config)
    assert all(path.exists() for path in exports)

    with duckdb.connect(str(config.database), read_only=True) as connection:
        row = connection.execute(
            "SELECT sum(trip_count), sum(gross_revenue) FROM marts.daily_trip_metrics"
        ).fetchone()
    assert row[0] == 12
    assert float(row[1]) == 209.7


def test_sample_generation_rejects_empty_dataset(tmp_path: Path) -> None:
    config = PipelineConfig(tmp_path, 2024, 1)
    try:
        generate_sample(config, rows=0)
    except ValueError as error:
        assert str(error) == "rows must be positive"
    else:
        raise AssertionError("Expected ValueError")
