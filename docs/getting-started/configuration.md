# Configuration

Configure the MITS Validator for your specific needs.

## Environment Variables

### API Server Configuration

```bash
# Server settings
export MITS_API_HOST=0.0.0.0
export MITS_API_PORT=8000
export MITS_API_WORKERS=1

# Validation settings
export MITS_MAX_FILE_SIZE=10485760  # 10MB in bytes
export MITS_TIMEOUT_SECONDS=30
export MITS_ALLOWED_CONTENT_TYPES="application/xml,text/xml,application/octet-stream"

# URL fetching settings
export URL_FETCH_TIMEOUT_SECONDS=5
export URL_FETCH_MAX_BYTES=10485760  # 10MB
```

### Development Settings

```bash
# Enable debug mode
export MITS_DEBUG=true

# Set log level
export MITS_LOG_LEVEL=INFO

# Enable profiling
export MITS_PROFILE=true
```

## Validation Profiles

### Default Profile

The default profile runs all validation levels:

```yaml
# rules/mits-5.0/profiles/default.yaml
name: default
description: Default validation profile with all levels enabled
enabled_levels:
  - WellFormed
  - XSD
  - Schematron
  - Semantic
severity_overrides: {}
intake_limits:
  max_bytes: 10485760  # 10MB
  allowed_content_types:
    - application/xml
    - text/xml
    - application/octet-stream
  timeout_seconds: 30
```

### ILS Receiver Profile

Optimized for ILS systems receiving MITS feeds:

```yaml
# rules/mits-5.0/profiles/ils-receiver.yaml
name: ils-receiver
description: Basic validation for ILS systems
enabled_levels:
  - WellFormed
  - XSD
severity_overrides:
  XSD:VALIDATION_ERROR: warning  # Downgrade XSD errors to warnings
intake_limits:
  max_bytes: 5242880  # 5MB
  timeout_seconds: 15
```

### PMS Publisher Profile

Full validation for PMS systems publishing MITS feeds:

```yaml
# rules/mits-5.0/profiles/pms-publisher.yaml
name: pms-publisher
description: Full validation for PMS publishers
enabled_levels:
  - WellFormed
  - XSD
  - Schematron
  - Semantic
severity_overrides:
  SEMANTIC:ENUM_UNKNOWN: error  # Upgrade semantic errors
intake_limits:
  max_bytes: 10485760  # 10MB
  timeout_seconds: 30
```

## Custom Profiles

### Creating a Custom Profile

1. Create a new YAML file in `rules/mits-5.0/profiles/`
2. Define the profile configuration
3. Use the profile with `--profile` flag

```yaml
# rules/mits-5.0/profiles/custom.yaml
name: custom
description: Custom validation profile
enabled_levels:
  - WellFormed
  - XSD
severity_overrides:
  XSD:VALIDATION_ERROR: info  # Downgrade to info level
intake_limits:
  max_bytes: 2097152  # 2MB
  timeout_seconds: 10
```

### Using Custom Profiles

```bash
# CLI usage
mits-validate validate --file feed.xml --profile custom

# API usage
curl -X POST -F "file=@feed.xml" -H "X-Profile: custom" http://localhost:8000/v1/validate
```

## Catalog Configuration

### MITS 5.0 Catalogs

The validator uses versioned catalogs for reference data:

```
rules/mits-5.0/
  catalogs/
    charge-classes.json          # Charge class definitions
    enums/                       # Enumeration catalogs
      charge-requirement.json
      refundability.json
    item-specializations/        # Item specialization schemas
      parking.json
      storage.json
      pet.json
  schemas/                       # JSON Schemas for validation
    charge-classes.schema.json
    enum.schema.json
    parking.schema.json
```

### Adding Custom Catalogs

1. Create catalog files in the appropriate directory
2. Ensure they validate against their schemas
3. Run validation: `uv run python scripts/validate_catalogs.py`

## Error Handling

### Error Codes

The validator uses standardized error codes:

- `INTAKE:*` - Input validation errors
- `WELLFORMED:*` - XML parsing errors
- `XSD:*` - Schema validation errors
- `SCHEMATRON:*` - Business rule errors
- `SEMANTIC:*` - Semantic validation errors
- `NETWORK:*` - Network-related errors
- `ENGINE:*` - Engine-level errors

### Severity Levels

- **ERROR** - Critical issues that must be fixed
- **WARNING** - Issues that should be addressed
- **INFO** - Informational messages

## Performance Tuning

### Memory Usage

```bash
# Limit memory usage
export MITS_MAX_MEMORY=512MB

# Enable memory monitoring
export MITS_MONITOR_MEMORY=true
```

### Timeout Configuration

```bash
# Set validation timeout
export MITS_VALIDATION_TIMEOUT=30

# Set URL fetch timeout
export URL_FETCH_TIMEOUT_SECONDS=5
```

### Concurrent Requests

```bash
# Limit concurrent requests
export MITS_MAX_CONCURRENT=10

# Set request queue size
export MITS_QUEUE_SIZE=100
```

## Logging

### Log Levels

```bash
# Set log level
export MITS_LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Log Format

```bash
# JSON format for structured logging
export MITS_LOG_FORMAT=json

# Human-readable format
export MITS_LOG_FORMAT=text
```

### Log Output

```bash
# Log to file
export MITS_LOG_FILE=/var/log/mits-validator.log

# Log to stdout
export MITS_LOG_OUTPUT=stdout
```

## Security

### Content Type Restrictions

```bash
# Restrict allowed content types
export MITS_ALLOWED_CONTENT_TYPES="application/xml,text/xml"

# Block suspicious content types
export MITS_BLOCK_SUSPICIOUS_TYPES=true
```

### Size Limits

```bash
# Set maximum file size
export MITS_MAX_FILE_SIZE=10485760  # 10MB

# Set maximum URL content size
export URL_FETCH_MAX_BYTES=10485760  # 10MB
```

### Network Security

```bash
# Disable URL validation
export MITS_DISABLE_URL_VALIDATION=true

# Restrict URL schemes
export MITS_ALLOWED_URL_SCHEMES="http,https"
```

## Monitoring

### Health Checks

```bash
# Enable health check endpoint
export MITS_ENABLE_HEALTH_CHECK=true

# Set health check interval
export MITS_HEALTH_CHECK_INTERVAL=30
```

### Metrics

```bash
# Enable metrics collection
export MITS_ENABLE_METRICS=true

# Set metrics endpoint
export MITS_METRICS_ENDPOINT=/metrics
```

## Troubleshooting

### Common Issues

1. **File too large**: Increase `MITS_MAX_FILE_SIZE`
2. **Timeout errors**: Increase `MITS_TIMEOUT_SECONDS`
3. **Memory issues**: Reduce `MITS_MAX_CONCURRENT`
4. **Network errors**: Check `URL_FETCH_TIMEOUT_SECONDS`

### Debug Mode

```bash
# Enable debug logging
export MITS_DEBUG=true
export MITS_LOG_LEVEL=DEBUG

# Run with verbose output
mits-api --debug
```

### Performance Profiling

```bash
# Enable profiling
export MITS_PROFILE=true

# Set profile output directory
export MITS_PROFILE_DIR=/tmp/mits-profile
```
