from __future__ import annotations

from prefect import flow, task

from .config import PipelineConfig
from .ingest import download_month, generate_sample
from .quality import validate_source
from .transform import build_warehouse, export_marts


@task(retries=2, retry_delay_seconds=5)
def ingest_task(config: PipelineConfig, sample: bool) -> str:
    path = generate_sample(config) if sample else download_month(config)
    return str(path)


@task
def quality_task(config: PipelineConfig) -> dict[str, int]:
    report = validate_source(config.raw_file)
    if not report.passed:
        raise ValueError(f"Source quality checks failed: {report}")
    return {
        "source_rows": report.row_count,
        "invalid_timestamp_rows": report.invalid_timestamp_rows,
        "negative_distance_rows": report.negative_distance_rows,
    }


@task
def transform_task(config: PipelineConfig) -> dict[str, int]:
    return build_warehouse(config)


@task
def export_task(config: PipelineConfig) -> list[str]:
    return [str(path) for path in export_marts(config)]


@flow(name="nyc-taxi-monthly-pipeline", log_prints=True)
def monthly_pipeline(config: PipelineConfig, sample: bool = False) -> dict[str, object]:
    source = ingest_task(config, sample)
    quality = quality_task(config, wait_for=[source])
    table_rows = transform_task(config, wait_for=[quality])
    exports = export_task(config, wait_for=[table_rows])
    result = {"source": source, "quality": quality, "table_rows": table_rows, "exports": exports}
    print(result)
    return result

