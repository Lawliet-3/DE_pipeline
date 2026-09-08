CREATE OR REPLACE TABLE staging.trips AS
SELECT
    md5(concat_ws('|', VendorID, tpep_pickup_datetime, PULocationID, DOLocationID)) AS trip_id,
    CAST(tpep_pickup_datetime AS TIMESTAMP) AS pickup_at,
    CAST(tpep_dropoff_datetime AS TIMESTAMP) AS dropoff_at,
    date_diff('minute', tpep_pickup_datetime, tpep_dropoff_datetime) AS duration_minutes,
    CAST(passenger_count AS INTEGER) AS passenger_count,
    CAST(trip_distance AS DOUBLE) AS trip_distance_miles,
    CAST(PULocationID AS INTEGER) AS pickup_location_id,
    CAST(DOLocationID AS INTEGER) AS dropoff_location_id,
    CAST(payment_type AS INTEGER) AS payment_type,
    CAST(fare_amount AS DECIMAL(12, 2)) AS fare_amount,
    CAST(total_amount AS DECIMAL(12, 2)) AS total_amount,
    _ingested_at
FROM raw.trips
WHERE tpep_pickup_datetime IS NOT NULL
  AND tpep_dropoff_datetime >= tpep_pickup_datetime
  AND trip_distance >= 0
  AND total_amount >= 0;

