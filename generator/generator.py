import os
import random
import time
import uuid
from datetime import datetime

import clickhouse_connect

CLICKHOUSE_HOST = os.environ.get("CLICKHOUSE_HOST", "localhost")
CLICKHOUSE_USER = os.environ.get("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.environ.get("CLICKHOUSE_PASSWORD", "")
GEN_SEED = int(os.environ.get("GEN_SEED", "42"))
GEN_INTERVAL = float(os.environ.get("GEN_INTERVAL", "1.5"))
GEN_RATE = float(os.environ.get("GEN_RATE", "8"))

CITIES = ["Москва", "Санкт-Петербург", "Владивосток", "Новосибирск", "Екатеринбург", "Хабаровск"]
CITY_WEIGHTS = [40, 20, 12, 11, 10, 7]
PAYMENT_METHODS = ["card", "sbp", "cash", "installment"]

COLUMNS = [
    "event_time", "order_id", "user_id", "product_id", "category",
    "city", "price", "quantity", "payment_method",
]


def make_order(event_time, products, product_weights):
    product_id, category, base_price = random.choices(products, product_weights)[0]
    price = round(base_price * random.uniform(0.9, 1.0), 2)
    quantity = 1 if random.random() < 0.8 else random.randint(2, 5)
    city = random.choices(CITIES, CITY_WEIGHTS)[0]
    payment_method = random.choice(PAYMENT_METHODS)
    user_id = random.randint(1, 5000)
    return [
        event_time, uuid.uuid4(), user_id, product_id, category,
        city, price, quantity, payment_method,
    ]


def main():
    random.seed(GEN_SEED)

    client = clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST, username=CLICKHOUSE_USER, password=CLICKHOUSE_PASSWORD
    )
    products = client.query(
        "SELECT product_id, category, base_price FROM shop.products ORDER BY product_id"
    ).result_rows
    random.shuffle(products)
    product_weights = [1 / rank for rank in range(1, len(products) + 1)]
    print(f"Загружено товаров: {len(products)}")

    while True:
        now = datetime.now().replace(microsecond=0)
        rows = [make_order(now, products, product_weights) for _ in range(round(GEN_RATE))]
        client.insert("shop.orders", rows, column_names=COLUMNS)
        print(f"Вставлено заказов: {len(rows)}")
        time.sleep(GEN_INTERVAL)


if __name__ == "__main__":
    main()
