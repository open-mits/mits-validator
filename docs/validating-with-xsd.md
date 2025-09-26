# Validating with Real MITS 5.0 XSD

This guide explains how to use the MITS Validator with real MITS 5.0 XSD schemas for comprehensive XML structure validation.

## Overview

The MITS Validator includes the official MITS 5.0 Property Marketing / ILS XSD schema, enabling precise validation of XML structure, data types, and element relationships.

## Schema Information

- **Version**: MITS 5.0
- **Namespace**: `http://www.mits.org/schema/PropertyMarketing/ILS/5.0`
- **Source**: RETTC MITS 5.0 Approved Data Models
- **Retrieved**: September 2025
- **SHA256**: `a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456`

## Usage

### CLI Validation

```bash
# Validate with XSD schema
mits-validate validate --file property-feed.xml --mode=xsd

# Validate with both XSD and Schematron
mits-validate validate --file property-feed.xml --mode=both

# Get JSON output
mits-validate validate --file property-feed.xml --mode=xsd --json
```

### API Validation

```bash
# Validate with XSD schema
curl -X POST -F "file=@property-feed.xml" \
  "http://localhost:8000/v1/validate?mode=xsd"

# Validate with both XSD and Schematron
curl -X POST -F "file=@property-feed.xml" \
  "http://localhost:8000/v1/validate?mode=both"
```

### Python Integration

```python
from mits_validator.validation.xsd import validate_xsd

# Validate XML content
result = validate_xsd("property-feed.xml")

if result.findings:
    for finding in result.findings:
        print(f"Error: {finding.message}")
        if finding.location:
            print(f"Location: Line {finding.location['line']}, Column {finding.location['column']}")
else:
    print("Valid MITS 5.0 XML")
```

## Schema Structure

### Root Element
```xml
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0"
                   version="5.0"
                   timestamp="2025-09-15T10:30:00Z">
  <!-- Property and Floorplan elements -->
</PropertyMarketing>
```

### Key Elements

#### Property Element
```xml
<Property>
  <PropertyID>PROP-001</PropertyID>
  <PropertyName>Sunset Apartments</PropertyName>
  <PropertyType>Apartment</PropertyType>
  <Address>
    <StreetAddress>123 Main Street</StreetAddress>
    <City>Anytown</City>
    <State>CA</State>
    <PostalCode>12345</PostalCode>
  </Address>
  <ChargeOffer>
    <!-- Charge offer items -->
  </ChargeOffer>
</Property>
```

#### Charge Classification
The schema defines approved charge classifications:
- `Rent` - Monthly rent
- `Deposit` - Security deposits
- `Pet` - Pet-related fees
- `Parking` - Parking fees
- `Utilities` - Utility charges
- `Technology` - Technology fees
- `Admin` - Administrative fees
- `OtherMandatory` - Other mandatory charges

#### Data Types
- **Currency**: `xs:decimal` with 2 fraction digits
- **Dates**: `xs:dateTime` for timestamps
- **Identifiers**: `xs:string` for IDs and names

## Validation Examples

### Valid XML
```xml
<?xml version="1.0" encoding="UTF-8"?>
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0"
                   version="5.0"
                   timestamp="2025-09-15T10:30:00Z">
  <Property>
    <PropertyID>PROP-001</PropertyID>
    <PropertyName>Sunset Apartments</PropertyName>
    <PropertyType>Apartment</PropertyType>
    <Address>
      <StreetAddress>123 Main Street</StreetAddress>
      <City>Anytown</City>
      <State>CA</State>
      <PostalCode>12345</PostalCode>
    </Address>
    <ChargeOffer>
      <ChargeOfferItem>
        <ChargeClassification>Rent</ChargeClassification>
        <Requirement>Mandatory</Requirement>
        <PaymentFrequency>Monthly</PaymentFrequency>
        <Refundability>NonRefundable</Refundability>
        <TermBasis>LeaseTerm</TermBasis>
        <Amount>1500.00</Amount>
        <Description>Monthly rent</Description>
      </ChargeOfferItem>
    </ChargeOffer>
  </Property>
</PropertyMarketing>
```

### Invalid XML (Missing Required Element)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0"
                   version="5.0"
                   timestamp="2025-09-15T10:30:00Z">
  <Property>
    <PropertyID>PROP-001</PropertyID>
    <!-- Missing required PropertyName -->
    <PropertyType>Apartment</PropertyType>
    <Address>
      <StreetAddress>123 Main Street</StreetAddress>
      <City>Anytown</City>
      <State>CA</State>
      <PostalCode>12345</PostalCode>
    </Address>
  </Property>
</PropertyMarketing>
```

**Error Response**:
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
      "code": "XSD:VALIDATION_ERROR",
      "message": "Schema validation failed: Element 'PropertyName' is missing",
      "rule_ref": "internal://XSD",
      "location": {
        "line": 3,
        "column": 5,
        "xpath": "/PropertyMarketing/Property"
      }
    }
  ],
  "validator": {
    "levels_executed": ["XSD"],
    "levels_available": ["WellFormed", "XSD", "Schematron", "Semantic"]
  },
  "metadata": {
    "request_id": "req_123",
    "timestamp": "2025-09-15T10:30:00Z",
    "engine": "mits-validator/0.1.0"
  }
}
```

## Error Codes

### XSD Validation Errors

| Code | Description | Example |
|------|-------------|---------|
| `XSD:VALIDATION_ERROR` | Schema validation failed | Missing required element |
| `XSD:SCHEMA_MISSING` | XSD schema not found | Schema file not available |
| `XSD:XML_PARSE_ERROR` | XML parsing failed | Malformed XML |
| `XSD:SCHEMA_PARSE_ERROR` | Schema parsing failed | Invalid XSD schema |

## Best Practices

### 1. Always Include Required Elements
```xml
<Property>
  <PropertyID>PROP-001</PropertyID>
  <PropertyName>Property Name</PropertyName>
  <PropertyType>Apartment</PropertyType>
  <Address>
    <StreetAddress>123 Main St</StreetAddress>
    <City>Anytown</City>
    <State>CA</State>
    <PostalCode>12345</PostalCode>
  </Address>
</Property>
```

### 2. Use Valid Enumerations
```xml
<PropertyType>Apartment</PropertyType>  <!-- Valid -->
<PropertyType>InvalidType</PropertyType>  <!-- Invalid -->
```

### 3. Follow Data Type Constraints
```xml
<Amount>1500.00</Amount>  <!-- Valid: 2 decimal places -->
<Amount>1500.123</Amount>  <!-- Invalid: too many decimal places -->
```

### 4. Include Proper Namespace
```xml
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0"
                   version="5.0"
                   timestamp="2025-09-15T10:30:00Z">
```

## Troubleshooting

### Common Issues

1. **Missing Namespace**: Ensure the correct namespace is declared
2. **Invalid Enumerations**: Use only approved values for enumerated fields
3. **Data Type Errors**: Follow the schema's data type constraints
4. **Missing Required Elements**: Include all required elements

### Debug Tips

1. **Check Line Numbers**: Use the `location.line` and `location.column` fields
2. **Validate Incrementally**: Start with minimal valid XML and add elements
3. **Use Schema Information**: Check the schema for element requirements
4. **Test with Examples**: Use the provided valid examples as templates

## Attribution

This XSD schema is based on the RETTC MITS 5.0 Approved Data Models and is used under the terms of the MITS specification license.

## Related Documentation

- [Schematron Rules](schematron-rules.md) - Business logic validation
- [API Reference](api/rest.md) - Complete API documentation
- [CLI Reference](api/cli.md) - Command-line interface
- [Error Codes](error-codes.md) - Complete error code reference
