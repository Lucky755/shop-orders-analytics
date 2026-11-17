import os
import random
import time
import uuid
from datetime import datetime, timedelta

import clickhouse_connect
import numpy as np

CLICKHOUSE_HOST = os.environ.get("CLICKHOUSE_HOST", "localhost")
CLICKHOUSE_USER = os.environ.get("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.environ.get("CLICKHOUSE_PASSWORD", "")
GEN_SEED = int(os.environ.get("GEN_SEED", "42"))
GEN_INTERVAL = float(os.environ.get("GEN_INTERVAL", "1.5"))
GEN_RATE = float(os.environ.get("GEN_RATE", "8"))

HOUR_FACTORS = [
    0.2, 0.15, 0.1, 0.1, 0.1, 0.15, 0.3, 0.5, 0.7, 0.9, 1.0, 1.1,
    1.3, 1.3, 1.1, 1.0, 1.0, 1.1, 1.3, 1.6, 1.8, 1.7, 1.2, 0.6,
]
WEEKEND_FACTOR = 1.15
TREND_PER_DAY = 0.01
TREND_START = datetime(2026, 11, 1)

CITIES = ["Москва", "Санкт-Петербург", "Владивосток", "Новосибирск", "Екатеринбург", "Хабаровск"]
CITY_WEIGHTS = [40, 20, 12, 11, 10, 7]
PAYMENT_METHODS = ["card", "sbp", "cash", "installment"]

SALE_MINUTES = 10
SALE_FACTOR = 5
SALE_EVERY_SECONDS = 3 * 3600
ANOMALY_CHANCE = 0.00002

COLUMNS = [
    "event_time", "order_id", "user_id", "product_id", "category",
    "city", "price", "quantity", "payment_method",
]


def batch_size(now, sale):
    rate = GEN_RATE * HOUR_FACTORS[now.hour]
    if now.weekday() >= 5:
        rate *= WEEKEND_FACTOR
    rate *= 1 + TREND_PER_DAY * (now - TREND_START).total_seconds() / 86400
    if sale:
        rate *= SALE_FACTOR
    return np.random.poisson(rate)


def choose_payment(amount, sale):
    if amount < 1000:
        weights = [55, 25, 20, 0]
    elif sale:
        weights = [30, 40, 5, 25]
    elif amount >= 15000:
        weights = [50, 25, 3, 22]
    else:
        weights = [60, 25, 10, 5]
    return random.choices(PAYMENT_METHODS, weights)[0]


def make_order(event_time, products, product_weights, sale):
    product_id, category, base_price = random.choices(products, product_weights)[0]
    price = round(base_price * random.uniform(0.9, 1.0), 2)
    quantity = 1 if random.random() < 0.8 else random.randint(2, 5)
    if random.random() < ANOMALY_CHANCE:
        quantity = 500
    if random.random() < ANOMALY_CHANCE:
        price = 0.01
    city = random.choices(CITIES, CITY_WEIGHTS)[0]
    payment_method = choose_payment(price * quantity, sale)
    user_id = random.randint(1, 5000)
    return [
        event_time, uuid.uuid4(), user_id, product_id, category,
        city, price, quantity, payment_method,
    ]


def connect():
    delay = 1
    while True:
        try:
            return clickhouse_connect.get_client(
                host=CLICKHOUSE_HOST, username=CLICKHOUSE_USER, password=CLICKHOUSE_PASSWORD
            )
        except Exception as error:
            print(f"ClickHouse недоступен: {error}")
        print(f"Повтор подключения через {delay} с")
        time.sleep(delay)
        delay = min(delay * 2, 30)


def insert_batch(client, rows):
    delay = 1
    while True:
        try:
            client.insert("shop.orders", rows, column_names=COLUMNS)
            print(f"Вставлено заказов: {len(rows)}")
            return
        except Exception as error:
            print(f"Ошибка вставки: {error}")
        print(f"Повтор вставки через {delay} с")
        time.sleep(delay)
        delay = min(delay * 2, 30)


def main():
    random.seed(GEN_SEED)
    np.random.seed(GEN_SEED)

    client = connect()
    products = client.query(
        "SELECT product_id, category, base_price FROM shop.products ORDER BY product_id"
    ).result_rows
    random.shuffle(products)
    product_weights = [1 / rank for rank in range(1, len(products) + 1)]
    print(f"Загружено товаров: {len(products)}")

    sale_until = datetime.min
    while True:
        now = datetime.now().replace(microsecond=0)
        sale = now < sale_until
        if not sale and random.random() < GEN_INTERVAL / SALE_EVERY_SECONDS:
            sale_until = now + timedelta(minutes=SALE_MINUTES)
            sale = True
            print(f"Распродажа до {sale_until:%H:%M:%S}")
        size = batch_size(now, sale)
        rows = [make_order(now, products, product_weights, sale) for _ in range(size)]
        insert_batch(client, rows)
        time.sleep(GEN_INTERVAL)


if __name__ == "__main__":
    main()
