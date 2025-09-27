# Branch Protection Rules

This document outlines the recommended branch protection rules for the `open-mits/mits-validator` repository.

## Main Branch Protection

The `main` branch should be protected with the following rules:

### Required Status Checks
- **Pre-commit hooks**: All pre-commit hooks must pass
- **CI/CD Pipeline**: GitHub Actions workflow must pass
- **Test Coverage**: Coverage must be ≥ 80%
- **Linting**: Ruff linting must pass
- **Type Checking**: MyPy type checking must pass (when enabled)

### Branch Protection Settings
- **Require a pull request before merging**: ✅ Enabled
- **Require approvals**: 1 approval required
- **Dismiss stale PR approvals when new commits are pushed**: ✅ Enabled
- **Require review from code owners**: ✅ Enabled (if CODEOWNERS file exists)
- **Restrict pushes that create files**: ✅ Enabled
- **Require status checks to pass before merging**: ✅ Enabled
- **Require branches to be up to date before merging**: ✅ Enabled
- **Require conversation resolution before merging**: ✅ Enabled
- **Require signed commits**: ❌ Optional (not required for this project)
- **Require linear history**: ❌ Optional (allows merge commits)
- **Include administrators**: ✅ Enabled (admins must follow rules)
- **Allow force pushes**: ❌ Disabled
- **Allow deletions**: ❌ Disabled

### Protected File Patterns
- `pyproject.toml` - Project configuration
- `README.md` - Project documentation
- `docs/` - Documentation files
- `.github/` - GitHub configuration
- `src/` - Source code
- `tests/` - Test files

## Development Branches

### Feature Branches
- Pattern: `feature/*`
- No protection rules required
- Should be merged via pull request to `main`

### Hotfix Branches
- Pattern: `hotfix/*`
- No protection rules required
- Should be merged via pull request to `main`

### Release Branches
- Pattern: `release/*`
- No protection rules required
- Should be merged via pull request to `main`

## Implementation

To implement these branch protection rules:

1. Go to the repository settings on GitHub
2. Navigate to "Branches" in the left sidebar
3. Click "Add rule" or "Add branch protection rule"
4. Configure the rules as outlined above
5. Save the configuration

## Code Owners

Create a `CODEOWNERS` file in the repository root to define who should review changes to specific files:

```
# Global owners
* @open-mits/maintainers

# Documentation
docs/ @open-mits/maintainers
README.md @open-mits/maintainers

# Source code
src/ @open-mits/maintainers

# Tests
tests/ @open-mits/maintainers

# Configuration files
pyproject.toml @open-mits/maintainers
.github/ @open-mits/maintainers
.pre-commit-config.yaml @open-mits/maintainers
```

## Status Check Requirements

The following status checks should be required:

1. **pre-commit**: All pre-commit hooks pass
2. **ci**: GitHub Actions workflow passes
3. **coverage**: Test coverage meets threshold
4. **lint**: Code linting passes
5. **type-check**: Type checking passes (when enabled)

## Enforcement

- All rules should be enforced for administrators
- Force pushes should be disabled
- Branch deletions should be disabled
- Linear history is optional but recommended for clean git history
