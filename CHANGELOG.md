# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- Fixed serialization error when returning block and country data containing numpy arrays. DuckDB/pandas was returning numpy arrays that FastAPI couldn't serialize to JSON. Added `convert_numpy_to_python()` utility function that recursively converts numpy arrays to Python lists before serialization. This affects all endpoints returning block or country data.

## [1.0.0] - TBD

### Added
- Initial release of Internacia API
- RESTful API endpoints for all internacia-python SDK functions
- Automatic OpenAPI documentation
- Request/response validation using Pydantic
- Error handling with consistent error responses
- Health check endpoint
- CORS support

