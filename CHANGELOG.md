# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - Unreleased

API for the internacia-db 3.x model. **Breaking:** list responses are paginated.

### Added
- `/blocks/{id}/members` and `/countries/{code}/memberships` (current memberships by default;
  `current=false` for the full history), `current` on `/blocks/member/{code}`.
- `/blocktypes` and `/blocktypes/{id}`.
- Time zones from the data: `/timezones`, `/timezones/{name}`, `/timezones/country/{code}` (they
  were placeholders).
- Retired IDs: `301` to the replacement for merged or renamed block ids and country codes, `410`
  for retired ids, `X-Internacia-Disambiguated` for reused ids.
- `fields=` on country and block routes.
- Typed response models for pages, memberships, block types and catalogs in the OpenAPI schema.
- `Deprecation` and `Link` headers on the deprecated duplicate routes.
- The full country and block lists, block types and catalogs are loaded into memory at startup
  (`PRELOAD_CATALOGS`, on by default): `GET /blocks` and `GET /countries` are 5–6 times faster.
- `docs/self-hosting.md`: reverse proxy (nginx, Caddy, Traefik), forwarded headers, compression,
  rate limiting and sizing.
- `data-bump.yml`: a pull request per new internacia-db release that rebuilds the image with it,
  runs the smoke tests and merges automatically when the contract major is unchanged;
  `release-tag.yml` tags releases from `main`, which publishes the image. Dependabot for Python
  packages, GitHub Actions and Docker.

### Changed
- The smoke tests take their expected counts from the database file, so they pass against
  any 3.x release; CI reads the tested release from the Dockerfile.
- **Breaking:** lists return one page with `total`, `limit` (default 100, max 1000), `offset`
  and `next`; `count` is the number of items on the page.
- Currencies, languages and regions come from the SDK catalogs (internacia-db views) instead of
  scanning every country per request; catalog entries include `country_count`.
- Handlers are synchronous and run in FastAPI's thread pool, so blocking DuckDB queries no longer
  stall the event loop. SDK errors are mapped by one exception handler.

### Deprecated
- `/countries/{code}`, `/countries/alpha2/{code}`, `/countries/alpha3/{code}`,
  `/currencies/{code}/countries`, `/languages/{code}/countries`, `/regions/{id}/countries`.

### Removed
- Unused request models and the empty `app/services` package.


### Added
- Docker image: multi-stage, non-root, read-only-root compatible, `linux/amd64` and
  `linux/arm64`, with an internacia-db release baked in and checked against its SHA-256;
  `compose.yaml`; `.github/workflows/docker.yml` builds and smoke-tests the image on pull
  requests and publishes it to GHCR on `v*` tags as `<api>-db-<db>`, `db-<db>`, `<api>` and
  `latest`.
- `GET /meta`: API, SDK and data versions with the database's build identity, contract version,
  row counts and schema hashes.
- `X-Internacia-Version` / `X-Internacia-Contract` on every response; weak `ETag`,
  `Cache-Control` (`CACHE_MAX_AGE`) and `304 Not Modified` for successful `GET`s.
- `INTERNACIA_DB_VERSION`: startup fails if the database has a different version.

### Changed
- Requires internacia SDK `>=0.4,<0.5` (data contract check at startup, `meta()`); resolved from
  git until 0.4.0 is on PyPI.

## [0.1.0] - Unreleased

First installable release. Targets internacia-db 3.x through the `internacia` SDK 0.3.x.

### Changed
- Packaging moved from `requirements.txt`/`pytest.ini` to `pyproject.toml` with a `uv.lock`;
  runtime and dev dependencies are separated. Requires Python 3.11+.
- The SDK dependency is `internacia>=0.3,<0.4` (the previous `internacia-python` name does not exist
  on PyPI). Until 0.3.0 is published it is resolved from git (see `[tool.uv.sources]`).
- Dependency floors raised above versions with known advisories (`starlette>=1.3.1`,
  `pydantic-settings>=2.14.2`, `python-dotenv>=1.2.2`, `pytest>=9.0.3`).
- API version is `0.1.0`.
- README rewritten: real endpoint list, how to get `internacia.duckdb`, `INTERNACIA_DB_PATH`.
  The never-implemented `POST /search` is no longer documented.

### Added
- `.env.example`.
- CI: ruff, unit tests and a smoke test of every route against the internacia-db 3.0.0 release
  DuckDB (sha256-verified), on Python 3.11 and 3.13, plus server start/refuse-to-start checks.
- `CORS_ORIGINS` setting.

### Fixed
- `/currencies` and `/languages` (and the per-country and per-code variants) returned 500 when a
  country's `currencies`/`languages` column is NULL.
- `/search` option parameters are `include_countries`/`include_blocks`; the tests used other names.
- If the database could not be opened, the API silently served 501 from a cached stub client.
  It now logs the reason and refuses to start.
- `/health` always returned 200. It now queries the database and returns 503 on failure.
- Server errors returned raw exception text (including SQL) and some were reported as 400.
  SDK validation errors are 400, not-found errors 404, everything else a generic, logged 500.
- CORS allowed credentials with a wildcard origin. Credentials are now disabled.

### Removed
- Unused `INTERNACIA_DB_URL` setting.
- The numpy conversion shim; SDK 0.3 returns plain Python types.
- The `StubClient` fallback and the eight copied `_check_client` helpers.
