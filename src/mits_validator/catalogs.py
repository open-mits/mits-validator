"""MITS 5.0 Catalog Loader and Registry.

This module provides a typed catalog loader that validates and exposes
MITS 5.0 catalogs for use in validation levels.
"""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import Draft202012Validator

from mits_validator.models import Finding, FindingLevel


class CatalogEntry:
    """Base class for catalog entries."""

    def __init__(self, data: dict[str, Any]) -> None:
        self.code: str = data["code"]
        self.name: str = data["name"]
        self.description: str | None = data.get("description")
        self.aliases: list[str] = data.get("aliases", [])
        self.notes: str | None = data.get("notes")


class ChargeClass(CatalogEntry):
    """Charge class catalog entry."""

    pass


class EnumEntry(CatalogEntry):
    """Enumeration catalog entry."""

    pass


class ItemSpecialization:
    """Item specialization entry."""

    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data


class CatalogRegistry:
    """Registry for loaded MITS 5.0 catalogs."""

    def __init__(self) -> None:
        self.charge_classes: dict[str, ChargeClass] = {}
        self.enums: dict[str, list[EnumEntry]] = {}
        self.specializations: dict[str, ItemSpecialization] = {}
        self.metadata: dict[str, Any] = {}


class CatalogLoader:
    """Loader for MITS 5.0 catalogs with validation."""

    def __init__(self, rules_dir: Path | None = None) -> None:
        self.rules_dir = rules_dir or Path("rules")
        self.registry = CatalogRegistry()

    def load_catalogs(self, version: str = "mits-5.0") -> tuple[CatalogRegistry, list[Finding]]:
        """Load and validate catalogs for the specified version."""
        findings: list[Finding] = []
        start_time = time.time()

        try:
            version_dir = self.rules_dir / version
            if not version_dir.exists():
                findings.append(
                    Finding(
                        level=FindingLevel.ERROR,
                        code="CATALOG:VERSION_NOT_FOUND",
                        message=f"MITS version {version} not found at {version_dir}",
                        rule_ref="internal://CatalogLoader",
                    )
                )
                return self.registry, findings

            # Load charge classes
            charge_classes_findings = self._load_charge_classes(version_dir)
            findings.extend(charge_classes_findings)

            # Load enums
            enums_findings = self._load_enums(version_dir)
            findings.extend(enums_findings)

            # Load item specializations
            specializations_findings = self._load_specializations(version_dir)
            findings.extend(specializations_findings)

            # Set metadata
            self.registry.metadata = {
                "catalog_version": version,
                "loaded_at": datetime.now(UTC).isoformat(),
                "rules_dir": str(self.rules_dir),
                "load_duration_ms": int((time.time() - start_time) * 1000),
            }

        except Exception as e:
            findings.append(
                Finding(
                    level=FindingLevel.ERROR,
                    code="ENGINE:LEVEL_CRASH",
                    message=f"Catalog loading crashed: {str(e)}",
                    rule_ref="internal://CatalogLoader",
                )
            )

        return self.registry, findings

    def _load_charge_classes(self, version_dir: Path) -> list[Finding]:
        """Load charge classes catalog."""
        findings: list[Finding] = []
        charge_classes_file = version_dir / "catalogs" / "charge-classes.json"
        schema_file = version_dir / "schemas" / "charge-classes.schema.json"

        try:
            if not charge_classes_file.exists():
                findings.append(
                    Finding(
                        level=FindingLevel.WARNING,
                        code="CATALOG:FILE_MISSING",
                        message=f"Charge classes file not found: {charge_classes_file}",
                        rule_ref="internal://CatalogLoader",
                    )
                )
                return findings

            # Load and validate against schema
            with open(charge_classes_file) as f:
                data = json.load(f)

            if schema_file.exists():
                with open(schema_file) as f:
                    schema = json.load(f)
                validator = Draft202012Validator(schema)
                validator.validate(data)

            # Load entries and check for duplicates
            codes_seen = set()
            for entry_data in data:
                if entry_data["code"] in codes_seen:
                    findings.append(
                        Finding(
                            level=FindingLevel.ERROR,
                            code="CATALOG:DUPLICATE_CODE",
                            message=f"Duplicate charge class code: {entry_data['code']}",
                            rule_ref="internal://CatalogLoader",
                        )
                    )
                    continue

                codes_seen.add(entry_data["code"])
                entry = ChargeClass(entry_data)
                self.registry.charge_classes[entry.code] = entry

        except json.JSONDecodeError as e:
            findings.append(
                Finding(
                    level=FindingLevel.ERROR,
                    code="CATALOG:INVALID_JSON",
                    message=f"Invalid JSON in charge classes file: {str(e)}",
                    rule_ref="internal://CatalogLoader",
                )
            )
        except jsonschema.ValidationError as e:
            findings.append(
                Finding(
                    level=FindingLevel.ERROR,
                    code="CATALOG:SCHEMA_VALIDATION_ERROR",
                    message=f"Charge classes schema validation failed: {str(e)}",
                    rule_ref="internal://CatalogLoader",
                )
            )
        except Exception as e:
            findings.append(
                Finding(
                    level=FindingLevel.ERROR,
                    code="ENGINE:LEVEL_CRASH",
                    message=f"Error loading charge classes: {str(e)}",
                    rule_ref="internal://CatalogLoader",
                )
            )

        return findings

    def _load_enums(self, version_dir: Path) -> list[Finding]:
        """Load enumeration catalogs."""
        findings: list[Finding] = []
        enums_dir = version_dir / "catalogs" / "enums"
        schema_file = version_dir / "schemas" / "enum.schema.json"

        if not enums_dir.exists():
            findings.append(
                Finding(
                    level=FindingLevel.WARNING,
                    code="CATALOG:DIRECTORY_MISSING",
                    message=f"Enums directory not found: {enums_dir}",
                    rule_ref="internal://CatalogLoader",
                )
            )
            return findings

        # Load schema if available
        schema = None
        if schema_file.exists():
            with open(schema_file) as f:
                schema = json.load(f)

        # Load each enum file
        for enum_file in enums_dir.glob("*.json"):
            enum_name = enum_file.stem
            try:
                with open(enum_file) as f:
                    data = json.load(f)

                # Validate against schema
                if schema:
                    validator = Draft202012Validator(schema)
                    validator.validate(data)

                # Load entries and check for duplicates
                codes_seen = set()
                entries = []
                for entry_data in data:
                    if entry_data["code"] in codes_seen:
                        findings.append(
                            Finding(
                                level=FindingLevel.ERROR,
                                code="CATALOG:DUPLICATE_CODE",
                                message=f"Duplicate enum code in {enum_name}: {entry_data['code']}",
                                rule_ref="internal://CatalogLoader",
                            )
                        )
                        continue

                    codes_seen.add(entry_data["code"])
                    entry = EnumEntry(entry_data)
                    entries.append(entry)

                self.registry.enums[enum_name] = entries

            except json.JSONDecodeError as e:
                findings.append(
                    Finding(
                        level=FindingLevel.ERROR,
                        code="CATALOG:INVALID_JSON",
                        message=f"Invalid JSON in {enum_name}: {str(e)}",
                        rule_ref="internal://CatalogLoader",
                    )
                )
            except jsonschema.ValidationError as e:
                findings.append(
                    Finding(
                        level=FindingLevel.ERROR,
                        code="CATALOG:SCHEMA_VALIDATION_ERROR",
                        message=f"Schema validation failed for {enum_name}: {str(e)}",
                        rule_ref="internal://CatalogLoader",
                    )
                )
            except Exception as e:
                findings.append(
                    Finding(
                        level=FindingLevel.ERROR,
                        code="ENGINE:LEVEL_CRASH",
                        message=f"Error loading enum {enum_name}: {str(e)}",
                        rule_ref="internal://CatalogLoader",
                    )
                )

        return findings

    def _load_specializations(self, version_dir: Path) -> list[Finding]:
        """Load item specialization catalogs."""
        findings: list[Finding] = []
        specializations_dir = version_dir / "catalogs" / "item-specializations"

        if not specializations_dir.exists():
            findings.append(
                Finding(
                    level=FindingLevel.WARNING,
                    code="CATALOG:DIRECTORY_MISSING",
                    message=f"Item specializations directory not found: {specializations_dir}",
                    rule_ref="internal://CatalogLoader",
                )
            )
            return findings

        # Load each specialization file
        for spec_file in specializations_dir.glob("*.json"):
            spec_name = spec_file.stem
            schema_file = version_dir / "schemas" / f"{spec_name}.schema.json"

            try:
                with open(spec_file) as f:
                    data = json.load(f)

                # Validate against schema if available
                if schema_file.exists():
                    with open(schema_file) as f:
                        schema = json.load(f)
                    validator = Draft202012Validator(schema)
                    validator.validate(data)

                entry = ItemSpecialization(data)
                self.registry.specializations[spec_name] = entry

            except json.JSONDecodeError as e:
                findings.append(
                    Finding(
                        level=FindingLevel.ERROR,
                        code="CATALOG:INVALID_JSON",
                        message=f"Invalid JSON in {spec_name}: {str(e)}",
                        rule_ref="internal://CatalogLoader",
                    )
                )
            except jsonschema.ValidationError as e:
                findings.append(
                    Finding(
                        level=FindingLevel.ERROR,
                        code="CATALOG:SCHEMA_VALIDATION_ERROR",
                        message=f"Schema validation failed for {spec_name}: {str(e)}",
                        rule_ref="internal://CatalogLoader",
                    )
                )
            except Exception as e:
                findings.append(
                    Finding(
                        level=FindingLevel.ERROR,
                        code="ENGINE:LEVEL_CRASH",
                        message=f"Error loading specialization {spec_name}: {str(e)}",
                        rule_ref="internal://CatalogLoader",
                    )
                )

        return findings


def get_catalog_loader(rules_dir: Path | None = None) -> CatalogLoader:
    """Get a catalog loader instance."""
    return CatalogLoader(rules_dir)
