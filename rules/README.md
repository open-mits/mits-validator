# Validation Rules Directory

This directory contains validation rules and schemas for the MITS validator.

## Directory Structure

```
rules/
├── xsd/                    # XSD schema files
│   └── schema.xsd         # Main MITS schema (placeholder)
├── schematron/            # Schematron rule files
│   └── rules.sch         # Business rules (placeholder)
├── profiles/              # Validation profile configurations
│   ├── default.yaml      # Default profile
│   ├── pms.yaml         # Property Management System profile
│   ├── ils.yaml         # Internet Listing Service profile
│   └── marketplace.yaml  # Marketplace profile
└── README.md             # This file
```

## Adding New Rules

### XSD Schemas

1. Place XSD schema files in `rules/xsd/`
2. Update the validation engine to load the schema
3. Test with sample XML files

### Schematron Rules

1. Place Schematron rule files in `rules/schematron/`
2. Ensure rules follow the MITS specification
3. Test with both valid and invalid XML

### Validation Profiles

1. Create or update profile YAML files in `rules/profiles/`
2. Define which levels and rules are active
3. Set size limits and timeouts appropriately

## Rule Development Guidelines

- **Error Codes**: Use the established taxonomy (CATEGORY:SUBCODE)
- **Severity**: Choose appropriate level (error, warning, info)
- **Messages**: Write clear, actionable error messages
- **Location**: Include line/column/xpath when possible
- **Testing**: Add unit tests for each rule

## Testing Rules

```bash
# Test with sample XML
uv run python -c "
from mits_validator.validation import ValidationEngine
engine = ValidationEngine()
results = engine.validate(b'<xml>test</xml>', 'application/xml')
print(results)
"
```

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines on adding new validation rules.
