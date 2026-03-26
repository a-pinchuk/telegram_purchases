FROM python:3.12-slim

WORKDIR /app

# System deps for kaleido (plotly chart export)
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY bot/ bot/
COPY services/ services/
COPY db/ db/
COPY data/ data/

RUN pip install --no-cache-dir .

CMD ["python", "-m", "bot"]
