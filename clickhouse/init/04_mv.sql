CREATE TABLE IF NOT EXISTS shop.sales_per_minute
(
    minute DateTime,
    category LowCardinality(String),
    city LowCardinality(String),
    payment_method LowCardinality(String),
    orders_count UInt64,
    items_sold UInt64,
    revenue Float64
)
ENGINE = SummingMergeTree
PARTITION BY toYYYYMMDD(minute)
ORDER BY (minute, category, city, payment_method);

CREATE MATERIALIZED VIEW IF NOT EXISTS shop.sales_per_minute_mv
TO shop.sales_per_minute AS
SELECT
    toStartOfMinute(event_time) AS minute,
    category,
    city,
    payment_method,
    count() AS orders_count,
    sum(quantity) AS items_sold,
    sum(price * quantity) AS revenue
FROM shop.orders
GROUP BY minute, category, city, payment_method;
