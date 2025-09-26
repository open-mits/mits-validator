# MITS 5.0 XSD Schemas

This directory contains the official MITS 5.0 Property Marketing / ILS XSD schemas.

## Schema Information

- **Retrieved**: September 2025
- **Source**: RETTC MITS 5.0 Approved Data Models (public)
- **Version**: 5.0
- **Namespace**: `http://www.mits.org/schema/PropertyMarketing/ILS/5.0`

## Files

### PropertyMarketing-ILS-5.0.xsd
- **SHA256**: `a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456`
- **Description**: Main MITS 5.0 Property Marketing / ILS schema
- **Root Element**: `PropertyMarketing`
- **Target Namespace**: `http://www.mits.org/schema/PropertyMarketing/ILS/5.0`

## Schema Structure

### Root Element
```xml
<PropertyMarketing version="5.0" timestamp="2025-09-15T10:30:00Z">
  <Property>...</Property>
  <Floorplan>...</Floorplan>
</PropertyMarketing>
```

### Key Elements
- **Property**: Community-level information
- **Floorplan**: Floor plan definitions
- **Unit**: Individual units within floor plans
- **ChargeOffer**: Fee structures and charges

### Charge Classification
The schema defines approved charge classifications:
- `Rent` - Monthly rent
- `Deposit` - Security deposits
- `Pet` - Pet-related fees
- `Parking` - Parking fees
- `Utilities` - Utility charges
- `Technology` - Technology fees
- `Admin` - Administrative fees
- `OtherMandatory` - Other mandatory charges

### Data Types
- **Currency**: `xs:decimal` with 2 fraction digits
- **Dates**: `xs:dateTime` for timestamps
- **Identifiers**: `xs:string` for IDs and names

## Usage

### Validation
```python
from mits_validator.validation.xsd import validate_xsd

result = validate_xsd("property-feed.xml")
if result.success:
    print("Valid MITS 5.0 feed")
else:
    for finding in result.findings:
        print(f"Error: {finding.message}")
```

### CLI
```bash
mits-validate validate --file property-feed.xml --mode=xsd
```

### API
```bash
curl -X POST -F "file=@property-feed.xml" \
  "http://localhost:8000/v1/validate?mode=xsd"
```

## Attribution

This schema is based on the RETTC MITS 5.0 Approved Data Models and is used under the terms of the MITS specification license.
