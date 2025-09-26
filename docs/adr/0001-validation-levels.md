# ADR-0001: Validation Levels Architecture

**Date**: 2024-01-15  
**Status**: Accepted  
**Deciders**: Core Maintainers  

## Context

The MITS Validator needs to support multiple types of validation with different requirements:

1. **XML Well-Formedness**: Basic XML syntax validation
2. **Schema Conformance**: XSD schema validation
3. **Business Rules**: Schematron rule validation
4. **Semantic Consistency**: Cross-field validation using catalogs

Each validation type has different:
- Execution requirements (some need schemas, others need rules)
- Error handling (some are critical, others are warnings)
- Performance characteristics (some are fast, others are slow)
- Dependencies (some need external resources, others don't)

## Decision

We will implement a **layered validation architecture** with the following characteristics:

### 1. Validation Levels Registry

A centralized registry that manages validation levels with:
- **Ordered execution**: Levels run in a specific sequence
- **Failure isolation**: Level failures don't crash the entire process
- **Conditional execution**: Levels can be enabled/disabled based on available resources
- **Result aggregation**: Results from all levels are combined

### 2. Validation Level Interface

All validation levels implement a common interface:

```python
class ValidationLevelProtocol:
    def validate(self, content: bytes) -> ValidationResult:
        """Validate content and return results."""
        pass
    
    def get_name(self) -> str:
        """Get the name of this validation level."""
        pass
```

### 3. Execution Order

Levels execute in this order:
1. **WellFormed** - Always executed (foundation)
2. **XSD** - Executed if schemas are available
3. **Schematron** - Executed if rules are available
4. **Semantic** - Executed if catalogs are available

### 4. Error Handling Strategy

- **Level Isolation**: Each level can fail independently
- **Error Aggregation**: All errors are collected and reported
- **Graceful Degradation**: Missing resources emit warnings, not errors
- **Consistent Error Format**: All errors follow the same structure

## Rationale

### Why Layered Architecture?

1. **Separation of Concerns**: Each level has a single responsibility
2. **Extensibility**: New levels can be added without modifying existing code
3. **Maintainability**: Each level can be developed and tested independently
4. **Flexibility**: Levels can be enabled/disabled based on available resources

### Why Ordered Execution?

1. **Dependency Management**: Later levels depend on earlier levels
2. **Performance**: Fast levels run first, slow levels run last
3. **Error Reporting**: Early failures provide immediate feedback
4. **Resource Efficiency**: Unnecessary levels are skipped if earlier levels fail

### Why Failure Isolation?

1. **Reliability**: Single level failures don't crash the entire process
2. **Comprehensive Reporting**: All issues are reported, not just the first failure
3. **Debugging**: Developers can see all validation issues at once
4. **User Experience**: Users get complete feedback on their data

### Why Conditional Execution?

1. **Resource Availability**: Not all resources (schemas, rules, catalogs) are always available
2. **Performance**: Skip expensive operations when resources are missing
3. **Flexibility**: Different deployments can have different capabilities
4. **Graceful Degradation**: System works even with missing resources

## Implementation Details

### Validation Engine

```python
class ValidationEngine:
    def __init__(self, rules_dir: Path, version: str):
        self._levels = {}
        self._register_levels()
    
    def validate(self, content: bytes, levels: list[str] = None) -> ValidationResult:
        results = []
        for level_name in self._get_enabled_levels(levels):
            try:
                result = self._levels[level_name].validate(content)
                results.append(result)
            except Exception as e:
                # Capture level failure as finding
                results.append(self._create_failure_result(level_name, e))
        return self._aggregate_results(results)
```

### Level Registration

```python
def _register_levels(self):
    self._levels["WellFormed"] = WellFormedValidator()
    self._levels["XSD"] = XSDValidator(self._xsd_schema_path)
    self._levels["Schematron"] = SchematronValidator(self._schematron_rules_path)
    self._levels["Semantic"] = SemanticValidator(self._catalog_loader)
```

### Error Handling

```python
def _create_failure_result(self, level_name: str, error: Exception) -> ValidationResult:
    return ValidationResult(
        level=level_name,
        findings=[Finding(
            level=FindingLevel.ERROR,
            code="ENGINE:LEVEL_CRASH",
            message=f"Validation level {level_name} crashed: {error}",
            rule_ref=f"internal://{level_name}"
        )],
        duration_ms=0
    )
```

## Consequences

### Positive

1. **Extensibility**: New validation levels can be added easily
2. **Maintainability**: Each level is independent and testable
3. **Reliability**: System continues working even with level failures
4. **Flexibility**: Different deployments can have different capabilities
5. **Performance**: Fast levels run first, slow levels run last

### Negative

1. **Complexity**: More complex than a single validation function
2. **Memory Usage**: Multiple level instances and result objects
3. **Debugging**: More complex error handling and result aggregation
4. **Testing**: More test cases needed for level interactions

### Mitigations

1. **Documentation**: Comprehensive documentation of the architecture
2. **Testing**: Extensive test coverage for all level interactions
3. **Monitoring**: Structured logging and metrics for debugging
4. **Examples**: Clear examples of how to add new levels

## Alternatives Considered

### 1. Single Validation Function

**Rejected because**:
- Not extensible for new validation types
- Difficult to maintain as requirements grow
- No separation of concerns
- Hard to test individual validation logic

### 2. Pipeline Architecture

**Rejected because**:
- Too rigid for different validation requirements
- Difficult to handle conditional execution
- Complex error handling across pipeline stages
- Not suitable for different resource dependencies

### 3. Plugin Architecture

**Rejected because**:
- Overkill for the current requirements
- Complex plugin loading and management
- Difficult to ensure execution order
- Too much abstraction for the use case

## Future Considerations

### Adding New Levels

1. Create new validator class implementing `ValidationLevelProtocol`
2. Add to the levels registry
3. Define error codes in the error catalog
4. Add tests for the new level
5. Update documentation

### Adding New MITS Versions

1. Create versioned resource directory
2. Add version-specific schemas and rules
3. Update catalog loader to support new version
4. Add version validation logic
5. Update documentation

### Performance Optimization

1. Parallel execution for independent levels
2. Caching for expensive operations
3. Streaming for large content
4. Resource pooling for external dependencies

## References

- [MITS Specification](https://www.mits.org/specification)
- [XML Schema Validation](https://www.w3.org/XML/Schema)
- [Schematron Rules](http://schematron.com/)
- [Architecture Decision Records](https://adr.github.io/)
