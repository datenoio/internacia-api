# Internacia API

Self-hosted, read-only REST API for [internacia-db](https://github.com/datenoio/internacia-db)
(countries and international organizations), built with FastAPI on top of the
[`internacia`](https://github.com/datenoio/internacia-python) Python SDK.

> **Status: pre-release.** There is no hosted instance; you run it yourself, from source or from
> the Docker image (published to GHCR on release tags). Response bodies are the raw internacia-db
> rows, so their fields follow the database schema of the file you load.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- An `internacia.duckdb` file from an internacia-db 3.x release

| internacia-api | internacia SDK | internacia-db |
|---|---|---|
| 0.2.x | `>=0.4,<0.5` | 3.x (contract 3.x) |
| 0.1.x | `>=0.3,<0.4` | 3.x |

> **Temporary:** internacia 0.4.0 is not on PyPI yet. Until it is, `pyproject.toml` resolves the
> SDK from git, pinned to an internacia-python commit (`[tool.uv.sources]`). This goes away once
> 0.4.0 is published.

## Docker

```bash
docker run -p 8000:8000 ghcr.io/datenoio/internacia-api:latest
# or, from a checkout
docker compose up --build
```

The image bakes in one internacia-db release (`internacia.duckdb`, checked against its SHA-256 at
build time; see `INTERNACIA_DB_VERSION` / `INTERNACIA_DB_SHA256` in the `Dockerfile`), runs as a
non-root user, works with a read-only root filesystem, and has a `/health` health check. Tags:
`<api>-db-<db>` (e.g. `0.2.0-db-3.0.0`), `db-<db>`, `<api>` and `latest`, for `linux/amd64` and
`linux/arm64`.

To serve another database, mount it over `/data/internacia.duckdb` and set
`INTERNACIA_DB_VERSION` to its version (or to an empty string to skip the version check):

```bash
docker run -p 8000:8000 -v "$PWD/internacia.duckdb:/data/internacia.duckdb:ro" \
  -e INTERNACIA_DB_VERSION=3.1.0 ghcr.io/datenoio/internacia-api:latest
```

## Install

```bash
git clone https://github.com/datenoio/internacia-api
cd internacia-api
uv sync            # runtime + dev dependencies from uv.lock
uv sync --no-dev   # runtime only
```

## Get the database

The API does not download data. Fetch `internacia.duckdb` from an
[internacia-db release](https://github.com/datenoio/internacia-db/releases) and verify it:

```bash
mkdir -p data
curl -fL -o data/internacia.duckdb \
  https://github.com/datenoio/internacia-db/releases/download/v3.0.0/internacia.duckdb
echo "02c33d6822432ef60bce19b81e33b180221f6d6504c3e163f0e14f866254e01d  data/internacia.duckdb" \
  | shasum -a 256 -c -
```

Alternatively, `uv run python -c "from internacia import download_database; download_database()"`
downloads the latest release into the SDK cache (`~/.internacia/<version>/`), which the API uses
when `INTERNACIA_DB_PATH` is not set.

## Configure

```bash
cp .env.example .env
```

| Variable | Default | Meaning |
|---|---|---|
| `INTERNACIA_DB_PATH` | unset (SDK cache) | Path to `internacia.duckdb` |
| `HOST` | `0.0.0.0` | Bind address for `python -m app.main` |
| `PORT` | `8000` | Port for `python -m app.main` |
| `DEBUG` | `False` | Auto-reload for `python -m app.main` |
| `CORS_ORIGINS` | `["*"]` | JSON list of allowed CORS origins; credentials are never allowed |
| `INTERNACIA_DB_VERSION` | unset | Expected internacia-db version; startup fails if the database differs |
| `CACHE_MAX_AGE` | `3600` | `Cache-Control: max-age` for successful responses (`0` turns it off) |
| `PRELOAD_CATALOGS` | `true` | Load the full lists and catalogs into memory at startup (about 80 MB) |

The server opens the database at startup and checks its data contract (the internacia SDK
refuses an unsupported contract major). If anything fails (missing file, wrong path, not an
internacia-db file, unexpected version), it logs the reason and exits instead of serving errors.

Every response carries `X-Internacia-Version` and `X-Internacia-Contract`. Successful `GET`
responses also carry a weak `ETag` (derived from the request URL, the API version and the data
build) and `Cache-Control`; send `If-None-Match` to get `304 Not Modified`.

## Run

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
# or
uv run python -m app.main
```

Interactive docs: http://localhost:8000/docs (Swagger UI) and http://localhost:8000/redoc.

For production (reverse proxy, forwarded headers, compression, rate limiting, memory), see
[docs/self-hosting.md](docs/self-hosting.md).

## Endpoints

All endpoints are `GET`. The full, typed list is in the OpenAPI docs (`/docs`).

- **Single records:** `{"data": {...}}`.
- **Lists:** one page: `{"items": [...], "count": n, "total": N, "limit": 100, "offset": 0,
  "next": "<url or null>"}`. `limit` defaults to 100 (max 1000); follow `next` to read the rest.
- **Field selection:** country and block routes accept `fields=code,name,...` to return only
  those top-level fields (useful for `/blocks`, whose full rows are large).
- **Search:** `{"results": [...], "count": n, "query": "..."}`.
- **Errors:** `{"error": "...", "status_code": n, "path": "..."}`. Invalid input gives `400`/`422`,
  unknown IDs `404`; server errors give a generic, logged `500`.
- **Retired IDs:** a merged or renamed block id or country code answers `301` with a `Location` to
  its replacement (e.g. `/blocks/USAN` → `/blocks/UNASUR`, `/countries/code/KV` →
  `/countries/code/XK`); a retired one answers `410`. If an id now names a different organization
  than it used to, `X-Internacia-Disambiguated` gives the id the old one moved to. This needs an
  internacia-db release with alias tables inside `internacia.duckdb` (after 3.0.0).
- **Open enums:** `status`, `geographic_scope`, `scope_category` and similar fields are open
  strings; new data releases may add values.

### Service

| Path | Description |
|---|---|
| `/` | API name, version and docs links |
| `/health` | Runs a query against the database: `200` when it succeeds, `503` otherwise |
| `/meta` | API, SDK and data versions; data build, contract version, row counts and schema hashes |

### Countries

| Path | Description |
|---|---|
| `/countries` | All countries and territories |
| `/countries/count` | Number of countries |
| `/countries/code/{alpha2}` | By ISO 3166-1 alpha-2 code, e.g. `US` |
| `/countries/iso3/{alpha3}` | By ISO 3166-1 alpha-3 code, e.g. `USA` |
| `/countries/numeric/{code}` | By ISO 3166-1 numeric code, e.g. `840` |
| `/countries/{alpha2}/memberships?current=` | Membership edges of a country (`current=true` by default) |
| `/countries/region/{id}` | By World Bank region ID, e.g. `ECS` |
| `/countries/income-level/{id}` | By World Bank income level ID, e.g. `LMC` |
| `/countries/un-members` | UN member states |
| `/countries/independent` | Independent countries |
| `/countries/continent/{name}` | By continent, e.g. `Europe` |
| `/countries/currency/{code}` | Countries using a currency, e.g. `EUR` |
| `/countries/language/{code}` | Countries using a language (ISO 639-3), e.g. `fra` |

### International blocks

| Path | Description |
|---|---|
| `/blocks` | All blocks |
| `/blocks/count` | Number of blocks |
| `/blocks/{id}` | By ID, e.g. `EU` (case-insensitive) |
| `/blocks/{id}/members?current=` | Membership edges of a block (`current=true` by default) |
| `/blocks/member/{alpha2}?current=` | Blocks that list a country; former memberships unless `current=true` |
| `/blocks/type/{blocktype}` | By block type, e.g. `economic` (see `/blocktypes`) |
| `/blocks/status/{status}` | By status, e.g. `formal` |
| `/blocks/scope/{scope}` | By geographic scope, e.g. `regional` |
| `/blocks/acronym/{acronym}` | By acronym, e.g. `NATO` |
| `/blocks/tag/{tag}` | By tag, e.g. `trade` |
| `/blocks/topic/{key}` | By topic key, e.g. `economy` |
| `/blocks/founded/{year}` | By founding year, e.g. `1945` |
| `/blocktypes`, `/blocktypes/{id}` | The block type taxonomy |

"Current" memberships follow the internacia-db data contract: not `former_member`, no `left`
date, and the block is neither historical nor dissolved. All participation statuses (member,
observer, partner, …) are returned; filter `status` for full members.

### Search

| Path | Description |
|---|---|
| `/search?query=&limit=&include_countries=&include_blocks=` | Fuzzy search across countries and blocks |
| `/search/countries?query=&limit=` | Countries only |
| `/search/blocks?query=&limit=` | Blocks only |

### Catalogs

| Path | Description |
|---|---|
| `/currencies`, `/currencies/{code}`, `/currencies/country/{alpha2}` | Currencies, with the number of countries using each |
| `/languages`, `/languages/{code}`, `/languages/country/{alpha2}` | Languages (ISO 639-3) |
| `/regions`, `/regions/{id}`, `/regions/country/{alpha2}` | World Bank regions |
| `/timezones`, `/timezones/{name}`, `/timezones/country/{alpha2}` | IANA time zones, e.g. `/timezones/Europe/Paris` |

### Deprecated routes

These still work and answer with `Deprecation: true` and a `Link` header naming the successor;
they will be removed in a later release.

| Deprecated | Use instead |
|---|---|
| `/countries/{code}`, `/countries/alpha2/{code}` | `/countries/code/{code}` |
| `/countries/alpha3/{code}` | `/countries/iso3/{code}` |
| `/currencies/{code}/countries` | `/countries/currency/{code}` |
| `/languages/{code}/countries` | `/countries/language/{code}` |
| `/regions/{id}/countries` | `/countries/region/{id}` |

## Examples

```bash
curl http://localhost:8000/countries/code/US
curl http://localhost:8000/blocks/EU
curl "http://localhost:8000/blocks/NATO/members"
curl "http://localhost:8000/blocks?fields=id,name&limit=20"
curl "http://localhost:8000/search?query=united&limit=10"
curl "http://localhost:8000/search?query=union&include_countries=false"
```

## Development

```bash
uv sync
uv run ruff check
uv run pytest
```

`pytest` runs the unit tests (SDK mocked) and, when `INTERNACIA_TEST_DB_PATH` is set, a smoke test
that calls every route against a real database:

```bash
uv run python scripts/fetch_test_db.py --version 3.0.0 \
  --sha256 02c33d6822432ef60bce19b81e33b180221f6d6504c3e163f0e14f866254e01d \
  --output .test-data/internacia.duckdb
INTERNACIA_TEST_DB_PATH=.test-data/internacia.duckdb uv run pytest
```

CI (`.github/workflows/ci.yml`) runs ruff, the unit tests and the smoke test on Python 3.11 and
3.13, then checks that the server starts with the database and refuses to start without it. The
tested internacia-db release is pinned there (`TESTED_DB_VERSION`, `TESTED_DB_SHA256`).

## License

[MIT](LICENSE). The internacia-db data is licensed separately (CC BY 4.0); see its repository.
