# Developer Guide

Welcome to the MITS Validator! This guide will help you get started with developing, contributing to, and integrating with the MITS Validator.

## Table of Contents

- [Quick Start](#quick-start)
- [Development Setup](#development-setup)
- [API Integration](#api-integration)
- [CLI Usage](#cli-usage)
- [Validation Levels](#validation-levels)
- [Error Handling](#error-handling)
- [Performance Tips](#performance-tips)
- [Contributing](#contributing)

## Quick Start

### Using the API

```bash
# Start the server
uv run uvicorn mits_validator.api:app --reload

# Validate a file
curl -X POST -F "file=@your-feed.xml" http://localhost:8000/v1/validate

# Validate a URL
curl -X POST -d "url=https://example.com/feed.xml" http://localhost:8000/v1/validate
```

### Using the CLI

```bash
# Install the package
pip install mits-validator

# Validate a file
mits-validate validate --file feed.xml

# Validate a URL
mits-validate validate --url https://example.com/feed.xml

# Use a specific profile
mits-validate validate --file feed.xml --profile pms-publisher

# Get JSON output
mits-validate validate --file feed.xml --json
```

## Development Setup

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/open-mits/mits-validator.git
cd mits-validator

# Install dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest
```

### Project Structure

```
mits-validator/
├── src/mits_validator/          # Main source code
│   ├── api.py                   # FastAPI application
│   ├── cli.py                   # CLI interface
│   ├── validation_engine.py     # Core validation logic
│   ├── levels/                  # Validation levels
│   │   ├── xsd.py              # XSD validation
│   │   ├── schematron.py       # Schematron validation
│   │   └── semantic.py         # Semantic validation
│   └── models.py               # Data models
├── rules/                      # Validation rules and schemas
│   ├── xsd/                    # XSD schemas
│   ├── schematron/             # Schematron rules
│   └── mits-5.0/               # MITS 5.0 catalogs
├── tests/                      # Test suite
├── docs/                       # Documentation
└── pyproject.toml              # Project configuration
```

## API Integration

### Python Client Example

```python
import httpx
import json

class MITSValidatorClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.Client()

    def validate_file(self, file_path, profile="default"):
        """Validate a local file."""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'profile': profile}
            response = self.client.post(
                f"{self.base_url}/v1/validate",
                files=files,
                data=data
            )
        return response.json()

    def validate_url(self, url, profile="default"):
        """Validate a remote URL."""
        data = {'url': url, 'profile': profile}
        response = self.client.post(
            f"{self.base_url}/v1/validate",
            data=data
        )
        return response.json()

    def health_check(self):
        """Check service health."""
        response = self.client.get(f"{self.base_url}/health")
        return response.json()

# Usage
validator = MITSValidatorClient()

# Validate a file
result = validator.validate_file("feed.xml", profile="pms-publisher")
print(f"Valid: {result['summary']['valid']}")
print(f"Findings: {result['summary']['total_findings']}")

# Validate a URL
result = validator.validate_url("https://example.com/feed.xml")
```

### JavaScript/Node.js Example

```javascript
const FormData = require('form-data');
const fetch = require('node-fetch');

class MITSValidatorClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }

    async validateFile(filePath, profile = 'default') {
        const form = new FormData();
        form.append('file', fs.createReadStream(filePath));
        form.append('profile', profile);

        const response = await fetch(`${this.baseUrl}/v1/validate`, {
            method: 'POST',
            body: form
        });

        return await response.json();
    }

    async validateUrl(url, profile = 'default') {
        const form = new FormData();
        form.append('url', url);
        form.append('profile', profile);

        const response = await fetch(`${this.baseUrl}/v1/validate`, {
            method: 'POST',
            body: form
        });

        return await response.json();
    }

    async healthCheck() {
        const response = await fetch(`${this.baseUrl}/health`);
        return await response.json();
    }
}

// Usage
const validator = new MITSValidatorClient();

validator.validateFile('feed.xml', 'pms-publisher')
    .then(result => {
        console.log(`Valid: ${result.summary.valid}`);
        console.log(`Findings: ${result.summary.total_findings}`);
    })
    .catch(console.error);
```

### cURL Examples

```bash
# Basic file validation
curl -X POST \
  -F "file=@feed.xml" \
  http://localhost:8000/v1/validate

# URL validation with profile
curl -X POST \
  -d "url=https://example.com/feed.xml" \
  -d "profile=pms-publisher" \
  http://localhost:8000/v1/validate

# Validation with specific levels
curl -X POST \
  -F "file=@feed.xml" \
  "http://localhost:8000/v1/validate?levels=WellFormed,XSD"

# Get health status
curl http://localhost:8000/health
```

## CLI Usage

### Basic Commands

```bash
# Show help
mits-validate --help

# Show version
mits-validate version

# Validate a file
mits-validate validate --file feed.xml

# Validate a URL
mits-validate validate --url https://example.com/feed.xml

# Use a specific profile
mits-validate validate --file feed.xml --profile pms-publisher

# Use specific validation mode
mits-validate validate --file feed.xml --mode schematron

# Get JSON output
mits-validate validate --file feed.xml --json
```

### Exit Codes

- `0` - Validation successful (no errors)
- `1` - Validation failed (errors found)
- `2` - Invalid arguments or system error

### Examples

```bash
# Validate with all levels
mits-validate validate --file feed.xml --profile enhanced-validation

# Quick validation (XSD only)
mits-validate validate --file feed.xml --profile performance

# Validate URL with timeout
mits-validate validate --url https://example.com/feed.xml --profile default
```

## Validation Levels

The validator supports four validation levels:

### 1. WellFormed (Level 1)
- **Purpose**: Basic XML structure validation
- **Checks**: XML syntax, well-formedness
- **Performance**: Fastest
- **Use Case**: Quick syntax validation

### 2. XSD (Level 2)
- **Purpose**: Schema conformance validation
- **Checks**: Element structure, data types, required fields
- **Performance**: Fast
- **Use Case**: Structural validation

### 3. Schematron (Level 3)
- **Purpose**: Business rule validation
- **Checks**: Cross-field rules, business logic
- **Performance**: Medium
- **Use Case**: Business rule compliance

### 4. Semantic (Level 4)
- **Purpose**: Semantic validation against catalogs
- **Checks**: Enumeration values, business logic consistency
- **Performance**: Slower (requires catalog loading)
- **Use Case**: Complete validation

## Error Handling

### Response Format

All API responses follow the Result Envelope format:

```json
{
  "summary": {
    "valid": boolean,
    "total_findings": number,
    "errors": number,
    "warnings": number,
    "info": number
  },
  "findings": [
    {
      "level": "error" | "warning" | "info",
      "code": "CATEGORY:SUBCODE",
      "message": "Human-readable message",
      "rule_ref": "internal://RuleName",
      "location": {
        "line": number,
        "column": number,
        "xpath": "string"
      }
    }
  ],
  "validator": {
    "levels_executed": ["string"],
    "levels_available": ["string"]
  },
  "metadata": {
    "request_id": "string",
    "timestamp": "ISO 8601 timestamp",
    "engine": "string"
  }
}
```

### Error Categories

| Category | Description | Examples |
|----------|-------------|----------|
| `INTAKE` | Input validation errors | Missing file, invalid content type |
| `WELLFORMED` | XML parsing errors | Malformed XML, encoding issues |
| `XSD` | Schema validation errors | Invalid structure, missing required fields |
| `SCHEMATRON` | Business rule errors | Invalid business logic, rule violations |
| `SEMANTIC` | Semantic validation errors | Invalid enumeration values, catalog mismatches |
| `NETWORK` | Network operation errors | URL fetch failures, timeouts |
| `ENGINE` | Engine errors | Internal errors, resource loading failures |

### Handling Errors in Code

```python
import httpx

def validate_with_error_handling(file_path):
    try:
        with open(file_path, 'rb') as f:
            response = httpx.post(
                "http://localhost:8000/v1/validate",
                files={"file": f}
            )
            response.raise_for_status()
            result = response.json()

            if result["summary"]["valid"]:
                print("✅ Validation successful!")
            else:
                print(f"❌ Validation failed with {result['summary']['total_findings']} findings")
                for finding in result["findings"]:
                    print(f"  {finding['level'].upper()}: {finding['message']}")

    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e.response.status_code}")
    except httpx.RequestError as e:
        print(f"Request error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
```

## Performance Tips

### API Performance

1. **Use appropriate profiles**:
   - `performance` - Fast validation (WellFormed + XSD only)
   - `default` - Balanced validation
   - `enhanced-validation` - Complete validation

2. **Optimize file sizes**:
   - Compress XML files when possible
   - Use streaming for large files
   - Set appropriate size limits

3. **Cache validation results**:
   - Implement client-side caching
   - Use ETags for unchanged content
   - Consider validation result caching

### CLI Performance

```bash
# Use performance profile for quick validation
mits-validate validate --file feed.xml --profile performance

# Validate only specific levels
mits-validate validate --file feed.xml --mode xsd

# Use JSON output for programmatic processing
mits-validate validate --file feed.xml --json | jq '.summary.valid'
```

### Batch Processing

```python
import asyncio
import aiohttp

async def validate_multiple_files(file_paths):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for file_path in file_paths:
            task = validate_file_async(session, file_path)
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        return results

async def validate_file_async(session, file_path):
    with open(file_path, 'rb') as f:
        data = aiohttp.FormData()
        data.add_field('file', f, filename=file_path)

        async with session.post(
            "http://localhost:8000/v1/validate",
            data=data
        ) as response:
            return await response.json()
```

## Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature`
3. **Make your changes**
4. **Run tests**: `uv run pytest`
5. **Run linting**: `uv run ruff check .`
6. **Commit your changes**: `git commit -m "Add your feature"`
7. **Push to your fork**: `git push origin feature/your-feature`
8. **Create a pull request**

### Code Standards

- **Python 3.12+** with type hints
- **Ruff** for linting and formatting
- **Pytest** for testing
- **Pre-commit hooks** for quality checks
- **80%+ test coverage** required

### Adding New Validation Rules

1. **Create the rule file** in `rules/schematron/` or `rules/xsd/`
2. **Add tests** in `tests/`
3. **Update documentation** in `docs/`
4. **Add error codes** to `src/mits_validator/errors.py`

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_validation_engine.py

# Run with verbose output
uv run pytest -v
```

## Troubleshooting

### Common Issues

1. **"No file or URL provided"**
   - Ensure you're providing either `file` or `url` parameter
   - Check file path is correct and accessible

2. **"Content too large"**
   - File/URL content exceeds size limit (default: 10MB)
   - Use `MAX_UPLOAD_BYTES` environment variable to increase limit

3. **"Unsupported media type"**
   - Content type not allowed (only XML types allowed)
   - Check file is valid XML

4. **"Request timeout"**
   - URL fetch timed out (default: 30 seconds)
   - Use `REQUEST_TIMEOUT` environment variable to increase timeout

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
uv run uvicorn mits_validator.api:app --reload

# CLI debug mode
mits-validate validate --file feed.xml --json | jq '.'
```

### Performance Debugging

```bash
# Profile API performance
curl -w "@curl-format.txt" -X POST -F "file=@feed.xml" http://localhost:8000/v1/validate

# Monitor resource usage
htop
# or
docker stats
```

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/open-mits/mits-validator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/open-mits/mits-validator/discussions)
- **Code**: [GitHub Repository](https://github.com/open-mits/mits-validator)

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.
