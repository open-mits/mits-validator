"""Tests for MITS 5.0 catalog loader."""

import json
import tempfile
from pathlib import Path

from mits_validator.catalogs import CatalogLoader, CatalogRegistry, ChargeClass, EnumEntry
from mits_validator.models import FindingLevel


class TestCatalogLoader:
    """Test catalog loader functionality."""

    def test_load_valid_catalogs(self):
        """Test loading valid catalogs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_dir = Path(temp_dir) / "rules"
            rules_dir.mkdir()
            
            # Create version directory structure
            version_dir = rules_dir / "mits-5.0"
            catalogs_dir = version_dir / "catalogs"
            enums_dir = catalogs_dir / "enums"
            specializations_dir = catalogs_dir / "item-specializations"
            schemas_dir = version_dir / "schemas"
            
            for dir_path in [catalogs_dir, enums_dir, specializations_dir, schemas_dir]:
                dir_path.mkdir(parents=True)
            
            # Create charge classes
            charge_classes = [
                {"code": "PET", "name": "Pet Fee", "description": "Pet-related fees"},
                {"code": "PARKING", "name": "Parking Fee", "description": "Parking fees"}
            ]
            with open(catalogs_dir / "charge-classes.json", "w") as f:
                json.dump(charge_classes, f)
            
            # Create charge classes schema
            charge_schema = {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "pattern": "^[A-Z][A-Z0-9_]*$"},
                        "name": {"type": "string", "minLength": 1},
                        "description": {"type": "string"}
                    },
                    "required": ["code", "name"]
                }
            }
            with open(schemas_dir / "charge-classes.schema.json", "w") as f:
                json.dump(charge_schema, f)
            
            # Create enum
            enum_data = [
                {"code": "REQUIRED", "name": "Required", "description": "Mandatory"},
                {"code": "OPTIONAL", "name": "Optional", "description": "Optional"}
            ]
            with open(enums_dir / "charge-requirement.json", "w") as f:
                json.dump(enum_data, f)
            
            # Create enum schema
            enum_schema = {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "pattern": "^[A-Z][A-Z0-9_]*$"},
                        "name": {"type": "string", "minLength": 1},
                        "description": {"type": "string"}
                    },
                    "required": ["code", "name"]
                }
            }
            with open(schemas_dir / "enum.schema.json", "w") as f:
                json.dump(enum_schema, f)
            
            # Create specialization
            specialization_data = {
                "pet_type": "DOG",
                "size_category": "MEDIUM",
                "vaccination_required": True,
                "deposit_required": True
            }
            with open(specializations_dir / "pet.json", "w") as f:
                json.dump(specialization_data, f)
            
            # Create specialization schema
            pet_schema = {
                "type": "object",
                "properties": {
                    "pet_type": {"type": "string", "enum": ["DOG", "CAT", "BIRD"]},
                    "size_category": {"type": "string", "enum": ["SMALL", "MEDIUM", "LARGE"]},
                    "vaccination_required": {"type": "boolean"},
                    "deposit_required": {"type": "boolean"}
                },
                "required": [
                    "pet_type", "size_category", "vaccination_required", "deposit_required"
                ]
            }
            with open(schemas_dir / "pet.schema.json", "w") as f:
                json.dump(pet_schema, f)
            
            # Load catalogs
            loader = CatalogLoader(rules_dir)
            registry, findings = loader.load_catalogs("mits-5.0")
            
            # Verify no errors
            error_findings = [f for f in findings if f.level == FindingLevel.ERROR]
            assert len(error_findings) == 0, f"Unexpected errors: {error_findings}"
            
            # Verify charge classes loaded
            assert len(registry.charge_classes) == 2
            assert "PET" in registry.charge_classes
            assert "PARKING" in registry.charge_classes
            
            pet_class = registry.charge_classes["PET"]
            assert pet_class.code == "PET"
            assert pet_class.name == "Pet Fee"
            assert pet_class.description == "Pet-related fees"
            
            # Verify enums loaded
            assert "charge-requirement" in registry.enums
            assert len(registry.enums["charge-requirement"]) == 2
            
            # Verify specializations loaded
            assert "pet" in registry.specializations
            pet_spec = registry.specializations["pet"]
            assert pet_spec.data["pet_type"] == "DOG"
            
            # Verify metadata
            assert registry.metadata["catalog_version"] == "mits-5.0"
            assert "loaded_at" in registry.metadata

    def test_load_missing_version(self):
        """Test loading non-existent version."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_dir = Path(temp_dir) / "rules"
            rules_dir.mkdir()
            
            loader = CatalogLoader(rules_dir)
            registry, findings = loader.load_catalogs("mits-6.0")
            
            # Should have error for missing version
            error_findings = [f for f in findings if f.code == "CATALOG:VERSION_NOT_FOUND"]
            assert len(error_findings) == 1

    def test_load_invalid_json(self):
        """Test loading catalog with invalid JSON."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_dir = Path(temp_dir) / "rules"
            version_dir = rules_dir / "mits-5.0"
            catalogs_dir = version_dir / "catalogs"
            catalogs_dir.mkdir(parents=True)
            
            # Create invalid JSON file
            with open(catalogs_dir / "charge-classes.json", "w") as f:
                f.write('{"invalid": json}')
            
            loader = CatalogLoader(rules_dir)
            registry, findings = loader.load_catalogs("mits-5.0")
            
            # Should have error for invalid JSON
            error_findings = [f for f in findings if f.code == "CATALOG:INVALID_JSON"]
            assert len(error_findings) == 1

    def test_load_duplicate_codes(self):
        """Test loading catalog with duplicate codes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_dir = Path(temp_dir) / "rules"
            version_dir = rules_dir / "mits-5.0"
            catalogs_dir = version_dir / "catalogs"
            catalogs_dir.mkdir(parents=True)
            
            # Create catalog with duplicate codes
            charge_classes = [
                {"code": "PET", "name": "Pet Fee"},
                {"code": "PET", "name": "Pet Fee Duplicate"}
            ]
            with open(catalogs_dir / "charge-classes.json", "w") as f:
                json.dump(charge_classes, f)
            
            loader = CatalogLoader(rules_dir)
            registry, findings = loader.load_catalogs("mits-5.0")
            
            # Should have error for duplicate codes
            error_findings = [f for f in findings if f.code == "CATALOG:DUPLICATE_CODE"]
            assert len(error_findings) == 1
            assert "Duplicate charge class code: PET" in error_findings[0].message

    def test_load_schema_validation_error(self):
        """Test loading catalog that fails schema validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_dir = Path(temp_dir) / "rules"
            version_dir = rules_dir / "mits-5.0"
            catalogs_dir = version_dir / "catalogs"
            schemas_dir = version_dir / "schemas"
            catalogs_dir.mkdir(parents=True)
            schemas_dir.mkdir(parents=True)
            
            # Create catalog with invalid data
            charge_classes = [
                {"code": "invalid-code", "name": "Invalid Code"}  # Invalid code format
            ]
            with open(catalogs_dir / "charge-classes.json", "w") as f:
                json.dump(charge_classes, f)
            
            # Create strict schema
            charge_schema = {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "pattern": "^[A-Z][A-Z0-9_]*$"},
                        "name": {"type": "string", "minLength": 1}
                    },
                    "required": ["code", "name"]
                }
            }
            with open(schemas_dir / "charge-classes.schema.json", "w") as f:
                json.dump(charge_schema, f)
            
            loader = CatalogLoader(rules_dir)
            registry, findings = loader.load_catalogs("mits-5.0")
            
            # Should have error for schema validation
            error_findings = [f for f in findings if f.code == "CATALOG:SCHEMA_VALIDATION_ERROR"]
            assert len(error_findings) == 1

    def test_load_missing_files(self):
        """Test loading with missing catalog files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_dir = Path(temp_dir) / "rules"
            version_dir = rules_dir / "mits-5.0"
            version_dir.mkdir(parents=True)
            
            loader = CatalogLoader(rules_dir)
            registry, findings = loader.load_catalogs("mits-5.0")
            
            # Should have warnings for missing files
            warning_findings = [f for f in findings if f.level == FindingLevel.WARNING]
            assert len(warning_findings) >= 1  # At least one missing file warning

    def test_catalog_entry_creation(self):
        """Test catalog entry creation."""
        # Test ChargeClass
        data = {
            "code": "TEST",
            "name": "Test Class",
            "description": "Test description",
            "aliases": ["TEST_ALIAS"],
            "notes": "Test notes"
        }
        entry = ChargeClass(data)
        assert entry.code == "TEST"
        assert entry.name == "Test Class"
        assert entry.description == "Test description"
        assert entry.aliases == ["TEST_ALIAS"]
        assert entry.notes == "Test notes"
        
        # Test EnumEntry
        enum_entry = EnumEntry(data)
        assert enum_entry.code == "TEST"
        assert enum_entry.name == "Test Class"

    def test_registry_initialization(self):
        """Test catalog registry initialization."""
        registry = CatalogRegistry()
        assert len(registry.charge_classes) == 0
        assert len(registry.enums) == 0
        assert len(registry.specializations) == 0
        assert len(registry.metadata) == 0

    def test_get_catalog_loader(self):
        """Test getting catalog loader instance."""
        from mits_validator.catalogs import get_catalog_loader
        
        loader = get_catalog_loader()
        assert isinstance(loader, CatalogLoader)
        
        # Test with custom rules dir
        custom_loader = get_catalog_loader(Path("/custom/rules"))
        assert custom_loader.rules_dir == Path("/custom/rules")
