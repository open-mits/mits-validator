# Quick Start

Get up and running with MITS Validator in minutes.

## Web Service

### Start the API Server

```bash
# Start the server
mits-api

# Server will be available at http://localhost:8000
```

### Health Check

```bash
# Check if the service is running
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "version": "0.1.0",
#   "timestamp": "2024-01-01T00:00:00Z"
# }
```

### Validate a File

```bash
# Upload and validate a MITS XML file
curl -X POST -F "file=@feed.xml" http://localhost:8000/v1/validate

# Expected response:
# {
#   "summary": {
#     "valid": true,
#     "total_findings": 0,
#     "errors": 0,
#     "warnings": 0,
#     "info": 0
#   },
#   "findings": [],
#   "validator": {
#     "levels_executed": ["WellFormed"],
#     "levels_available": ["WellFormed", "XSD", "Schematron", "Semantic"]
#   },
#   "metadata": {
#     "request_id": "req_123",
#     "timestamp": "2024-01-01T00:00:00Z",
#     "engine": "mits-validator/0.1.0"
#   }
# }
```

### Validate from URL

```bash
# Validate a MITS feed from a URL
curl -X POST -d "url=https://example.com/feed.xml" http://localhost:8000/v1/validate
```

## CLI Usage

### Basic Validation

```bash
# Validate a local file
mits-validate validate --file feed.xml

# Validate from URL
mits-validate validate --url https://example.com/feed.xml

# Get JSON output
mits-validate validate --file feed.xml --json
```

### Using Profiles

```bash
# Use a specific validation profile
mits-validate validate --file feed.xml --profile pms-publisher

# Available profiles:
# - default: All validation levels
# - ils-receiver: Basic validation for ILS systems
# - pms-publisher: Full validation for PMS publishers
```

## Examples

### Valid MITS Feed

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MITS version="5.0">
  <Header>
    <Provider>Example Property Management</Provider>
    <Timestamp>2024-01-01T00:00:00Z</Timestamp>
  </Header>
  <Property>
    <PropertyID>12345</PropertyID>
    <Bedrooms>2</Bedrooms>
    <Bathrooms>1</Bathrooms>
  </Property>
</MITS>
```

### Validation Response

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

## Next Steps

- [Configuration](configuration.md) - Configure the validator for your needs
- [Validation Levels](validation-levels.md) - Understand the different validation levels
- [Error Codes](error-codes.md) - Learn about error codes and messages
