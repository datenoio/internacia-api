# syntax=docker/dockerfile:1

# internacia-db release baked into the image. Bump both together (see .github/workflows/ci.yml).
ARG INTERNACIA_DB_VERSION=3.0.0
ARG INTERNACIA_DB_SHA256=02c33d6822432ef60bce19b81e33b180221f6d6504c3e163f0e14f866254e01d
ARG PYTHON_VERSION=3.12

FROM debian:bookworm-slim AS data
ARG INTERNACIA_DB_VERSION
ARG INTERNACIA_DB_SHA256
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL -o /internacia.duckdb \
      "https://github.com/datenoio/internacia-db/releases/download/v${INTERNACIA_DB_VERSION}/internacia.duckdb" \
    && echo "${INTERNACIA_DB_SHA256}  /internacia.duckdb" | sha256sum -c -

FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-bookworm-slim AS build
# git is needed while the SDK is resolved from a git source (see pyproject.toml).
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked --no-dev

FROM python:${PYTHON_VERSION}-slim-bookworm
ARG INTERNACIA_DB_VERSION
LABEL org.opencontainers.image.source="https://github.com/datenoio/internacia-api" \
      org.opencontainers.image.description="Self-hosted REST API for internacia-db" \
      org.opencontainers.image.licenses="MIT" \
      io.dateno.internacia.db-version="${INTERNACIA_DB_VERSION}"
RUN useradd --system --uid 10001 --home-dir /app app
WORKDIR /app
COPY --from=build /app/.venv /app/.venv
COPY app ./app
COPY --from=data /internacia.duckdb /data/internacia.duckdb
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    INTERNACIA_DB_PATH=/data/internacia.duckdb \
    INTERNACIA_DB_VERSION=${INTERNACIA_DB_VERSION}
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD ["python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4).status == 200 else 1)"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
