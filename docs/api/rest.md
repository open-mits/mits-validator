# REST API Reference

Complete reference for the MITS Validator REST API.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. In production deployments, consider implementing authentication and authorization.

## Content Types

### Request Content Types

- `multipart/form-data` - For file uploads
- `application/x-www-form-urlencoded` - For URL validation
- `application/json` - For JSON requests (future)

### Response Content Types

- `application/json` - All responses are JSON

## Endpoints

### Health Check

#### GET /health

Check the health status of the service.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- `200 OK` - Service is healthy
- `503 Service Unavailable` - Service is unhealthy

### Validation

#### POST /v1/validate

Validate a MITS XML feed.

**Request Body:**

For file upload:
```
Content-Type: multipart/form-data

file: <file content>
```

For URL validation:
```
Content-Type: application/x-www-form-urlencoded

url: <URL>
```

**Query Parameters:**
- `profile` (optional) - Validation profile to use
- `levels` (optional) - Comma-separated list of validation levels

**Headers:**
- `X-Profile` (optional) - Validation profile to use
- `X-Request-Id` (optional) - Custom request ID

**Response:**

Success (200 OK):
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

Error (400 Bad Request):
```json
{
  "summary": {
    "valid": false,
    "total_findings": 1,
    "errors": 1,
    "warnings": 0,
    "info": 0
  },
  "findings": [
    {
      "level": "error",
      "code": "INTAKE:NO_INPUT",
      "message": "No file or URL provided",
      "rule_ref": "internal://Intake"
    }
  ],
  "validator": {
    "levels_executed": [],
    "levels_available": ["WellFormed", "XSD", "Schematron", "Semantic"]
  },
  "metadata": {
    "request_id": "req_123",
    "timestamp": "2024-01-01T00:00:00Z",
    "engine": "mits-validator/0.1.0"
  }
}
```

**Status Codes:**
- `200 OK` - Validation completed successfully
- `400 Bad Request` - Invalid request (missing file/URL, invalid parameters)
- `413 Payload Too Large` - File/URL content exceeds size limit
- `415 Unsupported Media Type` - Unsupported content type
- `422 Unprocessable Entity` - Validation errors found
- `500 Internal Server Error` - Server error

## Response Format

### Result Envelope

All responses follow the Result Envelope format:

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

### Finding Object

```json
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
```

## Error Codes

### INTAKE - Input Validation

| Code | Severity | Title | Description |
|------|----------|-------|-------------|
| `INTAKE:NO_INPUT` | Error | No input provided | Neither file nor URL was provided |
| `INTAKE:BOTH_INPUTS` | Error | Both inputs provided | Both file and URL were provided |
| `INTAKE:TOO_LARGE` | Error | Content too large | File/URL content exceeds size limit |
| `INTAKE:UNSUPPORTED_MEDIA_TYPE` | Error | Unsupported media type | Content type not allowed |

### WELLFORMED - XML Parsing

| Code | Severity | Title | Description |
|------|----------|-------|-------------|
| `WELLFORMED:PARSE_ERROR` | Error | XML parse error | XML is not well-formed |
| `WELLFORMED:SUSPICIOUS_CONTENT_TYPE` | Warning | Suspicious content type | Content type may not be XML |

### XSD - Schema Validation

| Code | Severity | Title | Description |
|------|----------|-------|-------------|
| `XSD:SCHEMA_MISSING` | Info | Schema not found | XSD schema file not found |
| `XSD:VALIDATION_ERROR` | Error | Schema validation failed | XML does not conform to schema |

### SCHEMATRON - Business Rules

| Code | Severity | Title | Description |
|------|----------|-------|-------------|
| `SCHEMATRON:NO_RULES_LOADED` | Info | No rules loaded | No Schematron rules found |
| `SCHEMATRON:RULE_FAILURE` | Error | Rule validation failed | Business rule validation failed |

### SEMANTIC - Semantic Validation

| Code | Severity | Title | Description |
|------|----------|-------|-------------|
| `SEMANTIC:ENUM_UNKNOWN` | Warning | Unknown enumeration | Value not found in catalog |
| `SEMANTIC:LIMIT_EXCEEDED` | Error | Limit exceeded | Value exceeds allowed limit |
| `SEMANTIC:INCONSISTENT_TOTALS` | Error | Inconsistent totals | Calculated totals don't match |

### NETWORK - Network Operations

| Code | Severity | Title | Description |
|------|----------|-------|-------------|
| `NETWORK:TIMEOUT` | Error | Request timeout | URL fetch timed out |
| `NETWORK:CONNECTION_ERROR` | Error | Connection failed | Failed to connect to server |
| `NETWORK:HTTP_STATUS` | Error | HTTP error | Non-200 HTTP status code |
| `NETWORK:REQUEST_ERROR` | Error | Request failed | Network request failed |
| `NETWORK:FETCH_ERROR` | Error | Fetch error | Unexpected error during fetch |

### ENGINE - Engine Errors

| Code | Severity | Title | Description |
|------|----------|-------|-------------|
| `ENGINE:LEVEL_CRASH` | Error | Level crashed | Validation level crashed |
| `ENGINE:RESOURCE_LOAD_FAILED` | Error | Resource load failed | Failed to load validation resource |

## Examples

### File Upload

```bash
curl -X POST \
  -F "file=@feed.xml" \
  -H "X-Profile: pms-publisher" \
  http://localhost:8000/v1/validate
```

### URL Validation

```bash
curl -X POST \
  -d "url=https://example.com/feed.xml" \
  -H "X-Profile: ils-receiver" \
  http://localhost:8000/v1/validate
```

### With Query Parameters

```bash
curl -X POST \
  -F "file=@feed.xml" \
  "http://localhost:8000/v1/validate?profile=pms-publisher&levels=WellFormed,XSD"
```

### Error Response

```bash
curl -X POST \
  -F "file=@invalid.xml" \
  http://localhost:8000/v1/validate

# Response:
{
  "summary": {
    "valid": false,
    "total_findings": 1,
    "errors": 1,
    "warnings": 0,
    "info": 0
  },
  "findings": [
    {
      "level": "error",
      "code": "WELLFORMED:PARSE_ERROR",
      "message": "XML parse error: mismatched tag",
      "rule_ref": "internal://WellFormed",
      "location": {
        "line": 5,
        "column": 10,
        "xpath": "/MITS/Property[1]"
      }
    }
  ],
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

## Rate Limiting

Currently, no rate limiting is implemented. In production deployments, consider implementing rate limiting to prevent abuse.

## Caching

The API does not cache validation results. Each request is processed independently.

## Security Considerations

- **File Uploads**: Validate file size and content type
- **URL Validation**: Restrict to allowed schemes and domains
- **Content Type**: Only allow XML content types
- **Size Limits**: Enforce reasonable size limits
- **Timeouts**: Set appropriate timeouts for all operations

## Monitoring

### Health Checks

Monitor the `/health` endpoint for service availability.

### Metrics

Consider implementing metrics collection for:
- Request count and duration
- Error rates by type
- Validation level performance
- Resource usage

### Logging

The API logs all requests and responses. Consider implementing structured logging for better observability.
