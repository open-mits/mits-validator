# Installation

This guide covers installing the MITS Validator for different use cases.

## Prerequisites

- Python 3.12 or higher
- `uv` package manager (recommended) or `pip`

## Installation Methods

### Using uv (Recommended)

```bash
# Install globally
uv add mits-validator

# Or install in a project
uv add mits-validator --dev
```

### Using pip

```bash
# Install globally
pip install mits-validator

# Or install in a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install mits-validator
```

### From Source

```bash
# Clone the repository
git clone https://github.com/open-mits/mits-validator.git
cd mits-validator

# Install in development mode
uv sync -E dev
# or with pip
pip install -e .
```

## Verification

After installation, verify the installation:

```bash
# Check version
mits-validate version

# Check API server
mits-api --help
```

## Next Steps

- [Quick Start Guide](quickstart.md) - Get started with basic usage
- [Configuration](configuration.md) - Configure the validator for your needs
