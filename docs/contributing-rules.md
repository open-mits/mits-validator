# Contributing Rules

This guide explains how to add, edit, and maintain MITS validation rules and catalogs.

## Overview

The MITS Validator supports multiple types of rules and catalogs:

- **XSD Schemas** - XML structure validation
- **Schematron Rules** - Business logic validation  
- **MITS Catalogs** - Reference data for validation
- **Validation Profiles** - Configuration sets

## Adding XSD Schemas

XSD schemas validate XML structure and data types.

### Location
```
rules/xsd/
  schema.xsd          # Main MITS schema
  extensions/          # Additional schemas
    custom.xsd
```

### Requirements
- **Valid XSD 1.1** - Use XSD 1.1 features when needed
- **Namespace compliance** - Proper MITS namespace usage
- **Element documentation** - Document all elements and attributes
- **Type definitions** - Define custom types for complex data

### Example
```xml
<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           xmlns="http://www.mits.org/schema"
           targetNamespace="http://www.mits.org/schema"
           elementFormDefault="qualified">

  <xs:element name="MITS">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="Header" type="HeaderType"/>
        <xs:element name="Property" type="PropertyType" 
                    minOccurs="0" maxOccurs="unbounded"/>
      </xs:sequence>
      <xs:attribute name="version" type="xs:string" use="required"/>
    </xs:complexType>
  </xs:element>

  <!-- Type definitions -->
  <xs:complexType name="HeaderType">
    <xs:sequence>
      <xs:element name="Provider" type="xs:string"/>
      <xs:element name="Timestamp" type="xs:dateTime"/>
    </xs:sequence>
  </xs:complexType>

</xs:schema>
```

## Adding Schematron Rules

Schematron rules validate business logic and cross-field constraints.

### Location
```
rules/schematron/
  rules.sch           # Main business rules
  extensions/         # Additional rule sets
    custom.sch
```

### Requirements
- **Valid Schematron 1.6** - Use standard Schematron syntax
- **Clear assertions** - Use descriptive assertion messages
- **Context specificity** - Target specific elements and attributes
- **Rule documentation** - Document the business logic

### Example
```xml
<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron" 
            queryBinding="xslt2">
  <sch:title>MITS Business Rules</sch:title>

  <sch:pattern>
    <sch:title>Header Validation</sch:title>
    <sch:rule context="/MITS/Header">
      <sch:assert test="Provider">Header must contain a Provider element.</sch:assert>
      <sch:assert test="Timestamp">Header must contain a Timestamp element.</sch:assert>
      <sch:assert test="Timestamp castable as xs:dateTime">
        Timestamp must be a valid dateTime.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern>
    <sch:title>Property Validation</sch:title>
    <sch:rule context="/MITS/Property">
      <sch:assert test="PropertyID">Each Property must have a PropertyID.</sch:assert>
      <sch:assert test="Bedrooms >= 0">Bedrooms must be non-negative.</sch:assert>
      <sch:report test="not(Bedrooms) and not(Bathrooms)">
        Property should have at least Bedrooms or Bathrooms specified.
      </sch:report>
    </sch:rule>
  </sch:pattern>

</sch:schema>
```

## Adding MITS Catalogs

MITS catalogs provide reference data for validation and business logic.

### Location
```
rules/mits-5.0/
  catalogs/
    charge-classes.json          # Charge class definitions
    enums/                       # Enumeration catalogs
      charge-requirement.json
      refundability.json
      # ... more enums
    item-specializations/        # Item specialization schemas
      parking.json
      storage.json
      pet.json
  schemas/                       # JSON Schemas for validation
    charge-classes.schema.json
    enum.schema.json
    parking.schema.json
    # ... more schemas
```

### Catalog Entry Format

All catalog entries follow this structure:

```json
{
  "code": "UPPER_SNAKE_CASE",
  "name": "Human-friendly name",
  "description": "Optional detailed description",
  "aliases": ["optional", "alternative", "names"],
  "notes": "Optional implementation notes"
}
```

### Requirements
- **UPPER_SNAKE_CASE codes** - Use consistent naming convention
- **Unique codes** - No duplicates within a catalog file
- **Non-empty names** - Always provide a human-readable name
- **JSON Schema compliance** - Must validate against schema
- **Descriptive content** - Clear descriptions and notes

### Example: Charge Classes
```json
[
  {
    "code": "PET",
    "name": "Pet Fee",
    "description": "Monthly or one-time fees for pet ownership",
    "notes": "May include deposit, monthly fee, or both"
  },
  {
    "code": "PARKING",
    "name": "Parking Fee", 
    "description": "Fees for parking spaces or permits",
    "aliases": ["PARKING_PERMIT", "GARAGE_FEE"]
  }
]
```

### Example: Enumerations
```json
[
  {
    "code": "REQUIRED",
    "name": "Required",
    "description": "Charge is mandatory for this item"
  },
  {
    "code": "OPTIONAL", 
    "name": "Optional",
    "description": "Charge is optional for this item"
  }
]
```

### Example: Item Specializations
```json
{
  "pet_type": "DOG",
  "size_category": "MEDIUM", 
  "weight_limit": 50.0,
  "vaccination_required": true,
  "deposit_required": true,
  "amenities": ["DOG_PARK", "PET_WASTE_STATION"],
  "restrictions": ["LEASH_REQUIRED", "QUIET_HOURS"]
}
```

## Adding Validation Profiles

Validation profiles configure which levels to run and their limits.

### Location
```
src/mits_validator/profiles.py
```

### Profile Format
```python
@dataclass
class ValidationProfile:
    name: str
    levels: list[str]
    size_limit_mb: int
    timeout_seconds: int
    content_types: list[str]
```

### Example
```python
ValidationProfile(
    name="pms",
    levels=["WellFormed", "XSD"],
    size_limit_mb=5,
    timeout_seconds=15,
    content_types=["application/xml", "text/xml"]
)
```

## Testing Rules

### Unit Tests
Create tests for each rule type:

```python
def test_xsd_validation():
    """Test XSD schema validation."""
    result = validate_xml_against_schema(xml_content, schema_path)
    assert result.valid is True
    assert len(result.findings) == 0

def test_schematron_validation():
    """Test Schematron rule validation."""
    result = validate_xml_against_schematron(xml_content, rules_path)
    assert result.valid is True
    assert len(result.findings) == 0

def test_catalog_loading():
    """Test catalog loading and validation."""
    registry, findings = load_catalogs("mits-5.0")
    assert len(findings) == 0
    assert "PET" in registry.charge_classes
```

### Integration Tests
Test rules in the full validation pipeline:

```python
def test_full_validation_pipeline():
    """Test complete validation with all rules."""
    result = validate_mits_feed(xml_content, profile="default")
    assert result["summary"]["valid"] is True
    assert len(result["findings"]) == 0
```

## Validation Checklist

Before submitting rules:

- [ ] **Schema compliance** - All files validate against their schemas
- [ ] **Unique codes** - No duplicate codes within catalogs
- [ ] **Naming conventions** - UPPER_SNAKE_CASE for codes
- [ ] **Documentation** - Clear descriptions and notes
- [ ] **Tests** - Unit and integration tests pass
- [ ] **CI validation** - `scripts/validate_catalogs.py` passes
- [ ] **Error handling** - Proper error codes and messages
- [ ] **Performance** - Rules don't significantly slow validation

## Running Validation

### Local Validation
```bash
# Validate all catalogs
uv run python scripts/validate_catalogs.py

# Run specific tests
uv run pytest tests/test_catalog_loader.py

# Run all tests
uv run pytest
```

### CI Validation
The CI pipeline automatically:
- Validates all catalog files against schemas
- Checks for duplicate codes
- Runs all tests
- Ensures code quality standards

## Best Practices

### Rule Design
- **Fail fast** - Catch errors early in the validation pipeline
- **Clear messages** - Provide actionable error messages
- **Specific context** - Include location information when possible
- **Performance** - Optimize for speed and memory usage

### Code Organization
- **Modular structure** - Keep rules organized by type and purpose
- **Version control** - Use clear commit messages and PR descriptions
- **Documentation** - Document all rules and their purpose
- **Testing** - Comprehensive test coverage

### Maintenance
- **Regular updates** - Keep rules current with MITS specifications
- **Deprecation handling** - Mark deprecated rules clearly
- **Version compatibility** - Ensure backward compatibility
- **Performance monitoring** - Track validation performance

## Getting Help

- **Documentation** - Check existing docs and examples
- **Issues** - Create GitHub issues for questions or problems
- **Discussions** - Use GitHub Discussions for general questions
- **Code review** - Request reviews for complex changes
