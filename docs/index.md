# MITS Validator

A professional, open-source validator for MITS (Property Marketing / ILS) XML feeds.

## Overview

MITS Validator provides comprehensive validation for MITS XML feeds through multiple layers:

- **WellFormed (Level 1)**: Basic XML structure validation
- **XSD (Level 2)**: Schema conformance validation against MITS schemas
- **Schematron (Level 3)**: Business rules validation using Schematron
- **Semantic (Level 4)**: Semantic consistency checks against catalogs

## Features

### ✅ Current Features
- **Multi-level Validation**: WellFormed, XSD, Schematron, and Semantic validation
- **REST API**: FastAPI web service with comprehensive endpoints
- **CLI Interface**: Command-line tool for validation
- **Validation Profiles**: Configurable validation levels and settings
- **Error Reporting**: Detailed findings with location information
- **Performance Optimized**: Fast validation with configurable limits
- **Comprehensive Testing**: 87%+ test coverage with 153 passing tests
- **Professional Documentation**: Complete guides and examples

### 🚀 Enhanced Developer Experience
- **Interactive API Documentation**: Swagger UI with live examples
- **Comprehensive Guides**: Developer, deployment, and performance guides
- **Code Examples**: Python, JavaScript, cURL, and Postman examples
- **Performance Benchmarks**: Detailed performance metrics and optimization
- **Contributing Guidelines**: Clear guidelines for contributors

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

## Documentation

### 📚 Comprehensive Guides
- **[Developer Guide](developer-guide.md)** - Complete development setup and integration
- **[API Examples](api-examples.md)** - Interactive examples in multiple languages
- **[Performance Benchmarks](performance-benchmarks.md)** - Optimization and scaling guide
- **[Deployment Guide](deployment-guide.md)** - Production deployment strategies
- **[Contributing Guidelines](contributing-guidelines.md)** - How to contribute to the project

### 🔧 API Documentation
- **[REST API Reference](api/rest.md)** - Complete API reference
- **[CLI Documentation](api/cli.md)** - Command-line interface guide
- **[Validation Levels](validation-levels.md)** - Understanding validation levels
- **[Error Codes](error-codes.md)** - Comprehensive error reference

## Development

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager (recommended)

### Quick Setup
```bash
# Clone and setup
git clone https://github.com/open-mits/mits-validator.git
cd mits-validator
uv sync
uv run pre-commit install

# Run tests
uv run pytest

# Start development server
uv run uvicorn mits_validator.api:app --reload
```

### Development Tools
```bash
# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run linting
uv run ruff check .

# Run formatting
uv run ruff format .

# Run all checks
uv run pre-commit run --all-files
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](contributing-guidelines.md) for comprehensive details.

### Quick Start for Contributors
1. **Fork the repository** on GitHub
2. **Clone your fork**: `git clone https://github.com/your-username/mits-validator.git`
3. **Install dependencies**: `uv sync`
4. **Install pre-commit hooks**: `uv run pre-commit install`
5. **Create a feature branch**: `git checkout -b feature/your-feature`
6. **Make your changes** and add tests
7. **Run tests**: `uv run pytest`
8. **Commit and push**: `git commit -m "feat: add your feature"`
9. **Create a pull request** on GitHub

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
