# CLI Reference

Complete reference for the MITS Validator command-line interface.

## Installation

```bash
# Install globally
uv add mits-validator

# Or install in a project
uv add mits-validator --dev
```

## Commands

### mits-validate

Main validation command.

#### Usage

```bash
mits-validate [OPTIONS] COMMAND [ARGS]...
```

#### Global Options

- `--version` - Show version and exit
- `--help` - Show help and exit

### validate

Validate a MITS XML feed.

#### Usage

```bash
mits-validate validate [OPTIONS] --file FILE | --url URL
```

#### Options

- `--file FILE` - Path to MITS XML file
- `--url URL` - URL to MITS XML feed
- `--profile PROFILE` - Validation profile to use
- `--json` - Output results in JSON format
- `--help` - Show help and exit

#### Examples

```bash
# Validate a local file
mits-validate validate --file feed.xml

# Validate from URL
mits-validate validate --url https://example.com/feed.xml

# Use a specific profile
mits-validate validate --file feed.xml --profile pms-publisher

# Get JSON output
mits-validate validate --file feed.xml --json
```

#### Exit Codes

- `0` - Validation successful (no errors)
- `1` - Validation failed (errors found)
- `2` - Command line error

### version

Show version information.

#### Usage

```bash
mits-validate version
```

#### Output

```
MITS Validator 0.1.0
```

## Validation Profiles

### Available Profiles

- `default` - All validation levels enabled
- `ils-receiver` - Basic validation for ILS systems
- `pms-publisher` - Full validation for PMS publishers

### Profile Configuration

Profiles are defined in YAML files in `rules/mits-5.0/profiles/`:

```yaml
name: pms-publisher
description: Full validation for PMS publishers
enabled_levels:
  - WellFormed
  - XSD
  - Schematron
  - Semantic
severity_overrides:
  SEMANTIC:ENUM_UNKNOWN: error
intake_limits:
  max_bytes: 10485760  # 10MB
  timeout_seconds: 30
```

## Output Formats

### Human-Readable Output

Default output format with colored output:

```
✓ Validation completed successfully

Summary:
  Valid: true
  Total Findings: 0
  Errors: 0
  Warnings: 0
  Info: 0

Validation Levels:
  Executed: WellFormed
  Available: WellFormed, XSD, Schematron, Semantic

Metadata:
  Request ID: req_123
  Timestamp: 2024-01-01T00:00:00Z
  Engine: mits-validator/0.1.0
```

### JSON Output

Use `--json` flag for machine-readable output:

```json
{
  "summary": {
    "valid": true,
    "total_findings": 0,
    "errors": 0,
    "warnings": 0,
    "info": 0
  },
  "findings": [],
  "validator": {
    "levels_executed": ["WellFormed"],
    "levels_available": ["WellFormed", "XSD", "Schematron", "Semantic"]
  },
  "metadata": {
    "request_id": "req_123",
    "timestamp": "2024-01-01T00:00:00Z",
    "engine": "mits-validator/0.1.0"
  }
}
```

## Error Handling

### Error Output

When validation fails, errors are displayed:

```
✗ Validation failed

Summary:
  Valid: false
  Total Findings: 2
  Errors: 1
  Warnings: 1
  Info: 0

Findings:
  ERROR: WELLFORMED:PARSE_ERROR
    Message: XML parse error: mismatched tag
    Location: Line 5, Column 10
    Rule: internal://WellFormed

  WARNING: XSD:VALIDATION_ERROR
    Message: Element 'Property' is missing required attribute 'PropertyID'
    Location: Line 3, Column 5
    Rule: internal://XSD

Validation Levels:
  Executed: WellFormed, XSD
  Available: WellFormed, XSD, Schematron, Semantic

Metadata:
  Request ID: req_123
  Timestamp: 2024-01-01T00:00:00Z
  Engine: mits-validator/0.1.0
```

### Exit Codes

- `0` - Success (no errors)
- `1` - Validation failed (errors found)
- `2` - Command line error

## Configuration

### Environment Variables

```bash
# Set default profile
export MITS_DEFAULT_PROFILE=pms-publisher

# Set default output format
export MITS_OUTPUT_FORMAT=json

# Set log level
export MITS_LOG_LEVEL=INFO
```

### Configuration File

Create `~/.mits-validator/config.yaml`:

```yaml
default_profile: pms-publisher
output_format: json
log_level: INFO
```

## Examples

### Basic Validation

```bash
# Validate a local file
mits-validate validate --file feed.xml

# Output:
✓ Validation completed successfully
```

### URL Validation

```bash
# Validate from URL
mits-validate validate --url https://example.com/feed.xml

# Output:
✓ Validation completed successfully
```

### Profile Usage

```bash
# Use ILS receiver profile
mits-validate validate --file feed.xml --profile ils-receiver

# Output:
✓ Validation completed successfully
```

### JSON Output

```bash
# Get JSON output
mits-validate validate --file feed.xml --json

# Output:
{
  "summary": {
    "valid": true,
    "total_findings": 0,
    "errors": 0,
    "warnings": 0,
    "info": 0
  },
  "findings": [],
  "validator": {
    "levels_executed": ["WellFormed"],
    "levels_available": ["WellFormed", "XSD", "Schematron", "Semantic"]
  },
  "metadata": {
    "request_id": "req_123",
    "timestamp": "2024-01-01T00:00:00Z",
    "engine": "mits-validator/0.1.0"
  }
}
```

### Error Handling

```bash
# Validate invalid XML
mits-validate validate --file invalid.xml

# Output:
✗ Validation failed

Summary:
  Valid: false
  Total Findings: 1
  Errors: 1
  Warnings: 0
  Info: 0

Findings:
  ERROR: WELLFORMED:PARSE_ERROR
    Message: XML parse error: mismatched tag
    Location: Line 5, Column 10
    Rule: internal://WellFormed

# Exit code: 1
```

## Troubleshooting

### Common Issues

1. **File not found**: Check file path and permissions
2. **Network errors**: Check URL accessibility and network connectivity
3. **Profile not found**: Check profile name and file existence
4. **Permission denied**: Check file permissions

### Debug Mode

```bash
# Enable debug logging
export MITS_DEBUG=true
export MITS_LOG_LEVEL=DEBUG

# Run with verbose output
mits-validate validate --file feed.xml --json
```

### Performance

```bash
# Monitor validation time
time mits-validate validate --file feed.xml

# Profile memory usage
mits-validate validate --file feed.xml --json | jq '.metadata'
```

## Integration

### Shell Scripts

```bash
#!/bin/bash
# Validate and check exit code
if mits-validate validate --file feed.xml; then
  echo "Validation successful"
else
  echo "Validation failed"
  exit 1
fi
```

### CI/CD Pipelines

```yaml
# GitHub Actions example
- name: Validate MITS feed
  run: |
    mits-validate validate --file feed.xml --json > validation.json
    if [ $? -ne 0 ]; then
      echo "Validation failed"
      exit 1
    fi
```

### Automation

```bash
# Batch validation
for file in *.xml; do
  echo "Validating $file..."
  if ! mits-validate validate --file "$file"; then
    echo "Validation failed for $file"
  fi
done
```
