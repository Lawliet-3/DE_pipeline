.PHONY: install test lint demo run clean

install:
	pip install -e ".[dev]"

test:
	pytest -q

lint:
	ruff check .

demo:
	taxi-pipeline --sample --year 2024 --month 1

run:
	taxi-pipeline --year 2024 --month 1

clean:
	rm -f data/warehouse.duckdb data/exports/*.csv

