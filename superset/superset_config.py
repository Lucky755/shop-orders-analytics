import os

POSTGRES_USER = os.environ.get("POSTGRES_USER", "superset")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "superset")

SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY")
SQLALCHEMY_DATABASE_URI = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@superset_db:5432/{POSTGRES_DB}"
)

REDIS_URL = "redis://redis:6379/1"

CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "superset_",
    "CACHE_REDIS_URL": REDIS_URL,
}

DATA_CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 10,
    "CACHE_KEY_PREFIX": "superset_data_",
    "CACHE_REDIS_URL": REDIS_URL,
}
