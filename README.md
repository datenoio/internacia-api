# Internacia API

Self-hosted, read-only REST API for [internacia-db](https://github.com/datenoio/internacia-db)
(countries and international organizations), built with FastAPI on top of the
[`internacia`](https://github.com/datenoio/internacia-python) Python SDK.

> **Status: pre-release (0.1.0 in progress).** There is no hosted instance and no Docker image yet;
> you run it yourself against a local copy of the database. Response bodies are the raw
> internacia-db rows, so their fields follow the database schema of the file you load.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- An `internacia.duckdb` file from an internacia-db 3.x release

| internacia-api | internacia SDK | internacia-db |
|---|---|---|
| 0.1.x | `>=0.3,<0.4` | 3.x |

> **Temporary:** internacia 0.3.0 is not on PyPI yet. Until it is, `pyproject.toml` resolves the
> SDK from the head branch of [datenoio/internacia-python#3](https://github.com/datenoio/internacia-python/pull/3)
> via `[tool.uv.sources]`. This goes away once 0.3.0 is published.

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

## Run

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
# or
uv run python -m app.main
```

Interactive docs: http://localhost:8000/docs (Swagger UI) and http://localhost:8000/redoc.

## Endpoints

All endpoints are `GET`. Single records are returned as `{"data": {...}}`, lists as
`{"items": [...], "count": n}`, search as `{"results": [...], "count": n, "query": "..."}`, and
errors as `{"error": "...", "status_code": n, "path": "..."}`.

### Service

| Path | Description |
|---|---|
| `/` | API name, version and docs links |
| `/health` | Health status |

### Countries

| Path | Description |
|---|---|
| `/countries?limit=` | All countries (optional `limit`) |
| `/countries/count` | Number of countries |
| `/countries/code/{alpha2}` | By ISO 3166-1 alpha-2 code, e.g. `US` |
| `/countries/iso3/{alpha3}` | By ISO 3166-1 alpha-3 code, e.g. `USA` |
| `/countries/numeric/{code}` | By ISO 3166-1 numeric code, e.g. `840` |
| `/countries/region/{id}` | By World Bank region ID, e.g. `ECS` |
| `/countries/income-level/{id}` | By World Bank income level ID, e.g. `LMC` |
| `/countries/un-members` | UN member states |
| `/countries/independent` | Independent countries |
| `/countries/continent/{name}` | By continent, e.g. `Europe` |
| `/countries/currency/{code}` | Countries using a currency, e.g. `EUR` |
| `/countries/language/{code}` | Countries using a language (ISO 639-3), e.g. `fra` |
| `/countries/{code}`, `/countries/alpha2/{code}`, `/countries/alpha3/{code}` | Legacy aliases of the lookups above |

### International blocks

| Path | Description |
|---|---|
| `/blocks?limit=` | All blocks (optional `limit`; the full list is ~11 MB) |
| `/blocks/count` | Number of blocks |
| `/blocks/{id}` | By ID, e.g. `EU` (case-insensitive) |
| `/blocks/type/{blocktype}` | By block type, e.g. `economic` |
| `/blocks/status/{status}` | By status, e.g. `formal` |
| `/blocks/scope/{scope}` | By geographic scope, e.g. `regional` |
| `/blocks/member/{alpha2}` | Blocks that list a country as a member, e.g. `FR` |
| `/blocks/acronym/{acronym}` | By acronym, e.g. `NATO` |
| `/blocks/tag/{tag}` | By tag, e.g. `trade` |
| `/blocks/topic/{key}` | By topic key, e.g. `economy` |
| `/blocks/founded/{year}` | By founding year, e.g. `1945` |

### Search

| Path | Description |
|---|---|
| `/search?query=&limit=&include_countries=&include_blocks=` | Fuzzy search across countries and blocks |
| `/search/countries?query=&limit=` | Countries only |
| `/search/blocks?query=&limit=` | Blocks only |

### Derived catalogs

| Path | Description |
|---|---|
| `/currencies`, `/currencies/{code}` | Currencies used by countries |
| `/currencies/{code}/countries`, `/currencies/country/{alpha2}` | Countries per currency, currencies per country |
| `/languages`, `/languages/{code}` | Languages used by countries |
| `/languages/{code}/countries`, `/languages/country/{alpha2}` | Countries per language, languages per country |
| `/regions`, `/regions/{id}` | World Bank regions |
| `/regions/{id}/countries`, `/regions/country/{alpha2}` | Countries per region, region per country |
| `/timezones`, `/timezones/country/{alpha2}`, `/timezones/{name}` | Placeholder: always empty / 404 for now |

## Examples

```bash
curl http://localhost:8000/countries/code/US
curl http://localhost:8000/blocks/EU
curl http://localhost:8000/blocks/member/FR
curl "http://localhost:8000/search?query=united&limit=10"
curl "http://localhost:8000/search?query=union&include_countries=false"
```

## Development

```bash
uv sync
uv run pytest
```

## License

[MIT](LICENSE). The internacia-db data is licensed separately (CC BY 4.0); see its repository.
