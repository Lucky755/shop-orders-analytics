import os
import random
import uuid
from datetime import datetime

import clickhouse_connect

CITIES = ["Москва", "Санкт-Петербург", "Владивосток", "Новосибирск", "Екатеринбург", "Хабаровск"]
PAYMENT_METHODS = ["card", "sbp", "cash", "installment"]
BATCH_SIZE = 10

COLUMNS = [
    "event_time", "order_id", "user_id", "product_id", "category",
    "city", "price", "quantity", "payment_method",
]


def make_order(event_time, products):
    product_id, category, base_price = random.choice(products)
    price = round(base_price * random.uniform(0.9, 1.0), 2)
    quantity = 1 if random.random() < 0.8 else random.randint(2, 5)
    city = random.choice(CITIES)
    payment_method = random.choice(PAYMENT_METHODS)
    user_id = random.randint(1, 5000)
    return [
        event_time, uuid.uuid4(), user_id, product_id, category,
        city, price, quantity, payment_method,
    ]


def main():
    client = clickhouse_connect.get_client(
        host=os.environ.get("CLICKHOUSE_HOST", "localhost"),
        username=os.environ.get("CLICKHOUSE_USER", "default"),
        password=os.environ.get("CLICKHOUSE_PASSWORD", ""),
    )
    products = client.query(
        "SELECT product_id, category, base_price FROM shop.products ORDER BY product_id"
    ).result_rows
    print(f"Загружено товаров: {len(products)}")

    now = datetime.now().replace(microsecond=0)
    rows = [make_order(now, products) for _ in range(BATCH_SIZE)]
    client.insert("shop.orders", rows, column_names=COLUMNS)
    print(f"Вставлено заказов: {len(rows)}")


if __name__ == "__main__":
    main()
