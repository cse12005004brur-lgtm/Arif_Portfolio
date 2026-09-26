# Stage 1: Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt-get/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Final runtime stage
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 dos2unix curl && \
    rm -rf /var/lib/apt-get/lists/*

COPY --from=builder /install /usr/local

# Security: Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY . .

# Fix CRLF line-ending issue for Windows and set permissions
RUN find . -type f -exec dos2unix {} + && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

ENV PORT=5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]