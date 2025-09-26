# Schematron Rules: Examples & Contribution Guide

This guide explains how to use and contribute to Schematron business rules for MITS validation.

## Overview

Schematron rules provide business logic validation beyond XSD schema validation. They enforce cross-field relationships, business constraints, and data quality rules.

## Current Rules

The MITS Validator includes the following business rules:

### 1. Charge Classification Validity
**Rule**: Charge classifications must be from the approved list
**Context**: `ChargeOfferItem/ChargeClassification`
**Valid Values**: Rent, Deposit, Pet, Parking, Utilities, Technology, Admin, OtherMandatory

### 2. Requirement + Frequency Consistency
**Rule**: Mandatory charges must have a PaymentFrequency
**Context**: `ChargeOfferItem`
**Logic**: If `Requirement="Mandatory"`, then `PaymentFrequency` must be present

### 3. Refundability Coherence
**Rule**: Deposit charges must have Description or Amount
**Context**: `ChargeOfferItem`
**Logic**: If `Refundability="Deposit"`, then Description or Amount must be present

### 4. Term Basis Consistency
**Rule**: SpecificTerm charges must have valid date ranges
**Context**: `ChargeOfferItem`
**Logic**: If `TermBasis="SpecificTerm"`, then StartTermEarliest ≤ StartTermLatest

## Usage

### CLI Validation

```bash
# Validate with Schematron rules only
mits-validate validate --file property-feed.xml --mode=schematron

# Validate with both XSD and Schematron
mits-validate validate --file property-feed.xml --mode=both
```

### API Validation

```bash
# Validate with Schematron rules
curl -X POST -F "file=@property-feed.xml" \
  "http://localhost:8000/v1/validate?mode=schematron"

# Validate with both modes
curl -X POST -F "file=@property-feed.xml" \
  "http://localhost:8000/v1/validate?mode=both"
```

### Python Integration

```python
from mits_validator.validation.schematron import validate_schematron

# Validate XML content
result = validate_schematron("property-feed.xml")

if result.findings:
    for finding in result.findings:
        print(f"Business Rule Violation: {finding.message}")
        if finding.location:
            print(f"Rule: {finding.location.get('rule_id', 'unknown')}")
else:
    print("All business rules passed")
```

## Rule Examples

### Valid XML (All Rules Pass)
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

### Invalid XML (Rule Violations)

#### Invalid Charge Classification
```xml
<ChargeOfferItem>
  <ChargeClassification>InvalidCharge</ChargeClassification>
  <Requirement>Mandatory</Requirement>
  <PaymentFrequency>Monthly</PaymentFrequency>
  <Refundability>NonRefundable</Refundability>
  <TermBasis>LeaseTerm</TermBasis>
  <Amount>1500.00</Amount>
</ChargeOfferItem>
```

**Error**: `Charge classification 'InvalidCharge' is not valid. Must be one of: Rent, Deposit, Pet, Parking, Utilities, Technology, Admin, OtherMandatory`

#### Missing Payment Frequency
```xml
<ChargeOfferItem>
  <ChargeClassification>Rent</ChargeClassification>
  <Requirement>Mandatory</Requirement>
  <!-- Missing PaymentFrequency -->
  <Refundability>NonRefundable</Refundability>
  <TermBasis>LeaseTerm</TermBasis>
  <Amount>1500.00</Amount>
</ChargeOfferItem>
```

**Error**: `Mandatory charges must have a PaymentFrequency specified`

#### Deposit Without Description
```xml
<ChargeOfferItem>
  <ChargeClassification>Deposit</ChargeClassification>
  <Requirement>Mandatory</Requirement>
  <PaymentFrequency>OneTime</PaymentFrequency>
  <Refundability>Deposit</Refundability>
  <TermBasis>LeaseTerm</TermBasis>
  <Amount>1500.00</Amount>
  <!-- Missing Description -->
</ChargeOfferItem>
```

**Error**: `Deposit charges must have either a Description or Amount specified`

## Adding New Rules

### 1. Create Rule File
Create a new `.sch` file in `rules/schematron/5.0/`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron" 
            queryBinding="xslt2"
            xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0">

  <sch:title>Custom Business Rules</sch:title>
  <sch:description>Custom business logic validation rules</sch:description>

  <sch:pattern>
    <sch:title>Custom Rule</sch:title>
    <sch:rule context="ChargeOfferItem">
      <sch:assert test="Amount > 0">
        Charge amounts must be positive
      </sch:assert>
    </sch:rule>
  </sch:pattern>

</sch:schema>
```

### 2. Rule Syntax

#### Basic Assertion
```xml
<sch:assert test="condition">
  Error message when condition is false
</sch:assert>
```

#### Successful Report
```xml
<sch:report test="condition">
  Warning message when condition is true
</sch:report>
```

#### Context and Test Examples
```xml
<!-- Check element exists -->
<sch:assert test="PropertyName">
  Property must have a name
</sch:assert>

<!-- Check element value -->
<sch:assert test="Amount > 0">
  Amount must be positive
</sch:assert>

<!-- Check multiple conditions -->
<sch:assert test="Requirement='Mandatory' and PaymentFrequency">
  Mandatory charges must have payment frequency
</sch:assert>

<!-- Check enumeration -->
<sch:assert test="PropertyType='Apartment' or PropertyType='Condo' or PropertyType='House'">
  Property type must be valid
</sch:assert>
```

### 3. Test Your Rules

Create test XML files in `fixtures/mits5/`:

```xml
<!-- valid-custom-rule.xml -->
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0"
                   version="5.0"
                   timestamp="2025-09-15T10:30:00Z">
  <Property>
    <PropertyID>PROP-001</PropertyID>
    <PropertyName>Test Property</PropertyName>
    <PropertyType>Apartment</PropertyType>
    <!-- Valid XML that should pass your rule -->
  </Property>
</PropertyMarketing>
```

```xml
<!-- invalid-custom-rule.xml -->
<PropertyMarketing xmlns="http://www.mits.org/schema/PropertyMarketing/ILS/5.0"
                   version="5.0"
                   timestamp="2025-09-15T10:30:00Z">
  <Property>
    <PropertyID>PROP-001</PropertyID>
    <PropertyName>Test Property</PropertyName>
    <PropertyType>Apartment</PropertyType>
    <!-- Invalid XML that should trigger your rule -->
  </Property>
</PropertyMarketing>
```

### 4. Add Tests

Create tests in `tests/schematron/`:

```python
def test_custom_rule():
    """Test custom business rule."""
    xml_content = """<!-- Your test XML -->"""
    
    result = validate_schematron(xml_content)
    
    # Assert expected findings
    assert len(result.findings) == 1
    assert result.findings[0].level == FindingLevel.ERROR
    assert "Custom rule message" in result.findings[0].message
```

### 5. Update Documentation

Add your rule to this documentation:

```markdown
### 5. Custom Rule
**Rule**: Your rule description
**Context**: `Element/Path`
**Logic**: Your rule logic
```

## Rule Development Guidelines

### 1. Clear Messages
Write clear, actionable error messages:
```xml
<sch:assert test="Amount > 0">
  Charge amounts must be positive (found: <sch:value-of select="Amount"/>)
</sch:assert>
```

### 2. Specific Contexts
Target specific elements:
```xml
<sch:rule context="ChargeOfferItem">
  <!-- Rule applies only to ChargeOfferItem elements -->
</sch:rule>
```

### 3. Use XPath Effectively
```xml
<!-- Check parent element -->
<sch:assert test="../PropertyName">
  Property must have a name
</sch:assert>

<!-- Check sibling elements -->
<sch:assert test="Requirement='Mandatory' and PaymentFrequency">
  Mandatory charges must have payment frequency
</sch:assert>

<!-- Check attribute values -->
<sch:assert test="@propertyID">
  Property must have an ID
</sch:assert>
```

### 4. Test Thoroughly
- Create both valid and invalid test cases
- Test edge cases and boundary conditions
- Verify error messages are helpful
- Ensure rules don't conflict with each other

## Error Codes

### Schematron Validation Errors

| Code | Description | Example |
|------|-------------|---------|
| `SCHEMATRON:RULE_FAILURE` | Business rule validation failed | Invalid charge classification |
| `SCHEMATRON:NO_RULES_LOADED` | No rules available | Rules file not found |
| `SCHEMATRON:RULES_PARSE_ERROR` | Rules parsing failed | Invalid Schematron syntax |
| `SCHEMATRON:XML_PARSE_ERROR` | XML parsing failed | Malformed XML |
| `SCHEMATRON:VALIDATION_ERROR` | Validation process failed | Unexpected error |

## Best Practices

### 1. Rule Organization
- Group related rules in patterns
- Use descriptive pattern titles
- Keep rules focused and specific

### 2. Error Messages
- Be specific about what's wrong
- Include the actual value when helpful
- Provide guidance on how to fix

### 3. Performance
- Use efficient XPath expressions
- Avoid complex nested conditions
- Test with large XML files

### 4. Maintenance
- Document rule purpose and logic
- Include test cases
- Update documentation when rules change

## Troubleshooting

### Common Issues

1. **XPath Errors**: Check XPath syntax and element names
2. **Namespace Issues**: Ensure correct namespace declarations
3. **Rule Conflicts**: Check for overlapping or conflicting rules
4. **Performance**: Optimize XPath expressions for large files

### Debug Tips

1. **Test Incrementally**: Add one rule at a time
2. **Use Simple XPath**: Start with basic expressions
3. **Check Context**: Ensure rule context is correct
4. **Validate Syntax**: Use XML tools to check Schematron syntax

## Related Documentation

- [Validating with XSD](validating-with-xsd.md) - XSD schema validation
- [API Reference](api/rest.md) - Complete API documentation
- [CLI Reference](api/cli.md) - Command-line interface
- [Error Codes](error-codes.md) - Complete error code reference
