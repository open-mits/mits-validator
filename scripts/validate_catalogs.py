#!/usr/bin/env python3
"""Validate MITS 5.0 catalogs against their schemas and check for uniqueness."""

import json
import sys
from pathlib import Path

import jsonschema
from jsonschema import Draft202012Validator


def validate_catalog_file(file_path: Path, schema_path: Path | None = None) -> list[str]:
    """Validate a single catalog file against its schema."""
    errors = []
    
    try:
        with open(file_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"Invalid JSON in {file_path}: {e}"]
    
    if schema_path and schema_path.exists():
        try:
            with open(schema_path) as f:
                schema = json.load(f)
            validator = Draft202012Validator(schema)
            validator.validate(data)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation failed for {file_path}: {e}")
        except Exception as e:
            errors.append(f"Error loading schema {schema_path}: {e}")
    
    return errors


def check_unique_codes(file_path: Path) -> list[str]:
    """Check for unique codes within a catalog file."""
    errors = []
    
    try:
        with open(file_path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return errors  # Skip if file doesn't exist or is invalid
    
    if not isinstance(data, list):
        return errors  # Skip non-array files
    
    codes_seen: set[str] = set()
    for i, entry in enumerate(data):
        if not isinstance(entry, dict) or "code" not in entry:
            continue
        
        code = entry["code"]
        if code in codes_seen:
            errors.append(f"Duplicate code '{code}' in {file_path} (entry {i+1})")
        codes_seen.add(code)
    
    return errors


def validate_all_catalogs(rules_dir: Path = Path("rules")) -> bool:
    """Validate all catalogs in the rules directory."""
    errors: list[str] = []
    
    # Find all version directories
    version_dirs = [d for d in rules_dir.iterdir() if d.is_dir() and d.name.startswith("mits-")]
    
    if not version_dirs:
        print("No MITS version directories found in rules/")
        return True
    
    for version_dir in version_dirs:
        print(f"Validating catalogs in {version_dir.name}...")
        
        catalogs_dir = version_dir / "catalogs"
        schemas_dir = version_dir / "schemas"
        
        if not catalogs_dir.exists():
            print(f"  Warning: No catalogs directory in {version_dir.name}")
            continue
        
        # Validate charge classes
        charge_classes_file = catalogs_dir / "charge-classes.json"
        if charge_classes_file.exists():
            schema_file = schemas_dir / "charge-classes.schema.json"
            file_errors = validate_catalog_file(charge_classes_file, schema_file)
            errors.extend(file_errors)
            
            # Check for unique codes
            code_errors = check_unique_codes(charge_classes_file)
            errors.extend(code_errors)
        
        # Validate enums
        enums_dir = catalogs_dir / "enums"
        if enums_dir.exists():
            enum_schema_file = schemas_dir / "enum.schema.json"
            
            for enum_file in enums_dir.glob("*.json"):
                file_errors = validate_catalog_file(enum_file, enum_schema_file)
                errors.extend(file_errors)
                
                # Check for unique codes
                code_errors = check_unique_codes(enum_file)
                errors.extend(code_errors)
        
        # Validate item specializations
        specializations_dir = catalogs_dir / "item-specializations"
        if specializations_dir.exists():
            for spec_file in specializations_dir.glob("*.json"):
                spec_name = spec_file.stem
                schema_file = schemas_dir / f"{spec_name}.schema.json"
                file_errors = validate_catalog_file(spec_file, schema_file)
                errors.extend(file_errors)
    
    # Report results
    if errors:
        print(f"\nFound {len(errors)} validation errors:")
        for error in errors:
            print(f"  ❌ {error}")
        return False
    else:
        print("\n✅ All catalogs validated successfully!")
        return True


def main() -> int:
    """Main entry point."""
    rules_dir = Path("rules")
    
    if not rules_dir.exists():
        print("Error: rules/ directory not found")
        return 1
    
    success = validate_all_catalogs(rules_dir)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
