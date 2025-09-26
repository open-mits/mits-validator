"""Catalog loader for MITS versioned catalogs."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import Draft202012Validator

from mits_validator.models import Finding, FindingLevel


class CatalogEntry:
    """Base catalog entry with common fields."""

    def __init__(self, data: dict[str, Any]) -> None:
        self.code = data["code"]
        self.name = data["name"]
        self.description = data.get("description", "")
        self.aliases = data.get("aliases", [])
        self.notes = data.get("notes", "")


class ChargeClass(CatalogEntry):
    """Charge class entry."""

    pass


class EnumEntry(CatalogEntry):
    """Enumeration entry."""

    pass


class ItemSpecialization(CatalogEntry):
    """Item specialization entry with type-specific fields."""

    def __init__(self, data: dict[str, Any]) -> None:
        super().__init__(data)
        # Type-specific fields will be validated by schema
        self._raw_data = data

    def __getattr__(self, name: str) -> Any:
        """Allow access to type-specific fields."""
        return self._raw_data.get(name)


class CatalogRegistry:
    """Registry of loaded catalogs."""

    def __init__(self) -> None:
        self.charge_classes: dict[str, ChargeClass] = {}
        self.enums: dict[str, dict[str, EnumEntry]] = {}
        self.specializations: dict[str, ItemSpecialization] = {}
        self.metadata: dict[str, Any] = {
            "catalog_version": None,
            "loaded_at": None,
        }


class CatalogLoader:
    """Loads and validates MITS catalogs."""

    def __init__(self, base_path: Path | None = None) -> None:
        self.base_path = base_path or Path("rules")
        self.schemas: dict[str, dict[str, Any]] = {}

    def load_catalogs(self, version: str = "mits-5.0") -> tuple[CatalogRegistry, list[Finding]]:
        """Load catalogs for the specified version."""
        findings: list[Finding] = []
        registry = CatalogRegistry()
        registry.metadata["catalog_version"] = version
        registry.metadata["loaded_at"] = datetime.now(timezone.utc).isoformat()

        version_path = self.base_path / version

        # Load charge classes
        charge_classes_findings = self._load_charge_classes(version_path, registry)
        findings.extend(charge_classes_findings)

        # Load enums
        enums_findings = self._load_enums(version_path, registry)
        findings.extend(enums_findings)

        # Load specializations
        specializations_findings = self._load_specializations(version_path, registry)
        findings.extend(specializations_findings)

        return registry, findings

    def _load_charge_classes(self, version_path: Path, registry: CatalogRegistry) -> list[Finding]:
        """Load charge classes catalog."""
        findings: list[Finding] = []
        charge_classes_path = version_path / "catalogs" / "charge-classes.json"

        try:
            if not charge_classes_path.exists():
                findings.append(
                    Finding(
                        level=FindingLevel.WARNING,
                        code="CATALOG:FILE_MISSING",
                        message=f"Charge classes file not found: {charge_classes_path}",
                        rule_ref="internal://Catalog",
                    )
                )
                return findings

            with open(charge_classes_path) as f:
                data = json.load(f)

            # Validate against schema
            schema = self._get_schema("charge-classes")
            if schema:
                try:
                    Draft202012Validator(schema).validate(data)
                except jsonschema.ValidationError as e:
                    findings.append(
                        Finding(
                            level=FindingLevel.ERROR,
                            code="CATALOG:SCHEMA_VALIDATION_ERROR",
                            message=f"Charge classes schema validation failed: {e.message}",
                            rule_ref="internal://Catalog",
                        )
                    )
                    return findings

            # Load entries
            codes = set()
            for entry_data in data:
                if entry_data["code"] in codes:
                    findings.append(
                        Finding(
                            level=FindingLevel.ERROR,
                            code="CATALOG:DUPLICATE_CODE",
                            message=f"Duplicate charge class code: {entry_data['code']}",
                            rule_ref="internal://Catalog",
                        )
                    )
                    continue

                codes.add(entry_data["code"])
                registry.charge_classes[entry_data["code"]] = ChargeClass(entry_data)

        except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
            findings.append(
                Finding(
                    level=FindingLevel.ERROR,
                    code="CATALOG:INVALID_JSON",
                    message=f"Failed to load charge classes: {e}",
                    rule_ref="internal://Catalog",
                )
            )

        return findings

    def _load_enums(self, version_path: Path, registry: CatalogRegistry) -> list[Finding]:
        """Load enumeration catalogs."""
        findings: list[Finding] = []
        enums_path = version_path / "catalogs" / "enums"

        if not enums_path.exists():
            findings.append(
                Finding(
                    level=FindingLevel.WARNING,
                    code="CATALOG:DIRECTORY_MISSING",
                    message=f"Enums directory not found: {enums_path}",
                    rule_ref="internal://Catalog",
                )
            )
            return findings

        enum_files = list(enums_path.glob("*.json"))
        if not enum_files:
            findings.append(
                Finding(
                    level=FindingLevel.INFO,
                    code="CATALOG:NO_ENUMS",
                    message=f"No enum files found in: {enums_path}",
                    rule_ref="internal://Catalog",
                )
            )
            return findings

        for enum_file in enum_files:
            enum_name = enum_file.stem
            enum_findings = self._load_single_enum(enum_file, enum_name, registry)
            findings.extend(enum_findings)

        return findings

    def _load_single_enum(self, enum_file: Path, enum_name: str, registry: CatalogRegistry) -> list[Finding]:
        """Load a single enum file."""
        findings: list[Finding] = []

        try:
            with open(enum_file) as f:
                data = json.load(f)

            # Validate against enum schema
            schema = self._get_schema("enum")
            if schema:
                try:
                    Draft202012Validator(schema).validate(data)
                except jsonschema.ValidationError as e:
                    findings.append(
                        Finding(
                            level=FindingLevel.ERROR,
                            code="CATALOG:SCHEMA_VALIDATION_ERROR",
                            message=f"Enum {enum_name} schema validation failed: {e.message}",
                            rule_ref="internal://Catalog",
                        )
                    )
                    return findings

            # Load entries
            registry.enums[enum_name] = {}
            codes = set()
            for entry_data in data:
                if entry_data["code"] in codes:
                    findings.append(
                        Finding(
                            level=FindingLevel.ERROR,
                            code="CATALOG:DUPLICATE_CODE",
                            message=f"Duplicate enum code in {enum_name}: {entry_data['code']}",
                            rule_ref="internal://Catalog",
                        )
                    )
                    continue

                codes.add(entry_data["code"])
                registry.enums[enum_name][entry_data["code"]] = EnumEntry(entry_data)

        except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
            findings.append(
                Finding(
                    level=FindingLevel.ERROR,
                    code="CATALOG:INVALID_JSON",
                    message=f"Failed to load enum {enum_name}: {e}",
                    rule_ref="internal://Catalog",
                )
            )

        return findings

    def _load_specializations(self, version_path: Path, registry: CatalogRegistry) -> list[Finding]:
        """Load item specialization catalogs."""
        findings: list[Finding] = []
        specializations_path = version_path / "catalogs" / "item-specializations"

        if not specializations_path.exists():
            findings.append(
                Finding(
                    level=FindingLevel.WARNING,
                    code="CATALOG:DIRECTORY_MISSING",
                    message=f"Specializations directory not found: {specializations_path}",
                    rule_ref="internal://Catalog",
                )
            )
            return findings

        specialization_files = list(specializations_path.glob("*.json"))
        if not specialization_files:
            findings.append(
                Finding(
                    level=FindingLevel.INFO,
                    code="CATALOG:NO_SPECIALIZATIONS",
                    message=f"No specialization files found in: {specializations_path}",
                    rule_ref="internal://Catalog",
                )
            )
            return findings

        for spec_file in specialization_files:
            spec_name = spec_file.stem
            spec_findings = self._load_single_specialization(spec_file, spec_name, registry)
            findings.extend(spec_findings)

        return findings

    def _load_single_specialization(
        self, spec_file: Path, spec_name: str, registry: CatalogRegistry
    ) -> list[Finding]:
        """Load a single specialization file."""
        findings: list[Finding] = []

        try:
            with open(spec_file) as f:
                data = json.load(f)

            # Validate against appropriate schema
            schema = self._get_schema(spec_name)
            if schema:
                try:
                    Draft202012Validator(schema).validate(data)
                except jsonschema.ValidationError as e:
                    findings.append(
                        Finding(
                            level=FindingLevel.ERROR,
                            code="CATALOG:SCHEMA_VALIDATION_ERROR",
                            message=f"Specialization {spec_name} schema validation failed: {e.message}",
                            rule_ref="internal://Catalog",
                        )
                    )
                    return findings

            # Load entry
            registry.specializations[spec_name] = ItemSpecialization(data)

        except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
            findings.append(
                Finding(
                    level=FindingLevel.ERROR,
                    code="CATALOG:INVALID_JSON",
                    message=f"Failed to load specialization {spec_name}: {e}",
                    rule_ref="internal://Catalog",
                )
            )

        return findings

    def _get_schema(self, schema_name: str) -> dict[str, Any] | None:
        """Get schema by name, loading if necessary."""
        if schema_name not in self.schemas:
            schema_path = self.base_path / "mits-5.0" / "schemas" / f"{schema_name}.schema.json"
            try:
                if schema_path.exists():
                    with open(schema_path) as f:
                        self.schemas[schema_name] = json.load(f)
                else:
                    return None
            except (json.JSONDecodeError, FileNotFoundError):
                return None

        return self.schemas.get(schema_name)


# Global loader instance
_catalog_loader: CatalogLoader | None = None


def get_catalog_loader(base_path: Path | None = None) -> CatalogLoader:
    """Get a singleton instance of the CatalogLoader."""
    global _catalog_loader
    if _catalog_loader is None:
        _catalog_loader = CatalogLoader(base_path)
    return _catalog_loader
