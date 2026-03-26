FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY bot/ bot/
COPY services/ services/
COPY db/ db/
COPY data/ data/

RUN pip install --no-cache-dir .

VOLUME /app/data_db
ENV DB_PATH=/app/data_db/expenses.db

CMD ["python", "-m", "bot"]
