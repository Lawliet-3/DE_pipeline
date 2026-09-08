CREATE OR REPLACE TABLE marts.daily_trip_metrics AS
SELECT
    CAST(pickup_at AS DATE) AS trip_date,
    count(*) AS trip_count,
    round(avg(trip_distance_miles), 2) AS avg_distance_miles,
    round(avg(duration_minutes), 2) AS avg_duration_minutes,
    round(sum(total_amount), 2) AS gross_revenue,
    round(avg(total_amount), 2) AS avg_ticket
FROM staging.trips
GROUP BY 1
ORDER BY 1;

