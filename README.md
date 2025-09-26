# MITS Validator

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy.readthedocs.io/)

A professional, open-source validator for MITS (Property Marketing / ILS) XML feeds.

## 🚀 Features

### Current (MVP)
- ✅ **FastAPI Web Service** - RESTful API with health checks and validation endpoints
- ✅ **CLI Interface** - Command-line tool for validation tasks
- ✅ **File & URL Validation** - Support for both file uploads and URL-based validation
- ✅ **Size Limits & Security** - Configurable file size limits and safe request handling
- ✅ **Comprehensive Testing** - Full test suite with coverage reporting
- ✅ **Professional Documentation** - Complete docs with MkDocs Material

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
- **API Reference**: [docs/api/](docs/api/)
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