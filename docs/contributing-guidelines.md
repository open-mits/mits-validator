# Contributing Guidelines

Thank you for your interest in contributing to the MITS Validator! This document provides guidelines for contributing to the project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Community Guidelines](#community-guidelines)

## Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Git
- Basic understanding of XML validation concepts

### Development Setup

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/your-username/mits-validator.git
   cd mits-validator
   ```

2. **Set up development environment**
   ```bash
   # Install dependencies
   uv sync

   # Install pre-commit hooks
   uv run pre-commit install

   # Run tests to ensure everything works
   uv run pytest
   ```

3. **Create a development branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### 1. Feature Development

```bash
# Start with an issue or create a new one
# Assign yourself to the issue

# Create a feature branch
git checkout -b feature/add-new-validation-rule

# Make your changes
# ... implement feature ...

# Run tests
uv run pytest

# Run linting
uv run ruff check .

# Commit your changes
git add .
git commit -m "feat: add new validation rule for property types"

# Push to your fork
git push origin feature/add-new-validation-rule
```

### 2. Bug Fixes

```bash
# Create a bug fix branch
git checkout -b fix/validation-error-handling

# Fix the bug
# ... implement fix ...

# Add tests for the fix
# ... write tests ...

# Run tests
uv run pytest

# Commit your changes
git commit -m "fix: handle validation errors gracefully"

# Push to your fork
git push origin fix/validation-error-handling
```

### 3. Documentation Updates

```bash
# Create a documentation branch
git checkout -b docs/update-api-examples

# Update documentation
# ... update docs ...

# Preview changes
uv run mkdocs serve

# Commit your changes
git commit -m "docs: update API examples with new features"

# Push to your fork
git push origin docs/update-api-examples
```

## Code Standards

### Python Code Style

We use **Ruff** for linting and formatting. Follow these guidelines:

```python
# Good: Clear, descriptive names
def validate_property_type(property_type: str) -> bool:
    """Validate that property type is in allowed list."""
    allowed_types = {"Apartment", "House", "Townhouse", "Condo"}
    return property_type in allowed_types

# Good: Type hints for all functions
def process_validation_result(
    result: ValidationResult,
    include_warnings: bool = True
) -> ProcessedResult:
    """Process validation result with optional warnings."""
    # Implementation here
    pass

# Good: Comprehensive docstrings
class ValidationEngine:
    """
    Core validation engine for MITS XML feeds.

    This class orchestrates the validation process across multiple
    validation levels (WellFormed, XSD, Schematron, Semantic).

    Attributes:
        levels: List of available validation levels
        profiles: Available validation profiles

    Example:
        >>> engine = ValidationEngine()
        >>> result = engine.validate(content, profile="default")
        >>> print(result.summary.valid)
        True
    """
```

### Code Organization

```
src/mits_validator/
├── __init__.py              # Package initialization
├── api.py                   # FastAPI application
├── cli.py                   # CLI interface
├── validation_engine.py     # Core validation logic
├── models.py                # Data models
├── errors.py                # Error definitions
├── findings.py              # Finding models
├── levels/                  # Validation levels
│   ├── __init__.py
│   ├── xsd.py              # XSD validation
│   ├── schematron.py       # Schematron validation
│   └── semantic.py         # Semantic validation
├── validation/              # Validation utilities
│   ├── __init__.py
│   ├── xsd.py              # XSD validation logic
│   └── schematron.py       # Schematron validation logic
└── profiles.py              # Profile management
```

### Import Organization

```python
# Standard library imports
import os
import time
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

# Third-party imports
import fastapi
import httpx
import lxml
from fastapi import FastAPI, File, Form, HTTPException

# Local imports
from mits_validator import __version__
from mits_validator.findings import create_finding
from mits_validator.models import ValidationRequest
```

### Error Handling

```python
# Good: Specific exception handling
try:
    result = validate_xml(content)
except XMLParseError as e:
    logger.error(f"XML parsing failed: {e}")
    raise ValidationError("Invalid XML format") from e
except ValidationError as e:
    logger.warning(f"Validation failed: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise ValidationError("Internal validation error") from e

# Good: Meaningful error messages
def validate_file_size(file_path: Path, max_size: int) -> None:
    """Validate file size is within limits."""
    file_size = file_path.stat().st_size
    if file_size > max_size:
        raise ValidationError(
            f"File size {file_size} exceeds limit {max_size} bytes"
        )
```

## Testing Guidelines

### Test Structure

```
tests/
├── conftest.py              # Pytest configuration
├── test_validation_engine.py # Core validation tests
├── test_api.py              # API endpoint tests
├── test_cli.py              # CLI tests
├── levels/                  # Validation level tests
│   ├── test_xsd.py
│   ├── test_schematron.py
│   └── test_semantic.py
├── fixtures/                # Test data
│   ├── valid-feed.xml
│   ├── invalid-feed.xml
│   └── large-feed.xml
└── benchmarks/              # Performance tests
    └── test_validation_performance.py
```

### Writing Tests

```python
import pytest
from pathlib import Path
from mits_validator.validation_engine import ValidationEngine
from mits_validator.models import ValidationResult

class TestValidationEngine:
    """Test validation engine functionality."""

    @pytest.fixture
    def validation_engine(self):
        """Create validation engine for testing."""
        return ValidationEngine()

    @pytest.fixture
    def sample_xml(self):
        """Sample XML content for testing."""
        return """<?xml version="1.0" encoding="UTF-8"?>
        <PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0"
                           version="5.0"
                           timestamp="2024-01-01T00:00:00Z">
          <Property>
            <PropertyID>TEST-001</PropertyID>
            <PropertyName>Test Property</PropertyName>
          </Property>
        </PropertyMarketing>"""

    def test_validate_valid_xml(self, validation_engine, sample_xml):
        """Test validation of valid XML."""
        result = validation_engine.validate(
            content=sample_xml.encode('utf-8'),
            content_type="application/xml"
        )

        assert isinstance(result, list)
        assert len(result) > 0
        assert any(r.findings == [] for r in result)

    def test_validate_invalid_xml(self, validation_engine):
        """Test validation of invalid XML."""
        invalid_xml = "<PropertyMarketing><UnclosedTag>"

        result = validation_engine.validate(
            content=invalid_xml.encode('utf-8'),
            content_type="application/xml"
        )

        assert isinstance(result, list)
        assert len(result) > 0
        assert any(len(r.findings) > 0 for r in result)

    @pytest.mark.parametrize("profile", ["default", "performance", "enhanced-validation"])
    def test_validation_profiles(self, validation_engine, sample_xml, profile):
        """Test different validation profiles."""
        result = validation_engine.validate(
            content=sample_xml.encode('utf-8'),
            content_type="application/xml"
        )

        assert isinstance(result, list)
        assert len(result) > 0
```

### Test Coverage

```bash
# Run tests with coverage
uv run pytest --cov=src --cov-report=html --cov-report=term-missing

# Check coverage threshold
uv run pytest --cov=src --cov-fail-under=80
```

### Performance Tests

```python
import time
import pytest
from mits_validator.validation_engine import ValidationEngine

class TestValidationPerformance:
    """Test validation performance."""

    @pytest.fixture
    def validation_engine(self):
        return ValidationEngine()

    def test_validation_performance(self, validation_engine, sample_xml):
        """Test that validation completes within acceptable time."""
        start_time = time.time()

        result = validation_engine.validate(
            content=sample_xml.encode('utf-8'),
            content_type="application/xml"
        )

        duration = time.time() - start_time

        # Should complete within 1 second for small files
        assert duration < 1.0
        assert isinstance(result, list)
```

## Documentation

### Code Documentation

```python
def validate_property_type(property_type: str) -> bool:
    """
    Validate that property type is in the allowed list.

    Args:
        property_type: The property type to validate

    Returns:
        True if property type is valid, False otherwise

    Raises:
        ValueError: If property_type is None or empty

    Example:
        >>> validate_property_type("Apartment")
        True
        >>> validate_property_type("InvalidType")
        False
    """
    if not property_type:
        raise ValueError("Property type cannot be None or empty")

    allowed_types = {"Apartment", "House", "Townhouse", "Condo"}
    return property_type in allowed_types
```

### API Documentation

```python
from fastapi import FastAPI, File, Form, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI(
    title="MITS Validator API",
    description="Professional validator for MITS XML feeds",
    version="0.1.0"
)

@app.post(
    "/v1/validate",
    response_model=ValidationResponse,
    summary="Validate MITS XML feed",
    description="Validate a MITS XML feed against schema and business rules",
    responses={
        200: {"description": "Validation completed successfully"},
        400: {"description": "Invalid request"},
        413: {"description": "File too large"},
        415: {"description": "Unsupported media type"},
        500: {"description": "Internal server error"}
    }
)
async def validate_feed(
    file: UploadFile = File(None, description="XML file to validate"),
    url: str = Form(None, description="URL to validate"),
    profile: str = Form("default", description="Validation profile to use")
) -> JSONResponse:
    """
    Validate a MITS XML feed.

    This endpoint validates MITS XML feeds against schema and business rules.
    You can provide either a file upload or a URL to validate.

    Args:
        file: XML file to validate (multipart/form-data)
        url: URL to validate (application/x-www-form-urlencoded)
        profile: Validation profile to use (default, performance, enhanced-validation)

    Returns:
        Validation result with findings and metadata

    Raises:
        HTTPException: For various error conditions
    """
    # Implementation here
    pass
```

### README Updates

When adding new features, update the README:

```markdown
## New Features

### Enhanced Validation Profiles

The validator now supports enhanced validation profiles for comprehensive checking:

```bash
# Use enhanced validation profile
mits-validate validate --file feed.xml --profile enhanced-validation
```

### Performance Improvements

- **50% faster** validation for large files
- **Reduced memory usage** by 30%
- **Improved error messages** with better context

## Installation

```bash
pip install mits-validator
```

## Quick Start

```bash
# Validate a file
mits-validate validate --file feed.xml

# Validate a URL
mits-validate validate --url https://example.com/feed.xml
```
```

## Pull Request Process

### 1. Before Submitting

- [ ] **Run all tests**: `uv run pytest`
- [ ] **Check linting**: `uv run ruff check .`
- [ ] **Check formatting**: `uv run ruff format .`
- [ ] **Update documentation** if needed
- [ ] **Add tests** for new features
- [ ] **Update changelog** if applicable

### 2. Pull Request Template

```markdown
## Description

Brief description of changes made.

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing

- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Performance tests updated if applicable

## Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
- [ ] Ready for review

## Related Issues

Fixes #(issue number)

## Additional Notes

Any additional information for reviewers.
```

### 3. Review Process

1. **Automated checks** must pass
2. **Code review** by maintainers
3. **Testing** on different environments
4. **Documentation** review
5. **Approval** and merge

## Issue Reporting

### Bug Reports

```markdown
**Bug Description**
A clear description of the bug.

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g. Ubuntu 20.04]
- Python version: [e.g. 3.12.0]
- MITS Validator version: [e.g. 0.1.0]

**Additional Context**
Any other context about the problem.
```

### Feature Requests

```markdown
**Feature Description**
A clear description of the feature you'd like to see.

**Use Case**
Describe the use case for this feature.

**Proposed Solution**
Describe your proposed solution.

**Alternatives**
Describe any alternative solutions you've considered.

**Additional Context**
Any other context about the feature request.
```

## Community Guidelines

### Code of Conduct

- **Be respectful** and inclusive
- **Be constructive** in feedback
- **Be patient** with newcomers
- **Be collaborative** in discussions

### Communication

- **GitHub Issues** for bug reports and feature requests
- **GitHub Discussions** for questions and general discussion
- **Pull Requests** for code contributions
- **Discord/Slack** for real-time chat (if available)

### Recognition

Contributors will be recognized in:
- **CONTRIBUTORS.md** file
- **Release notes** for significant contributions
- **GitHub contributors** page
- **Project documentation**

## Getting Help

### Documentation

- **README.md** - Quick start guide
- **docs/** - Comprehensive documentation
- **API docs** - Interactive API documentation
- **Examples** - Code examples and tutorials

### Support Channels

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - Questions and general discussion
- **Email** - opensource@example.org (for sensitive issues)

### Mentorship

- **Good first issues** - Labeled for newcomers
- **Mentorship program** - Pair with experienced contributors
- **Documentation** - Comprehensive guides and examples

## Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR** - Breaking changes
- **MINOR** - New features (backward compatible)
- **PATCH** - Bug fixes (backward compatible)

### Release Schedule

- **Patch releases** - As needed for bug fixes
- **Minor releases** - Monthly for new features
- **Major releases** - Quarterly for breaking changes

### Release Notes

- **Changelog** - Detailed list of changes
- **Migration guide** - For breaking changes
- **Upgrade guide** - For new features

Thank you for contributing to the MITS Validator! Your contributions help make the project better for everyone.
