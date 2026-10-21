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

### Removed
- Unused `INTERNACIA_DB_URL` setting.
