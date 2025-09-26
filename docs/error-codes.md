# Error Codes & Messages

The MITS Validator uses a structured error taxonomy with consistent codes, messages, and remediation guidance.

## Error Code Format

All error codes follow the pattern: `CATEGORY:SUBCODE`

- **CATEGORY** - High-level error category (e.g., `INTAKE`, `WELLFORMED`)
- **SUBCODE** - Specific error within the category (e.g., `PARSE_ERROR`, `TOO_LARGE`)

## Error Categories

### INTAKE - Input Validation Errors

Errors related to input validation, content type checking, and size limits.

| Code | Severity | Title | Description |
|------|----------|-------|-------------|
| `INTAKE:BOTH_INPUTS` | Error | Both file and URL provided | Must provide either file upload or URL, not both |
| `INTAKE:NO_INPUT` | Error | No input provided | Must provide either file upload or URL |
| `INTAKE:TOO_LARGE` | Error | File too large | File size exceeds the configured limit |
| `INTAKE:UNSUPPORTED_MEDIA_TYPE` | Error | Unsupported content type | Content type not in allowlist |
| `INTAKE:OCTET_STREAM_WARNING` | Warning | Octet-stream content type | Using generic binary content type |

### WELLFORMED - XML Parsing Errors

Errors related to XML syntax and structure validation.

| Code | Severity | Title | Description |
|------|----------|-------|-------------|
| `WELLFORMED:PARSE_ERROR` | Error | XML parsing failed | XML syntax error or malformed structure |
| `WELLFORMED:UNEXPECTED_ERROR` | Error | Unexpected parsing error | Unexpected error during XML parsing |

### XSD - Schema Validation Errors

Errors related to XSD schema conformance validation.

| Code | Severity | Title | Description |
|------|----------|-------|-------------|
| `XSD:VALIDATION_ERROR` | Error | Schema validation failed | XML does not conform to XSD schema |
| `XSD:SCHEMA_MISSING` | Warning | Schema not available | No XSD schema found for validation |

### SCHEMATRON - Business Rule Errors

Errors related to Schematron business rule validation.

| Code | Severity | Title | Description |
|------|----------|-------|-------------|
| `SCHEMATRON:RULE_FAILURE` | Error | Business rule failed | XML failed Schematron business rule |
| `SCHEMATRON:NO_RULES_LOADED` | Info | No rules available | No Schematron rules found for validation |

### NETWORK - Network and URL Errors

Errors related to URL fetching and network operations.

| Code | Severity | Title | Description |
|------|----------|-------|-------------|
| `NETWORK:TIMEOUT` | Error | Network timeout | Request timed out while fetching URL |
| `NETWORK:CONNECTION_ERROR` | Error | Connection failed | Unable to connect to URL |
| `NETWORK:HTTP_STATUS` | Error | HTTP error status | URL returned error status code |
| `NETWORK:REQUEST_ERROR` | Error | Request failed | General request error |
| `NETWORK:FETCH_ERROR` | Error | Fetch failed | Error occurred while fetching content |

### URL - URL Intake Errors

Errors related to URL input validation.

| Code | Severity | Title | Description |
|------|----------|-------|-------------|
| `URL:INTAKE_ACKNOWLEDGED` | Info | URL intake acknowledged | URL validation is experimental |

### ENGINE - System Errors

Errors related to the validation engine and system failures.

| Code | Severity | Title | Description |
|------|----------|-------|-------------|
| `ENGINE:LEVEL_CRASH` | Error | Validation level crashed | A validation level encountered an unexpected error |

### CATALOG - Catalog Loading Errors

Errors related to MITS catalog loading and validation.

| Code | Severity | Title | Description |
|------|----------|-------|-------------|
| `CATALOG:VERSION_NOT_FOUND` | Error | Catalog version not found | The specified MITS catalog version directory was not found |
| `CATALOG:FILE_MISSING` | Warning | Catalog file missing | A required catalog file was not found |
| `CATALOG:DIRECTORY_MISSING` | Warning | Catalog directory missing | A required catalog directory was not found |
| `CATALOG:INVALID_JSON` | Error | Invalid JSON in catalog | Catalog file contains invalid JSON syntax |
| `CATALOG:SCHEMA_VALIDATION_ERROR` | Error | Catalog schema validation failed | Catalog file does not conform to its JSON schema |
| `CATALOG:DUPLICATE_CODE` | Error | Duplicate catalog code | Duplicate code found within a catalog file |

## Severity Levels

### Error
- **Impact**: Validation fails, `summary.valid = false`
- **Action**: Must be addressed before validation can succeed
- **Examples**: Malformed XML, schema violations, system crashes

### Warning
- **Impact**: Validation succeeds but with concerns
- **Action**: Should be reviewed and addressed
- **Examples**: Missing schemas, deprecated content types

### Info
- **Impact**: Informational only, no impact on validation
- **Action**: Optional, for awareness
- **Examples**: Experimental features, missing optional resources

## Message Standards

All error messages follow these standards:

- **One-line** - Single, concise message
- **Human-readable** - Clear and understandable
- **Present tense** - "XML parsing failed" not "XML parsing has failed"
- **Specific** - Include relevant details when possible
- **Actionable** - Suggest next steps when appropriate

## Location Information

When available, error messages include location information:

```json
{
  "level": "error",
  "code": "WELLFORMED:PARSE_ERROR",
  "message": "XML parsing failed: unexpected end of file",
  "location": {
    "line": 123,
    "column": 4,
    "xpath": "/Root/Node[2]"
  }
}
```

## Remediation Guidance

Each error code includes remediation guidance:

- **Clear cause** - What caused the error
- **Next steps** - How to fix the issue
- **Prevention** - How to avoid the error in the future

## Error Code Stability

Error codes are stable and will not change without a major version bump:

- **Addition** - New codes can be added
- **Deprecation** - Codes can be marked as deprecated
- **Removal** - Codes are only removed in major versions
- **Changes** - Code meanings are never changed

## Using Error Codes

### In Validation Results

Error codes are included in the `findings` array:

```json
{
  "findings": [
    {
      "level": "error",
      "code": "WELLFORMED:PARSE_ERROR",
      "message": "XML parsing failed: unexpected end of file",
      "location": {
        "line": 123,
        "column": 4
      },
      "rule_ref": "internal://WellFormed"
    }
  ]
}
```

### In Code

Error codes are defined in the central error catalog:

```python
from mits_validator.errors import get_error_definition

# Get error definition
error_def = get_error_definition("WELLFORMED:PARSE_ERROR")
print(error_def.title)  # "XML parsing failed"
print(error_def.remediation)  # "Fix XML syntax errors"
```

### In Tests

Test error codes for proper behavior:

```python
def test_xml_parsing_error():
    result = validate_malformed_xml()
    assert result["summary"]["valid"] is False
    assert any(f["code"] == "WELLFORMED:PARSE_ERROR" for f in result["findings"])
```
