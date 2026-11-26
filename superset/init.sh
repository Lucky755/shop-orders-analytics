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

echo "Инициализация Superset закончена"
