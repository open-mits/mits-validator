# Contributing

Thank you for your interest in contributing to the MITS Validator! This guide will help you get started.

## Getting Started

### Prerequisites

- Python 3.12 or higher
- `uv` package manager (recommended) or `pip`
- Git

### Development Setup

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/your-username/mits-validator.git
   cd mits-validator
   ```

2. **Install dependencies**
   ```bash
   # Using uv (recommended)
   uv sync -E dev
   
   # Or with pip
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Install pre-commit hooks**
   ```bash
   uv run pre-commit install
   ```

4. **Run tests**
   ```bash
   uv run pytest
   ```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

- Write your code
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 3. Test Your Changes

```bash
# Run all tests
uv run pytest

# Run specific test files
uv run pytest tests/test_validation.py

# Run with coverage
uv run pytest --cov=src/mits_validator

# Run linting
uv run ruff check src/
uv run ruff format src/

# Run type checking
uv run mypy src/
```

### 4. Commit Your Changes

```bash
# Add your changes
git add .

# Commit with a descriptive message
git commit -m "feat: add new validation level"

# Push to your fork
git push origin feature/your-feature-name
```

### 5. Create a Pull Request

- Go to your fork on GitHub
- Click "New Pull Request"
- Fill out the PR template
- Request review from maintainers

## Code Standards

### Python Code Style

We use `ruff` for linting and formatting:

```bash
# Check code style
uv run ruff check src/

# Format code
uv run ruff format src/

# Fix auto-fixable issues
uv run ruff check src/ --fix
```

### Type Hints

All code should include type hints:

```python
from typing import List, Optional

def validate_xml(content: bytes, schema_path: Optional[str] = None) -> ValidationResult:
    """Validate XML content against schema."""
    pass
```

### Documentation

- Document all public functions and classes
- Use Google-style docstrings
- Include examples in docstrings

```python
def validate_xml(content: bytes, schema_path: Optional[str] = None) -> ValidationResult:
    """Validate XML content against schema.
    
    Args:
        content: XML content to validate
        schema_path: Optional path to XSD schema
        
    Returns:
        ValidationResult with findings
        
    Example:
        >>> result = validate_xml(b"<xml>content</xml>")
        >>> print(result.valid)
        True
    """
    pass
```

## Testing

### Test Structure

```
tests/
  test_validation.py          # Core validation tests
  test_api.py                # API endpoint tests
  test_cli.py                # CLI tests
  test_contract.py           # Contract tests
  test_defensive_validation.py  # Defensive validation tests
  test_catalog_loader.py     # Catalog loader tests
  test_profile_system.py    # Profile system tests
  test_url_fetcher.py       # URL fetcher tests
  test_xsd_validation.py    # XSD validation tests
  test_schematron_level.py  # Schematron level tests
  test_semantic_level.py    # Semantic level tests
  test_validation_engine_integration.py  # Integration tests
```

### Writing Tests

```python
def test_validation_success():
    """Test successful validation."""
    # Arrange
    xml_content = b"<MITS><Property><PropertyID>123</PropertyID></Property></MITS>"
    
    # Act
    result = validate_xml(xml_content)
    
    # Assert
    assert result.valid is True
    assert len(result.findings) == 0
```

### Test Categories

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **Contract Tests**: Test API contracts and schemas
- **Performance Tests**: Test validation performance

## Adding New Features

### Validation Levels

1. **Create the level class**
   ```python
   # src/mits_validator/levels/new_level.py
   class NewLevelValidator:
       def validate(self, content: bytes) -> ValidationResult:
           # Implementation
           pass
   ```

2. **Register the level**
   ```python
   # src/mits_validator/validation.py
   def _register_levels(self):
       # Add to registry
       self._levels["NewLevel"] = NewLevelValidator(...)
   ```

3. **Add tests**
   ```python
   # tests/test_new_level.py
   def test_new_level_validation():
       # Test implementation
       pass
   ```

### Error Codes

1. **Add to error catalog**
   ```python
   # src/mits_validator/errors.py
   ERROR_CATALOG = {
       "NEW_LEVEL:ERROR_CODE": ErrorDefinition(
           level=FindingLevel.ERROR,
           title="Error Title",
           description="Error description",
           remediation="How to fix",
           emitted_by="NewLevel"
       )
   }
   ```

2. **Update documentation**
   ```markdown
   # docs/error-codes.md
   | `NEW_LEVEL:ERROR_CODE` | Error | Error Title | Error description |
   ```

### API Endpoints

1. **Add endpoint**
   ```python
   # src/mits_validator/api.py
   @app.post("/v1/new-endpoint")
   async def new_endpoint():
       # Implementation
       pass
   ```

2. **Update OpenAPI**
   ```python
   # Update FastAPI app with new endpoint documentation
   ```

3. **Add tests**
   ```python
   # tests/test_api.py
   def test_new_endpoint():
       # Test implementation
       pass
   ```

## Documentation

### Updating Documentation

1. **README.md** - Update for new features
2. **docs/** - Add new documentation pages
3. **API docs** - Update OpenAPI specifications
4. **Code comments** - Document complex logic

### Documentation Standards

- Use clear, concise language
- Include examples
- Keep documentation up-to-date
- Use consistent formatting

## Release Process

### Version Bumping

We use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Changelog

Update `CHANGELOG.md` with:
- New features
- Bug fixes
- Breaking changes
- Deprecations

## Code Review

### Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are comprehensive
- [ ] Documentation is updated
- [ ] No breaking changes (unless intentional)
- [ ] Performance impact is considered
- [ ] Security implications are reviewed

### Review Process

1. **Self-review**: Review your own changes first
2. **Request review**: Ask for review from maintainers
3. **Address feedback**: Make requested changes
4. **Merge**: Maintainer merges after approval

## Getting Help

### Resources

- **Documentation**: Check existing docs and examples
- **Issues**: Search GitHub issues for similar problems
- **Discussions**: Use GitHub Discussions for questions
- **Code review**: Ask for help in PR comments

### Communication

- Be respectful and constructive
- Provide context for questions
- Use clear, descriptive titles
- Include relevant code examples

## Security

### Security Issues

For security issues, please:
1. **Do not** create public issues
2. Email security@open-mits.org
3. Include detailed information
4. Wait for response before disclosure

### Security Best Practices

- Never commit secrets or credentials
- Use secure coding practices
- Validate all inputs
- Handle errors gracefully

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

## Recognition

Contributors are recognized in:
- CONTRIBUTORS.md
- Release notes
- Project documentation

Thank you for contributing to the MITS Validator! 🎉
