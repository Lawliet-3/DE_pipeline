from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PipelineConfig:
    root: Path
    year: int
    month: int

    @property
    def raw_dir(self) -> Path:
        return self.root / "data" / "raw" / f"year={self.year}" / f"month={self.month:02d}"

    @property
    def raw_file(self) -> Path:
        return self.raw_dir / f"yellow_tripdata_{self.year}-{self.month:02d}.parquet"

    @property
    def database(self) -> Path:
        return self.root / "data" / "warehouse.duckdb"

    @property
    def export_dir(self) -> Path:
        return self.root / "data" / "exports"

    @property
    def source_url(self) -> str:
        return (
            "https://d37ci6vzurychx.cloudfront.net/trip-data/"
            f"yellow_tripdata_{self.year}-{self.month:02d}.parquet"
        )

