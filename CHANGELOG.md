# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
