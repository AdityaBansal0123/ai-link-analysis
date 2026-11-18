# Multi-stage Dockerfile for high-efficiency, secure deployment
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final Production Image
FROM python:3.11-slim

WORKDIR /app

# Security: Run as non-root user
RUN useradd -m -u 1001 appuser

COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser app /app/app
COPY --chown=appuser:appuser .env.example /app/.env.example

ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=4000 \
    HOST=0.0.0.0

USER appuser

EXPOSE 4000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:4000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "4000"]
