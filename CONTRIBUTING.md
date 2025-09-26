# Contributing to MITS Validator

Thank you for your interest in contributing to MITS Validator! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- Git

### Getting Started

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/your-username/mits-validator.git
   cd mits-validator
   ```

2. **Install dependencies:**
   ```bash
   uv sync -E dev
   ```

3. **Install pre-commit hooks:**
   ```bash
   uv run pre-commit install
   ```

4. **Run tests to verify setup:**
   ```bash
   uv run pytest
   ```

## Development Workflow

### Code Style

We use the following tools to maintain code quality:

- **Ruff**: For linting and formatting
- **MyPy**: For type checking (strict mode)
- **Pre-commit**: For automated checks

All code must pass these checks before submission.

### Running Checks Locally

```bash
# Run all checks
uv run ruff check
uv run ruff format --check
uv run mypy
uv run pytest

# Or run everything at once
uv run pre-commit run --all-files
```

### Testing

- Write tests for new features and bug fixes
- Maintain test coverage above 80%
- Use descriptive test names and docstrings
- Test both success and error cases

## Pull Request Guidelines

### Before Submitting

1. **Ensure all checks pass:**
   - `uv run ruff check`
   - `uv run ruff format --check`
   - `uv run mypy`
   - `uv run pytest`

2. **Update documentation** if needed

3. **Add tests** for new functionality

4. **Update CHANGELOG.md** (if applicable)

### PR Description

Include:
- Clear description of changes
- Reference to related issues
- Screenshots (for UI changes)
- Breaking changes (if any)

### Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for test changes
- `refactor:` for code refactoring
- `chore:` for maintenance tasks

Examples:
```
feat: add XSD validation support
fix: handle malformed XML gracefully
docs: update API documentation
```

## MITS Specification Changes

When modifying validation rules:

1. **Reference official MITS sources** in your PR description
2. **Document the change rationale** clearly
3. **Include test cases** that demonstrate the new behavior
4. **Consider backward compatibility** for existing feeds

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). Please read and follow it in all interactions.

## Getting Help

- **Issues**: Use GitHub issues for bug reports and feature requests
- **Discussions**: Use GitHub discussions for questions and general discussion
- **Security**: Report security issues privately (see [SECURITY.md](SECURITY.md))

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to MITS Validator!
