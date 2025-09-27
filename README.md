# MITS Validator

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy.readthedocs.io/)

A professional, open-source validator for MITS (Property Marketing / ILS) XML feeds.

## 🚀 Features

### Current (MVP)
- ✅ **FastAPI Web Service** - RESTful API with health checks and validation endpoints
- ✅ **Defensive Input Validation** - Strict content checks, size limits, and error handling
- ✅ **Structured Validation Results** - Machine-readable result envelope with findings
- ✅ **Modular Validation Architecture** - Extensible validation levels (WellFormed, XSD, Schematron, Semantic)
- ✅ **Real MITS 5.0 XSD Validation** - Official MITS 5.0 schema validation with comprehensive error reporting
- ✅ **Schematron Business Rules** - Business logic validation with example rules
- ✅ **Validation Profiles** - Configurable profiles for different use cases (PMS, ILS, Marketplace)
- ✅ **Error Taxonomy** - Centralized error codes with consistent messaging
- ✅ **File & URL Validation** - Support for both file uploads and URL-based validation
- ✅ **Size Limits & Security** - Configurable file size limits and safe request handling
- ✅ **XML Well-Formedness** - Basic XML parsing and structure validation
- ✅ **Comprehensive Testing** - Full test suite with coverage reporting
- ✅ **Professional Documentation** - Complete docs with MkDocs Material

### Performance & Scalability
- ✅ **Async Validation Engine** - Handles large XML files without blocking
- ✅ **Streaming XML Parser** - Memory-optimized processing for very large files
- ✅ **Comprehensive Health Checks** - Filesystem, cache, memory, disk space monitoring
- ✅ **Alerting System** - Configurable thresholds and notifications
- ✅ **Caching Layer** - Redis and in-memory caching for schemas and rules
- ✅ **Rate Limiting** - Request throttling and client management
- ✅ **Metrics Collection** - Prometheus-compatible monitoring
- ✅ **Structured Logging** - Correlation IDs and service information
- ✅ **Container Support** - Docker images with health checks
- ✅ **Production Ready** - Scalable architecture with monitoring

### Roadmap
- 🔄 **XSD Conformance** - Validate XML structure against MITS schemas
- 🔄 **Business Rules** - Implement Schematron rules for business logic validation
- 🔄 **Semantic Consistency** - Ensure data consistency across the feed
- 🔄 **Advanced Reporting** - Detailed validation reports and analytics
- 🔄 **Integration Tools** - SDKs and plugins for popular platforms

## 📦 Installation

### Using uv (Recommended)

```bash
# Install with uv
uv add mits-validator

# Or for development
uv sync -E dev
```

### Using pip

```bash
# Install from PyPI
pip install mits-validator

# Or for development
pip install -e ".[dev]"
```

## 🚀 Quick Start

### Web Service

```bash
# Start the API server
mits-api

# Health check
curl http://localhost:8000/health

# Validate a file
curl -X POST -F "file=@feed.xml" http://localhost:8000/v1/validate

# Validate from URL
curl -X POST -d "url=https://example.com/feed.xml" http://localhost:8000/v1/validate
```

## 🐳 Run with Docker

### Quick Start

```bash
# Pull the latest image
docker pull ghcr.io/open-mits/mits-validator:latest

# Run the container
docker run -p 8000:8000 ghcr.io/open-mits/mits-validator:latest

# Health check
curl http://localhost:8000/health

# Validate a file
curl -X POST -F "file=@feed.xml" http://localhost:8000/v1/validate
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Port to bind the service |
| `MAX_UPLOAD_BYTES` | `10485760` | Maximum file size (10MB) |
| `REQUEST_TIMEOUT` | `30` | Request timeout in seconds |
| `ALLOWED_CONTENT_TYPES` | `application/xml,text/xml,application/octet-stream` | Allowed content types |
| `DEFAULT_PROFILE` | `default` | Default validation profile |
| `LOG_LEVEL` | `INFO` | Logging level |
| `CORS_ORIGINS` | `*` | CORS allowed origins |
| `CORS_METHODS` | `GET,POST,OPTIONS` | CORS allowed methods |
| `CORS_HEADERS` | `*` | CORS allowed headers |

#### Performance & Scalability Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | `None` | Redis connection URL for caching |
| `RATE_LIMIT_MAX_REQUESTS` | `100` | Maximum requests per time window |
| `RATE_LIMIT_TIME_WINDOW` | `60` | Rate limit time window in seconds |
| `THROTTLE_MAX_CONCURRENT` | `10` | Maximum concurrent requests |
| `ASYNC_VALIDATION_MAX_CONCURRENT` | `5` | Maximum concurrent async validations |
| `MEMORY_LIMIT_MB` | `100` | Memory limit for streaming parser |
| `ALERT_THRESHOLD_ERROR_RATE` | `0.1` | Error rate threshold for alerts |
| `ALERT_THRESHOLD_RESPONSE_TIME` | `5.0` | Response time threshold for alerts |

### Example Usage

```bash
# Run with custom configuration
docker run -p 8000:8000 \
  -e MAX_UPLOAD_BYTES=52428800 \
  -e LOG_LEVEL=DEBUG \
  ghcr.io/open-mits/mits-validator:latest

# Run with volume mount for local files
docker run -p 8000:8000 \
  -v $(pwd)/feeds:/app/feeds:ro \
  ghcr.io/open-mits/mits-validator:latest

# Run in background
docker run -d --name mits-validator \
  -p 8000:8000 \
  ghcr.io/open-mits/mits-validator:latest
```

### Development with Docker

```bash
# Build the image
make build

# Run locally
make run

# Run tests in container
make test
```

## 🚀 Performance & Scalability Features

### Async Validation Engine
The validator includes an async validation engine for handling large XML files without blocking:

```python
# Async validation for large files
POST /v1/validate/async
Content-Type: application/json

{
  "url": "https://example.com/large-feed.xml",
  "profile": "enhanced-validation"
}
```

### Streaming XML Parser
Memory-optimized processing for very large XML files:

```python
# Memory-optimized validation
POST /v1/validate/streaming
Content-Type: application/xml

# Large XML content streamed and processed efficiently
```

### Health Monitoring
Comprehensive health checks for production environments:

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health check
curl http://localhost:8000/health/detailed
```

### Metrics & Monitoring
Prometheus-compatible metrics collection:

```bash
# Metrics endpoint
curl http://localhost:8000/metrics
```

### Caching
Redis and in-memory caching for improved performance:

```bash
# Run with Redis caching
docker run -p 8000:8000 \
  -e REDIS_URL=redis://localhost:6379 \
  ghcr.io/open-mits/mits-validator:latest
```

### Rate Limiting
Configurable rate limiting and request throttling:

```bash
# Run with custom rate limits
docker run -p 8000:8000 \
  -e RATE_LIMIT_MAX_REQUESTS=100 \
  -e RATE_LIMIT_TIME_WINDOW=60 \
  ghcr.io/open-mits/mits-validator:latest
```

# Run smoke tests
make smoke

# Clean up
make clean
```

## 📦 Container Images

### Published Images

Container images are published to GitHub Container Registry (GHCR):

- **Latest**: `ghcr.io/open-mits/mits-validator:latest`
- **Versioned**: `ghcr.io/open-mits/mits-validator:v1.0.0`
- **Major.Minor**: `ghcr.io/open-mits/mits-validator:v1.0`

### Pull and Run

```bash
# Pull latest image
docker pull ghcr.io/open-mits/mits-validator:latest

# Run with default settings
docker run -p 8000:8000 ghcr.io/open-mits/mits-validator:latest

# Run with custom port
docker run -p 3000:8000 ghcr.io/open-mits/mits-validator:latest
```

### Versioning Policy

- **`:latest`** - Follows the main branch (latest development)
- **`v*`** - Semantic version tags (e.g., `v1.0.0`, `v1.1.0`)
- **`v*.*`** - Major.minor version tags (e.g., `v1.0`, `v1.1`)

### Public Demo & Limits

For public demos and testing, consider the following limits:

- **Rate Limiting**: Implement rate limiting for production use
- **File Size**: Default 10MB limit (configurable)
- **Timeout**: 30-second request timeout
- **Privacy**: Never upload sensitive production data to public instances

### Operational Notes

- **Resource Requirements**: 512MB RAM, 1 CPU core minimum
- **Security**: Runs as non-root user with read-only filesystem
- **Health Checks**: Built-in health check endpoint
- **Logging**: Structured JSON logging with configurable levels
- **CORS**: Configurable CORS settings for web integration

### CLI Usage

```bash
# Show version
mits-validate version

# Validate a file (future)
mits-validate check feed.xml
```

### API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Result Envelope

The validation API returns a structured, machine-readable result envelope:

```json
{
  "api_version": "1.0",
  "validator": {
    "name": "mits-validator",
    "spec_version": "unversioned",
    "profile": "default",
    "levels_executed": ["WellFormed"]
  },
  "input": {
    "source": "file",
    "filename": "feed.xml",
    "size_bytes": 1234,
    "content_type": "application/xml"
  },
  "summary": {
    "valid": true,
    "errors": 0,
    "warnings": 0,
    "duration_ms": 12
  },
  "findings": [
    {
      "level": "error",
      "code": "WELLFORMED:PARSE_ERROR",
      "message": "XML parsing failed: ...",
      "location": {
        "line": 123,
        "column": 4,
        "xpath": "/Root/Node[2]"
      },
      "rule_ref": "internal://WellFormed"
    }
  ],
  "metadata": {
    "request_id": "uuid-here",
    "timestamp": "2024-01-01T00:00:00Z",
    "engine": {
      "fastapi": "0.115.0",
      "lxml": "5.2.0"
    }
  }
}
```

### Key Fields:
- **`api_version`**: Response schema version (stable)
- **`validator`**: Validator metadata and executed levels
- **`input`**: Information about the validated input
- **`summary`**: High-level validation results
- **`findings`**: Detailed validation findings with location info
- **`metadata`**: Request tracking and engine versions

## Validator Levels & Rules

The validator uses a modular architecture with multiple validation levels:

### Validation Levels
1. **WellFormed** - XML syntax and structure validation
2. **XSD** - Schema conformance validation (when schemas available)
3. **Schematron** - Business rules validation (when rules available)
4. **Semantic** - Cross-field consistency checks (future)

### Validation Profiles
- **default** - All levels enabled, 10MB limit
- **pms** - Property Management System profile, 5MB limit
- **ils** - Internet Listing Service profile, 20MB limit
- **marketplace** - Marketplace profile, 50MB limit

### Error Codes
The validator uses a structured error taxonomy:

| Category | Description | Example Codes |
|----------|-------------|---------------|
| `INTAKE` | Input validation errors | `INTAKE:BOTH_INPUTS`, `INTAKE:TOO_LARGE` |
| `WELLFORMED` | XML parsing errors | `WELLFORMED:PARSE_ERROR` |
| `XSD` | Schema validation errors | `XSD:VALIDATION_ERROR` |
| `SCHEMATRON` | Business rule errors | `SCHEMATRON:RULE_FAILURE` |
| `ENGINE` | System errors | `ENGINE:LEVEL_CRASH` |

See [Error Codes Documentation](docs/error-codes.md) for the complete catalog.

## Catalogs & Versioning

The validator supports versioned MITS catalogs that define charge classes, enumerations, and item specializations. These catalogs provide machine-validated reference data for validation.

### Catalog Structure
```
rules/
  mits-5.0/
    catalogs/
      charge-classes.json          # Charge class definitions
      enums/                       # Enumeration catalogs
        charge-requirement.json
        refundability.json
        payment-frequency.json
        # ... more enums
      item-specializations/        # Item specialization schemas
        parking.json
        storage.json
        pet.json
    schemas/                       # JSON Schemas for validation
      charge-classes.schema.json
      enum.schema.json
      parking.schema.json
      # ... more schemas
```

### Catalog Features
- **Versioned Resources** - Support for multiple MITS versions (5.0, 6.0+)
- **JSON Schema Validation** - All catalogs validated against schemas
- **Unique Code Enforcement** - Duplicate codes detected and reported
- **Machine-Readable** - Structured data for programmatic access
- **Extensible** - Easy to add new catalogs and versions

### Adding/Editing Catalogs
1. **Follow Naming Conventions** - Use UPPER_SNAKE_CASE for codes
2. **Ensure Uniqueness** - All codes must be unique within each catalog
3. **Validate Against Schema** - Run `scripts/validate_catalogs.py`
4. **Test Changes** - Ensure CI passes with your changes

See [Contributing Rules](docs/contributing-rules.md) for detailed guidelines.

## 🔧 Development

### Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/open-mits/mits-validator.git
cd mits-validator

# Install dependencies
uv sync -E dev

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest
```

### Running the Service

```bash
# Development server
uv run mits-api

# Or with uvicorn directly
uv run uvicorn mits_validator.api:app --reload
```

### Code Quality

```bash
# Run all checks
uv run ruff check
uv run ruff format --check
uv run mypy
uv run pytest

# Or run everything at once
uv run pre-commit run --all-files
```

## 📚 Documentation

- **Project Overview**: [docs/index.md](docs/index.md)
- **Architecture**: [docs/architecture.md](docs/architecture.md)
- **API Reference**: [docs/api/](docs/api/)
- **Operational Notes**: [docs/operational-notes.md](docs/operational-notes.md)
- **Roadmap**: [docs/roadmap.md](docs/roadmap.md)
- **Contributing Guide**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Security Policy**: [SECURITY.md](SECURITY.md)
- **Governance**: [GOVERNANCE.md](GOVERNANCE.md)

### Building Documentation

```bash
# Install docs dependencies
uv sync -E docs

# Serve documentation locally
uv run mkdocs serve

# Build documentation
uv run mkdocs build
```

## 🔒 Security

**Important**: MITS feeds may contain sensitive property information.

- **Never upload production data** to public instances
- **Use local deployment** for sensitive feeds
- **Review data** before uploading to any service
- **Consider data retention policies** of your deployment

See our [Security Policy](SECURITY.md) for more information.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Ways to Contribute

- **Code**: Bug fixes, features, improvements
- **Documentation**: Guides, examples, API docs
- **Testing**: Test cases, bug reports
- **Community**: Help others, answer questions

### Development Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and checks
5. Submit a pull request

## 📋 Project Status

| Phase | Status | Description |
|-------|--------|-------------|
| **Foundation** | ✅ Complete | Repository setup, CI/CD, basic service |
| **Core Validation** | 🔄 In Progress | XSD conformance, basic validation |
| **Business Rules** | 📋 Planned | Schematron rules, business logic |
| **Advanced Features** | 📋 Planned | Semantic checks, reporting, integrations |

## 🏗️ Architecture

```
mits-validator/
├── src/mits_validator/     # Main package
│   ├── api.py             # FastAPI application
│   ├── cli.py             # CLI interface
│   └── __main__.py        # Entry point
├── tests/                 # Test suite
├── docs/                  # Documentation
├── .github/               # GitHub workflows and templates
└── pyproject.toml         # Project configuration
```

## 📄 License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/open-mits/mits-validator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/open-mits/mits-validator/discussions)
- **Security**: [Security Policy](SECURITY.md)

## 🏛️ Governance

This project is governed by the [open-mits](https://github.com/open-mits) organization. See our [Governance](GOVERNANCE.md) document for details.

---

**Note**: This is an early-stage project. The API and CLI interfaces may change as we develop the core validation features. We recommend using version pinning in production environments.
