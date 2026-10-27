CREATE DATABASE IF NOT EXISTS shop;

CREATE TABLE IF NOT EXISTS shop.products
(
    product_id UInt32,
    name String,
    category LowCardinality(String),
    base_price Float32
)
ENGINE = MergeTree
ORDER BY product_id;
