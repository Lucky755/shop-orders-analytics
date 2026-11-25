FROM apache/superset:6.1.0

USER root
RUN . /app/.venv/bin/activate && uv pip install --no-cache clickhouse-connect==0.15.1 psycopg2-binary==2.9.9
COPY superset_config.py /app/pythonpath/superset_config.py
USER superset
