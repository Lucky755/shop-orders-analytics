#!/bin/bash
set -e

superset db upgrade

superset fab create-admin \
    --username "$SUPERSET_ADMIN_USER" \
    --password "$SUPERSET_ADMIN_PASSWORD" \
    --firstname Admin \
    --lastname Shop \
    --email admin@example.com

superset init

superset set-database-uri \
    --database_name ClickHouse \
    --uri "clickhousedb://$CLICKHOUSE_USER:$CLICKHOUSE_PASSWORD@clickhouse:8123/shop"

echo "Инициализация Superset закончена"
