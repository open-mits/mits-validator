"""Tests for catalog loader functionality."""

import json
from pathlib import Path

from mits_validator.catalog_loader import CatalogLoader, CatalogRegistry
from mits_validator.models import FindingLevel


class TestCatalogLoader:
    """Test catalog loader functionality."""

    def test_load_catalogs_success(self, tmp_path: Path) -> None:
        """Test successful catalog loading."""
        # Create test catalog structure
        rules_dir = tmp_path / "rules"
        version_dir = rules_dir / "mits-5.0"
        catalogs_dir = version_dir / "catalogs"
        enums_dir = catalogs_dir / "enums"
        specializations_dir = catalogs_dir / "item-specializations"
        schemas_dir = version_dir / "schemas"

        # Create directories
        enums_dir.mkdir(parents=True)
        specializations_dir.mkdir(parents=True)
        schemas_dir.mkdir(parents=True)

        # Create charge classes
        charge_classes_data = [{"code": "RENT", "name": "Rent", "description": "Monthly rent"}]
        with open(catalogs_dir / "charge-classes.json", "w") as f:
            json.dump(charge_classes_data, f)

        # Create enum
        enum_data = [{"code": "REQUIRED", "name": "Required", "description": "Mandatory charge"}]
        with open(enums_dir / "charge-requirement.json", "w") as f:
            json.dump(enum_data, f)

        # Create specialization
        specialization_data = {
            "code": "PARKING_SPACE",
            "name": "Parking Space",
            "structure_types": ["SURFACE", "GARAGE"],
            "size_types": ["COMPACT", "STANDARD"],
            "availability": "BOTH",
            "units_of_measure": ["HOUR", "DAY"],
        }
        with open(specializations_dir / "parking.json", "w") as f:
            json.dump(specialization_data, f)

        # Create schemas
        enum_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"code": {"type": "string"}, "name": {"type": "string"}},
                "required": ["code", "name"],
            },
        }
        with open(schemas_dir / "enum.schema.json", "w") as f:
            json.dump(enum_schema, f)

        charge_classes_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"code": {"type": "string"}, "name": {"type": "string"}},
                "required": ["code", "name"],
            },
        }
        with open(schemas_dir / "charge-classes.schema.json", "w") as f:
            json.dump(charge_classes_schema, f)

        parking_schema = {
            "type": "object",
            "properties": {
                "code": {"type": "string"},
                "name": {"type": "string"},
                "structure_types": {"type": "array"},
                "size_types": {"type": "array"},
                "availability": {"type": "string"},
                "units_of_measure": {"type": "array"},
            },
            "required": [
                "code",
                "name",
                "structure_types",
                "size_types",
                "availability",
                "units_of_measure",
            ],
        }
        with open(schemas_dir / "parking.schema.json", "w") as f:
            json.dump(parking_schema, f)

        # Load catalogs
        loader = CatalogLoader(rules_dir)
        registry, findings = loader.load_catalogs("mits-5.0")

        # Verify registry
        assert isinstance(registry, CatalogRegistry)
        assert registry.metadata["catalog_version"] == "mits-5.0"
        assert "loaded_at" in registry.metadata

        # Verify charge classes
        assert len(registry.charge_classes) == 1
        assert "RENT" in registry.charge_classes
        assert registry.charge_classes["RENT"].name == "Rent"

        # Verify enums
        assert len(registry.enums) == 1
        assert "charge-requirement" in registry.enums
        assert len(registry.enums["charge-requirement"]) == 1
        assert "REQUIRED" in registry.enums["charge-requirement"]

        # Verify specializations
        assert len(registry.specializations) == 1
        assert "parking" in registry.specializations
        assert registry.specializations["parking"].code == "PARKING_SPACE"

        # Should have no error findings
        error_findings = [f for f in findings if f.level == FindingLevel.ERROR]
        assert len(error_findings) == 0

    def test_load_catalogs_missing_files(self, tmp_path: Path) -> None:
        """Test catalog loading with missing files."""
        rules_dir = tmp_path / "rules"
        version_dir = rules_dir / "mits-5.0"
        catalogs_dir = version_dir / "catalogs"
        catalogs_dir.mkdir(parents=True)

        # Create only schemas directory
        schemas_dir = version_dir / "schemas"
        schemas_dir.mkdir(parents=True)

        # Load catalogs
        loader = CatalogLoader(rules_dir)
        registry, findings = loader.load_catalogs("mits-5.0")

        # Should have warning findings for missing files
        warning_findings = [f for f in findings if f.level == FindingLevel.WARNING]
        assert len(warning_findings) > 0

        # Should have warning findings for missing directories
        warning_findings = [f for f in findings if f.level == FindingLevel.WARNING]
        assert len(warning_findings) > 0

    def test_load_catalogs_invalid_json(self, tmp_path: Path) -> None:
        """Test catalog loading with invalid JSON."""
        rules_dir = tmp_path / "rules"
        version_dir = rules_dir / "mits-5.0"
        catalogs_dir = version_dir / "catalogs"
        catalogs_dir.mkdir(parents=True)

        # Create invalid JSON file
        with open(catalogs_dir / "charge-classes.json", "w") as f:
            f.write("invalid json content")

        # Load catalogs
        loader = CatalogLoader(rules_dir)
        registry, findings = loader.load_catalogs("mits-5.0")

        # Should have error findings for invalid JSON
        error_findings = [f for f in findings if f.level == FindingLevel.ERROR]
        assert len(error_findings) > 0
        assert any("CATALOG:INVALID_JSON" in f.code for f in error_findings)

    def test_load_catalogs_duplicate_codes(self, tmp_path: Path) -> None:
        """Test catalog loading with duplicate codes."""
        rules_dir = tmp_path / "rules"
        version_dir = rules_dir / "mits-5.0"
        catalogs_dir = version_dir / "catalogs"
        catalogs_dir.mkdir(parents=True)

        # Create charge classes with duplicate codes
        charge_classes_data = [
            {"code": "RENT", "name": "Rent"},
            {"code": "RENT", "name": "Rent Again"},  # Duplicate code
        ]
        with open(catalogs_dir / "charge-classes.json", "w") as f:
            json.dump(charge_classes_data, f)

        # Load catalogs
        loader = CatalogLoader(rules_dir)
        registry, findings = loader.load_catalogs("mits-5.0")

        # Should have error findings for duplicate codes
        error_findings = [f for f in findings if f.level == FindingLevel.ERROR]
        assert len(error_findings) > 0
        assert any("CATALOG:DUPLICATE_CODE" in f.code for f in error_findings)

    def test_load_catalogs_schema_validation_error(self, tmp_path: Path) -> None:
        """Test catalog loading with schema validation errors."""
        rules_dir = tmp_path / "rules"
        version_dir = rules_dir / "mits-5.0"
        catalogs_dir = version_dir / "catalogs"
        schemas_dir = version_dir / "schemas"
        catalogs_dir.mkdir(parents=True)
        schemas_dir.mkdir(parents=True)

        # Create invalid charge classes (missing required field)
        charge_classes_data = [
            {"code": "RENT"}  # Missing required 'name' field
        ]
        with open(catalogs_dir / "charge-classes.json", "w") as f:
            json.dump(charge_classes_data, f)

        # Create schema
        charge_classes_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"code": {"type": "string"}, "name": {"type": "string"}},
                "required": ["code", "name"],
            },
        }
        with open(schemas_dir / "charge-classes.schema.json", "w") as f:
            json.dump(charge_classes_schema, f)

        # Load catalogs
        loader = CatalogLoader(rules_dir)
        registry, findings = loader.load_catalogs("mits-5.0")

        # Should have error findings for schema validation
        error_findings = [f for f in findings if f.level == FindingLevel.ERROR]
        assert len(error_findings) > 0
        assert any("CATALOG:SCHEMA_VALIDATION_ERROR" in f.code for f in error_findings)

    def test_get_catalog_loader_singleton(self) -> None:
        """Test that get_catalog_loader returns a singleton."""
        from mits_validator.catalog_loader import get_catalog_loader

        loader1 = get_catalog_loader()
        loader2 = get_catalog_loader()

        assert loader1 is loader2

    def test_catalog_entry_properties(self) -> None:
        """Test catalog entry properties."""
        from mits_validator.catalog_loader import ChargeClass, EnumEntry, ItemSpecialization

        # Test ChargeClass
        charge_data = {
            "code": "RENT",
            "name": "Rent",
            "description": "Monthly rent",
            "aliases": ["MONTHLY_RENT"],
            "notes": "Primary charge",
        }
        charge = ChargeClass(charge_data)
        assert charge.code == "RENT"
        assert charge.name == "Rent"
        assert charge.description == "Monthly rent"
        assert charge.aliases == ["MONTHLY_RENT"]
        assert charge.notes == "Primary charge"

        # Test EnumEntry
        enum_data = {"code": "REQUIRED", "name": "Required", "description": "Mandatory charge"}
        enum_entry = EnumEntry(enum_data)
        assert enum_entry.code == "REQUIRED"
        assert enum_entry.name == "Required"
        assert enum_entry.description == "Mandatory charge"

        # Test ItemSpecialization
        spec_data = {
            "code": "PARKING_SPACE",
            "name": "Parking Space",
            "structure_types": ["SURFACE", "GARAGE"],
            "size_types": ["COMPACT", "STANDARD"],
            "availability": "BOTH",
            "units_of_measure": ["HOUR", "DAY"],
        }
        spec = ItemSpecialization(spec_data)
        assert spec.code == "PARKING_SPACE"
        assert spec.name == "Parking Space"
        assert spec.structure_types == ["SURFACE", "GARAGE"]
        assert spec.size_types == ["COMPACT", "STANDARD"]
        assert spec.availability == "BOTH"
        assert spec.units_of_measure == ["HOUR", "DAY"]
