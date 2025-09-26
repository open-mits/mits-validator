# MITS Validator

A professional, open-source validator for MITS (Property Marketing / ILS) XML feeds.

## Overview

MITS Validator provides comprehensive validation for MITS XML feeds through multiple layers:

- **XSD Conformance**: Validates XML structure against MITS schemas
- **Business Rules**: Implements Schematron rules for business logic validation
- **Semantic Consistency**: Ensures data consistency across the feed

## Features

### Current (MVP)
- ✅ FastAPI web service with health checks
- ✅ CLI interface for validation
- ✅ File upload and URL validation endpoints
- ✅ Comprehensive test suite
- ✅ Professional documentation

### Roadmap
- 🔄 XSD conformance validation
- 🔄 Schematron business rules
- 🔄 Semantic consistency checks
- 🔄 Advanced reporting and analytics
- 🔄 Integration tools and SDKs

## Quick Start

### Installation

```bash
# Using uv (recommended)
uv add mits-validator

# Or with pip
pip install mits-validator
```

### Web Service

```bash
# Start the API server
mits-api

# Health check
curl http://localhost:8000/health

# Validate a file
curl -X POST -F "file=@feed.xml" http://localhost:8000/v1/validate
```

### CLI Usage

```bash
# Show version
mits-validate version

# Validate a file (future)
mits-validate check feed.xml
```

## API Endpoints

### Health Check
- **GET** `/health` - Returns service status and version

### Validation
- **POST** `/v1/validate` - Validate MITS XML feed
  - File upload: `multipart/form-data` with `file` field
  - URL validation: `application/x-www-form-urlencoded` with `url` field
  - Size limit: 10MB (configurable)

## Development

### Prerequisites
- Python 3.12+
- uv package manager

### Setup
```bash
git clone https://github.com/open-mits/mits-validator.git
cd mits-validator
uv sync -E dev
uv run pre-commit install
```

### Running Tests
```bash
uv run pytest
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](contributing.md) for details.

### Development Setup
1. Fork the repository
2. Install dependencies: `uv sync -E dev`
3. Install pre-commit hooks: `uv run pre-commit install`
4. Make your changes
5. Run tests: `uv run pytest`
6. Submit a pull request

## Security

**Important**: MITS feeds may contain sensitive property information.

- Never upload production data to public instances
- Use local deployment for sensitive feeds
- Review data before uploading to any service

See our [Security Policy](security.md) for more information.

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/open-mits/mits-validator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/open-mits/mits-validator/discussions)
- **Security**: [Security Policy](security.md)

## Governance

This project is governed by the [open-mits](https://github.com/open-mits) organization. See our [Governance](governance.md) document for details.
