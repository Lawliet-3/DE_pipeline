from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import PipelineConfig
from .flow import monthly_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the NYC taxi analytics pipeline")
    parser.add_argument("--year", type=int, default=2024)
    parser.add_argument("--month", type=int, choices=range(1, 13), default=1)
    parser.add_argument("--sample", action="store_true", help="Use deterministic offline sample data")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    result = monthly_pipeline(PipelineConfig(args.root.resolve(), args.year, args.month), args.sample)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()

