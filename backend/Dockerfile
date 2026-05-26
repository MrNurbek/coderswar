FROM python:3.11-slim

# psycopg2-binary uchun minimal system dep
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python dependencies (cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Source code
COPY . .

RUN mkdir -p staticfiles media

EXPOSE 8000
