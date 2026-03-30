# ── Stage 1: Build frontend ──
FROM node:20-slim AS frontend-build
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ .
RUN npm run build

# ── Stage 2: Python app ──
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
COPY webapp/ webapp/

# Copy built frontend
COPY --from=frontend-build /build/dist frontend/dist

RUN pip install --no-cache-dir .

VOLUME /app/data_db
ENV DB_PATH=/app/data_db/expenses.db

EXPOSE 8080

CMD ["python", "-m", "bot"]
