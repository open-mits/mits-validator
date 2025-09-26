#!/usr/bin/env python3
"""Validate MITS catalog files against their JSON schemas."""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

import jsonschema
from jsonschema import Draft202012Validator


def validate_catalogs() -> int:
    """Validate all catalog files against their schemas."""
    rules_dir = Path("rules")
    if not rules_dir.exists():
        print("❌ Rules directory not found")
        return 1

    errors = 0
    schemas_dir = rules_dir / "mits-5.0" / "schemas"
    catalogs_dir = rules_dir / "mits-5.0" / "catalogs"

    # Load schemas
    schemas: Dict[str, Dict[str, Any]] = {}
    for schema_file in schemas_dir.glob("*.schema.json"):
        try:
            with open(schema_file) as f:
                schemas[schema_file.stem] = json.load(f)
                print(f"📋 Loaded schema: {schema_file.stem}")
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"❌ Failed to load schema {schema_file}: {e}")
            errors += 1

    # Validate charge classes
    charge_classes_file = catalogs_dir / "charge-classes.json"
    if charge_classes_file.exists():
        errors += validate_file_against_schema(
            charge_classes_file, schemas.get("charge-classes.schema"), "charge-classes"
        )

    # Validate enums
    enums_dir = catalogs_dir / "enums"
    if enums_dir.exists():
        for enum_file in enums_dir.glob("*.json"):
            errors += validate_file_against_schema(
                enum_file, schemas.get("enum.schema"), f"enum/{enum_file.name}"
            )

    # Validate specializations
    specializations_dir = catalogs_dir / "item-specializations"
    if specializations_dir.exists():
        for spec_file in specializations_dir.glob("*.json"):
            schema_name = f"{spec_file.stem}.schema"
            errors += validate_file_against_schema(
                spec_file, schemas.get(schema_name), f"specialization/{spec_file.name}"
            )

    if errors == 0:
        print("✅ All catalog files are valid")
    else:
        print(f"❌ Found {errors} validation errors")

    return errors


def validate_file_against_schema(
    file_path: Path, schema: Dict[str, Any] | None, file_type: str
) -> int:
    """Validate a single file against its schema."""
    if not schema:
        print(f"⚠️  No schema found for {file_type}")
        return 0

    try:
        with open(file_path) as f:
            data = json.load(f)

        # Validate against schema
        Draft202012Validator(schema).validate(data)

        # Check for duplicate codes
        if isinstance(data, list):
            codes: Set[str] = set()
            for item in data:
                if "code" in item:
                    if item["code"] in codes:
                        print(f"❌ Duplicate code '{item['code']}' in {file_type}")
                        return 1
                    codes.add(item["code"])

        print(f"✅ {file_type} is valid")
        return 0

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {file_type}: {e}")
        return 1
    except jsonschema.ValidationError as e:
        print(f"❌ Schema validation failed for {file_type}: {e.message}")
        return 1
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return 1


if __name__ == "__main__":
    sys.exit(validate_catalogs())