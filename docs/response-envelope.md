# Response Envelope (v1)

The MITS Validator uses a standardized response envelope for all API responses, ensuring consistency and predictability.

## Envelope Structure

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

## Field Descriptions

### Summary

- **`valid`**: `true` if no errors found, `false` if any errors exist
- **`total_findings`**: Total number of findings across all levels
- **`errors`**: Number of error-level findings
- **`warnings`**: Number of warning-level findings
- **`info`**: Number of info-level findings

### Findings

Each finding represents a validation issue:

- **`level`**: Severity level (`error`, `warning`, `info`)
- **`code`**: Standardized error code (`CATEGORY:SUBCODE`)
- **`message`**: Human-readable description
- **`rule_ref`**: Reference to the validation rule
- **`location`**: Optional location information (line, column, xpath)

### Validator

- **`levels_executed`**: List of validation levels that were executed
- **`levels_available`**: List of all available validation levels

### Metadata

- **`request_id`**: Unique identifier for the request
- **`timestamp`**: ISO 8601 timestamp of the validation
- **`engine`**: Version information about the validation engine

## Validation Rules

### Validity Determination

The `valid` field is `true` if and only if:
- No error-level findings exist
- All required validation levels executed successfully
- No critical system errors occurred

### Finding Levels

- **`error`**: Critical issues that must be fixed
- **`warning`**: Issues that should be addressed
- **`info`**: Informational messages

### Error Codes

Error codes follow the format `CATEGORY:SUBCODE`:

- **`INTAKE:*`**: Input validation errors
- **`WELLFORMED:*`**: XML parsing errors
- **`XSD:*`**: Schema validation errors
- **`SCHEMATRON:*`**: Business rule errors
- **`SEMANTIC:*`**: Semantic validation errors
- **`NETWORK:*`**: Network operation errors
- **`ENGINE:*`**: Engine-level errors

## Examples

### Successful Validation

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
    "levels_executed": ["WellFormed", "XSD"],
    "levels_available": ["WellFormed", "XSD", "Schematron", "Semantic"]
  },
  "metadata": {
    "request_id": "req_123",
    "timestamp": "2024-01-15T10:30:00Z",
    "engine": "mits-validator/0.1.0"
  }
}
```

### Validation with Errors

```json
{
  "summary": {
    "valid": false,
    "total_findings": 2,
    "errors": 1,
    "warnings": 1,
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
    },
    {
      "level": "warning",
      "code": "XSD:VALIDATION_ERROR",
      "message": "Element 'Property' is missing required attribute 'PropertyID'",
      "rule_ref": "internal://XSD",
      "location": {
        "line": 3,
        "column": 5,
        "xpath": "/MITS/Property[1]"
      }
    }
  ],
  "validator": {
    "levels_executed": ["WellFormed", "XSD"],
    "levels_available": ["WellFormed", "XSD", "Schematron", "Semantic"]
  },
  "metadata": {
    "request_id": "req_124",
    "timestamp": "2024-01-15T10:31:00Z",
    "engine": "mits-validator/0.1.0"
  }
}
```

### Validation with Missing Resources

```json
{
  "summary": {
    "valid": true,
    "total_findings": 1,
    "errors": 0,
    "warnings": 0,
    "info": 1
  },
  "findings": [
    {
      "level": "info",
      "code": "XSD:SCHEMA_MISSING",
      "message": "No XSD schema available for validation",
      "rule_ref": "internal://XSD"
    }
  ],
  "validator": {
    "levels_executed": ["WellFormed"],
    "levels_available": ["WellFormed", "XSD", "Schematron", "Semantic"]
  },
  "metadata": {
    "request_id": "req_125",
    "timestamp": "2024-01-15T10:32:00Z",
    "engine": "mits-validator/0.1.0"
  }
}
```

## Backward Compatibility

### Versioning Policy

- **v1**: Current stable version
- **Future versions**: Will include `api_version` field
- **Breaking changes**: Require new `api_version`
- **Additive changes**: Allowed within same version

### Migration Strategy

When introducing breaking changes:

1. **Announce deprecation**: 6 months notice
2. **Maintain compatibility**: Support both versions
3. **Provide migration guide**: Clear upgrade path
4. **Remove old version**: After deprecation period

### Additive Changes

The following changes are allowed within v1:

- New fields in metadata
- New validation levels
- New error codes
- Additional location information
- New finding properties

## JSON Schema

The response envelope is validated against a JSON Schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["summary", "findings", "validator", "metadata"],
  "properties": {
    "summary": {
      "type": "object",
      "required": ["valid", "total_findings", "errors", "warnings", "info"],
      "properties": {
        "valid": {"type": "boolean"},
        "total_findings": {"type": "integer", "minimum": 0},
        "errors": {"type": "integer", "minimum": 0},
        "warnings": {"type": "integer", "minimum": 0},
        "info": {"type": "integer", "minimum": 0}
      }
    },
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["level", "code", "message", "rule_ref"],
        "properties": {
          "level": {"enum": ["error", "warning", "info"]},
          "code": {"type": "string", "pattern": "^[A-Z_]+:[A-Z_]+$"},
          "message": {"type": "string", "minLength": 1},
          "rule_ref": {"type": "string"},
          "location": {
            "type": "object",
            "properties": {
              "line": {"type": "integer", "minimum": 1},
              "column": {"type": "integer", "minimum": 1},
              "xpath": {"type": "string"}
            }
          }
        }
      }
    },
    "validator": {
      "type": "object",
      "required": ["levels_executed", "levels_available"],
      "properties": {
        "levels_executed": {
          "type": "array",
          "items": {"type": "string"}
        },
        "levels_available": {
          "type": "array",
          "items": {"type": "string"}
        }
      }
    },
    "metadata": {
      "type": "object",
      "required": ["request_id", "timestamp", "engine"],
      "properties": {
        "request_id": {"type": "string"},
        "timestamp": {"type": "string", "format": "date-time"},
        "engine": {"type": "string"}
      }
    }
  }
}
```

## Contract Testing

The response envelope is validated in contract tests to ensure:

1. **Schema compliance**: All responses conform to the JSON Schema
2. **Field presence**: Required fields are always present
3. **Type correctness**: All fields have correct types
4. **Value constraints**: Values meet minimum/maximum requirements
5. **Consistency**: Error codes and messages are consistent

## Error Handling

### Standard Error Responses

All error responses follow the same envelope structure:

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
    "request_id": "req_126",
    "timestamp": "2024-01-15T10:33:00Z",
    "engine": "mits-validator/0.1.0"
  }
}
```

### HTTP Status Codes

- **200 OK**: Validation completed successfully
- **400 Bad Request**: Invalid request (missing file/URL, invalid parameters)
- **413 Payload Too Large**: File/URL content exceeds size limit
- **415 Unsupported Media Type**: Unsupported content type
- **422 Unprocessable Entity**: Validation errors found
- **500 Internal Server Error**: Server error

## Best Practices

### For API Consumers

1. **Check `valid` field**: Use this to determine if validation passed
2. **Handle findings**: Process all findings, not just errors
3. **Use error codes**: Implement error code-based handling
4. **Check levels**: Verify which levels were executed
5. **Log request IDs**: Use for debugging and support

### For API Developers

1. **Always use envelope**: Never return raw data
2. **Consistent error codes**: Use standardized error codes
3. **Meaningful messages**: Provide actionable error messages
4. **Include location**: Add location information when available
5. **Test thoroughly**: Ensure all paths return valid envelope

## Future Enhancements

### Planned Additions

- **Performance metrics**: Validation timing information
- **Resource usage**: Memory and CPU usage statistics
- **Configuration info**: Active profile and settings
- **Version info**: MITS specification version used

### Extension Points

- **Custom fields**: Profile-specific metadata
- **Additional levels**: New validation types
- **Enhanced location**: More detailed location information
- **Structured data**: Machine-readable finding details

This response envelope provides a stable, predictable interface for MITS validation while maintaining flexibility for future enhancements.
