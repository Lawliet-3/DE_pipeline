CREATE OR REPLACE TABLE marts.payment_metrics AS
SELECT
    payment_type,
    count(*) AS trip_count,
    round(100.0 * count(*) / sum(count(*)) OVER (), 2) AS trip_share_pct,
    round(sum(total_amount), 2) AS gross_revenue
FROM staging.trips
GROUP BY 1
ORDER BY trip_count DESC, payment_type;

