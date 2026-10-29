CREATE TABLE IF NOT EXISTS shop.orders
(
    event_time DateTime,
    order_id UUID,
    user_id UInt32,
    product_id UInt32,
    category LowCardinality(String),
    city LowCardinality(String),
    price Float32,
    quantity UInt16,
    payment_method LowCardinality(String)
)
ENGINE = MergeTree
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (category, event_time);
