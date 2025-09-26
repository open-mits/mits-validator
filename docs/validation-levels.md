# Validation Levels

The MITS Validator uses a modular architecture with multiple validation levels that can be executed independently or in combination.

## Level Architecture

The validator executes levels in a specific order, with each level building upon the previous ones:

1. **WellFormed** - XML syntax and structure validation
2. **XSD** - Schema conformance validation (when schemas available)
3. **Schematron** - Business rules validation (when rules available)
4. **Semantic** - Cross-field consistency checks (future)

## Level Details

### WellFormed Level

**Purpose**: Validates that the input is well-formed XML.

**What it checks**:
- XML syntax correctness
- Proper element nesting
- Valid character encoding
- Basic XML structure

**Error codes**: `WELLFORMED:*`
- `WELLFORMED:PARSE_ERROR` - XML parsing failed
- `WELLFORMED:UNEXPECTED_ERROR` - Unexpected parsing error

**Always executed**: Yes (this is the foundation level)

### XSD Level

**Purpose**: Validates XML structure against MITS schemas.

**What it checks**:
- Element structure conformance
- Attribute validation
- Data type validation
- Schema compliance

**Error codes**: `XSD:*`
- `XSD:VALIDATION_ERROR` - Schema validation failed
- `XSD:SCHEMA_MISSING` - No schema available (warning)

**Execution**: Only if XSD schemas are available in `rules/xsd/`

### Schematron Level

**Purpose**: Validates business rules and cross-field constraints.

**What it checks**:
- Business logic rules
- Cross-field relationships
- Data consistency
- Custom validation rules

**Error codes**: `SCHEMATRON:*`
- `SCHEMATRON:RULE_FAILURE` - Business rule failed
- `SCHEMATRON:NO_RULES_LOADED` - No rules available (info)

**Execution**: Only if Schematron rules are available in `rules/schematron/`

### Semantic Level (Future)

**Purpose**: Validates semantic consistency and data quality.

**What it will check**:
- Data consistency across fields
- Business logic validation
- Data quality metrics
- Advanced constraints

**Error codes**: `SEMANTIC:*` (to be defined)

## Level Isolation

Each validation level is isolated to prevent cascading failures:

- **Level failures don't crash the validator** - If one level fails, others continue
- **Findings are captured** - Level failures are recorded as findings
- **Execution continues** - The registry continues with remaining levels
- **Error codes are standardized** - All level failures use `ENGINE:LEVEL_CRASH`

## Registry System

The validator uses a registry system to manage and execute validation levels:

```python
from mits_validator.validation import ValidationEngine

# Create engine with default levels
engine = ValidationEngine()

# Execute validation
results = engine.validate(content, profile="default")
```

### Registry Features

- **Ordered execution** - Levels run in a specific sequence
- **Failure isolation** - One level's failure doesn't affect others
- **Findings aggregation** - All findings are collected and reported
- **Timing tracking** - Each level's execution time is recorded
- **Metadata collection** - Registry tracks what levels were executed

## Configuration

Validation levels can be configured through profiles:

### Default Profile
```json
{
  "name": "default",
  "levels": ["WellFormed", "XSD", "Schematron"],
  "size_limit_mb": 10,
  "timeout_seconds": 30
}
```

### PMS Profile
```json
{
  "name": "pms",
  "levels": ["WellFormed", "XSD"],
  "size_limit_mb": 5,
  "timeout_seconds": 15
}
```

## Adding New Levels

To add a new validation level:

1. **Create the level module** in `src/mits_validator/levels/`
2. **Implement the interface**:
   ```python
   class MyLevel(ValidationLevel):
       def validate(self, content: bytes) -> ValidationResult:
           # Implementation
   ```
3. **Register the level** in the validation engine
4. **Add error codes** to the central error catalog
5. **Write tests** for the new level
6. **Update documentation**

## Best Practices

- **Fail gracefully** - Never crash the validator
- **Use standard error codes** - Follow the `CATEGORY:SUBCODE` format
- **Provide clear messages** - Human-readable error descriptions
- **Include location info** - Line, column, xpath when possible
- **Test thoroughly** - Cover success and failure cases
- **Document behavior** - Clear documentation of what the level checks
