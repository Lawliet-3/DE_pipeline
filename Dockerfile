FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

ENTRYPOINT ["taxi-pipeline"]
CMD ["--sample", "--year", "2024", "--month", "1"]

