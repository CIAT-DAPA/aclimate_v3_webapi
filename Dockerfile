FROM python:3.10-slim

# uv binary used to install the locked dependencies
COPY --from=ghcr.io/astral-sh/uv:0.11.32 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_NO_CACHE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PORT=3002

# System dependencies for rasterio, geopandas, psycopg2, and git-based packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN useradd -l -u 10001 appuser

# Install Python dependencies (cacheable layer)
COPY pyproject.toml uv.lock .python-version /app/
RUN uv sync --frozen --no-dev

# Copy application source code
COPY src/ /app/src

WORKDIR /app/src

# Remove build-time dependencies no longer needed at runtime
RUN apt-get remove -y gcc g++ libgdal-dev && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

EXPOSE 3002

HEALTHCHECK --interval=30s --timeout=5s --start-period=45s --retries=5 \
  CMD curl -fsS http://127.0.0.1:${PORT}/health || exit 1

USER appuser

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT} --proxy-headers"]
