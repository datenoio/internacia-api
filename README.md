# Internacia API

REST API for internacia-db using the internacia-python SDK. This FastAPI application provides HTTP endpoints to interact with internacia-db functionality.

## Features

- RESTful API endpoints for all internacia-python SDK functions
- Automatic OpenAPI documentation
- Request/response validation using Pydantic
- Error handling with consistent error responses
- Health check endpoint
- CORS support

## Project Structure

```
internacia-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialization
│   ├── config.py            # Configuration settings
│   ├── dependencies.py      # Shared dependencies (SDK client)
│   ├── utils.py             # Utility functions (numpy conversion, error handling)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py      # Request models
│   │   └── responses.py     # Response models
│   ├── routers/
│       ├── __init__.py
│       ├── countries.py     # Country-related endpoints
│       ├── blocks.py         # International block endpoints
│       ├── search.py         # Search endpoints
│       └── health.py         # Health check endpoint
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore
└── README.md                # This file
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd internacia-api
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file from the example:
```bash
cp .env.example .env
```

5. Configure environment variables in `.env` (see Configuration section below)

## Configuration

Create a `.env` file in the root directory with the following variables:

```env
# API Settings
API_TITLE=Internacia API
API_VERSION=1.0.0
API_DESCRIPTION=REST API for internacia-db using internacia-python SDK

# Server Settings
HOST=0.0.0.0
PORT=8000
DEBUG=False

# SDK Configuration
# Uncomment and configure based on your SDK requirements:
# INTERNACIA_DB_URL=your_database_url
# INTERNACIA_DB_PATH=/path/to/database
```

## Running the Application

### Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Or using the Python module directly:

```bash
python -m app.main
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check

- `GET /health` - Check API and SDK health status

### Countries

- `GET /countries/{country_code}` - Get country information by code
- `GET /countries` - List all countries

### International Blocks

- `GET /blocks/{block_name}` - Get international block by name
- `GET /blocks` - List all international blocks

### Search

- `GET /search?query={query}&limit={limit}` - Perform fuzzy search
- `POST /search` - Perform advanced search with filters

## Example Requests

### Get Country by Code

```bash
curl http://localhost:8000/countries/US
```

### List All Countries

```bash
curl http://localhost:8000/countries
```

### Get International Block

```bash
curl http://localhost:8000/blocks/eu
```

### Fuzzy Search

```bash
curl "http://localhost:8000/search?query=united&limit=10"
```

### Advanced Search

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "europe",
    "filters": {},
    "limit": 20,
    "offset": 0
  }'
```

### Health Check

```bash
curl http://localhost:8000/health
```

## Response Format

### Success Response

```json
{
  "data": {
    "code": "US",
    "name": "United States",
    ...
  }
}
```

### Error Response

```json
{
  "error": "Country with code 'XX' not found",
  "status_code": 404,
  "path": "/countries/XX"
}
```

## Development

### Adding New Endpoints

1. Create request/response models in `app/models/` if needed
2. Create router endpoint in appropriate file in `app/routers/` that calls SDK methods directly
3. Use utility functions from `app/utils.py` for numpy conversion and error handling
4. Register router in `app/main.py`

**Important**: When returning data from SDK methods, always use `convert_numpy_to_python()` from `app/utils.py` to convert numpy arrays to Python lists. This ensures proper JSON serialization, as DuckDB/pandas may return numpy arrays that FastAPI cannot serialize directly.

### Testing

The API calls SDK methods directly. If the SDK is not available, endpoints will return a 501 (Not Implemented) error.

## Troubleshooting

### Serialization Errors

If you encounter errors like "Unable to serialize unknown type: <class 'numpy.ndarray'>", this has been fixed in the latest version. The API automatically converts numpy arrays to Python lists before serialization. If you're adding new endpoints, make sure to use `convert_numpy_to_python()` from `app/utils.py` when returning SDK data.

## Dependencies

- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI
- **internacia-python**: SDK for interacting with internacia-db
- **Pydantic**: Data validation using Python type annotations
- **python-dotenv**: Load environment variables from .env file

## License

[Add your license here]

## Contributing

[Add contributing guidelines here]

