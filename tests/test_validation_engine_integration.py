"""Tests for validation engine integration with new levels and profiles."""

import tempfile
from pathlib import Path

from mits_validator.validation_engine import ValidationEngine


class TestValidationEngineIntegration:
    """Test validation engine with new levels and profiles."""

    def test_default_profile_levels(self):
        """Test that default profile includes all levels."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_dir = Path(temp_dir) / "rules" / "mits-5.0"
            rules_dir.mkdir(parents=True)

            # Create minimal profile
            profiles_dir = rules_dir / "profiles"
            profiles_dir.mkdir(parents=True)

            engine = ValidationEngine(rules_dir=Path(temp_dir) / "rules")

            # Should have all levels available
            available_levels = engine.get_available_levels()
            assert "WellFormed" in available_levels
            assert "XSD" in available_levels
            assert "Schematron" in available_levels
            assert "Semantic" in available_levels

    def test_ils_receiver_profile(self):
        """Test ils-receiver profile configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_dir = Path(temp_dir) / "rules" / "mits-5.0"
            rules_dir.mkdir(parents=True)

            # Create ils-receiver profile
            profiles_dir = rules_dir / "profiles"
            profiles_dir.mkdir(parents=True)

            profile_data = {
                "name": "ils-receiver",
                "description": "Profile for ILS receivers",
                "enabled_levels": ["WellFormed", "XSD", "Schematron"],
                "severity_overrides": {
                    "XSD:SCHEMA_MISSING": "error",
                    "SCHEMATRON:NO_RULES_LOADED": "warning",
                },
            }

            import yaml

            with open(profiles_dir / "ils-receiver.yaml", "w") as f:
                yaml.dump(profile_data, f)

            engine = ValidationEngine(profile="ils-receiver", rules_dir=Path(temp_dir) / "rules")

            # Should have specific levels
            available_levels = engine.get_available_levels()
            assert "WellFormed" in available_levels
            assert "XSD" in available_levels
            assert "Schematron" in available_levels
            assert "Semantic" not in available_levels  # Disabled in this profile

    def test_pms_publisher_profile(self):
        """Test pms-publisher profile configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_dir = Path(temp_dir) / "rules" / "mits-5.0"
            rules_dir.mkdir(parents=True)

            # Create pms-publisher profile
            profiles_dir = rules_dir / "profiles"
            profiles_dir.mkdir(parents=True)

            profile_data = {
                "name": "pms-publisher",
                "description": "Profile for PMS publishers",
                "enabled_levels": ["WellFormed", "XSD"],
                "severity_overrides": {
                    "XSD:SCHEMA_MISSING": "warning",
                    "SCHEMATRON:NO_RULES_LOADED": "info",
                },
            }

            import yaml

            with open(profiles_dir / "pms-publisher.yaml", "w") as f:
                yaml.dump(profile_data, f)

            engine = ValidationEngine(profile="pms-publisher", rules_dir=Path(temp_dir) / "rules")

            # Should have limited levels
            available_levels = engine.get_available_levels()
            assert "WellFormed" in available_levels
            assert "XSD" in available_levels
            assert "Schematron" not in available_levels  # Disabled
            assert "Semantic" not in available_levels  # Disabled

    def test_validation_with_schematron_level(self):
        """Test validation with Schematron level."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_dir = Path(temp_dir) / "rules" / "mits-5.0"
            rules_dir.mkdir(parents=True)

            # Create schematron directory (empty)
            schematron_dir = rules_dir / "schematron"
            schematron_dir.mkdir(parents=True)

            engine = ValidationEngine(rules_dir=Path(temp_dir) / "rules")
            results = engine.validate(b'<?xml version="1.0"?><root><test>content</test></root>')

            # Should have results for all levels
            level_names = [result.level for result in results]
            assert "WellFormed" in level_names
            assert "XSD" in level_names
            assert "Schematron" in level_names
            assert "Semantic" in level_names

            # Find Schematron result
            schematron_result = next(r for r in results if r.level == "Schematron")
            assert len(schematron_result.findings) == 1
            assert schematron_result.findings[0].code == "SCHEMATRON:NO_RULES_LOADED"
            assert schematron_result.findings[0].level.value == "info"

    def test_validation_with_semantic_level(self):
        """Test validation with Semantic level."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_dir = Path(temp_dir) / "rules" / "mits-5.0"
            rules_dir.mkdir(parents=True)

            # Create minimal catalogs
            catalogs_dir = rules_dir / "catalogs"
            enums_dir = catalogs_dir / "enums"
            specializations_dir = catalogs_dir / "item-specializations"
            schemas_dir = rules_dir / "schemas"

            for dir_path in [catalogs_dir, enums_dir, specializations_dir, schemas_dir]:
                dir_path.mkdir(parents=True)

            # Create minimal catalog files
            (catalogs_dir / "charge-classes.json").write_text("[]")
            (enums_dir / "charge-requirement.json").write_text("[]")
            (specializations_dir / "parking.json").write_text("{}")

            # Create minimal schemas
            (schemas_dir / "charge-classes.schema.json").write_text('{"type": "array"}')
            (schemas_dir / "enum.schema.json").write_text('{"type": "array"}')
            (schemas_dir / "parking.schema.json").write_text('{"type": "object"}')

            engine = ValidationEngine(rules_dir=Path(temp_dir) / "rules")
            results = engine.validate(b'<?xml version="1.0"?><root><test>content</test></root>')

            # Should have results for all levels
            level_names = [result.level for result in results]
            assert "WellFormed" in level_names
            assert "XSD" in level_names
            assert "Schematron" in level_names
            assert "Semantic" in level_names

            # Find Semantic result
            semantic_result = next(r for r in results if r.level == "Semantic")
            # Should have no findings when catalogs are loaded successfully
            assert len(semantic_result.findings) == 0

    def test_severity_overrides(self):
        """Test that severity overrides are applied correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_dir = Path(temp_dir) / "rules" / "mits-5.0"
            rules_dir.mkdir(parents=True)

            # Create profile with severity overrides
            profiles_dir = rules_dir / "profiles"
            profiles_dir.mkdir(parents=True)

            profile_data = {
                "name": "test-profile",
                "description": "Test profile with overrides",
                "enabled_levels": ["WellFormed", "Schematron"],
                "severity_overrides": {
                    "SCHEMATRON:NO_RULES_LOADED": "error"  # Override info to error
                },
            }

            import yaml

            with open(profiles_dir / "test-profile.yaml", "w") as f:
                yaml.dump(profile_data, f)

            engine = ValidationEngine(profile="test-profile", rules_dir=Path(temp_dir) / "rules")
            results = engine.validate(b'<?xml version="1.0"?><root><test>content</test></root>')

            # Find Schematron result
            schematron_result = next(r for r in results if r.level == "Schematron")
            assert len(schematron_result.findings) == 1
            # Severity should be overridden to error
            assert schematron_result.findings[0].code == "SCHEMATRON:NO_RULES_LOADED"
            assert schematron_result.findings[0].level.value == "error"

    def test_profile_info(self):
        """Test getting profile information."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_dir = Path(temp_dir) / "rules" / "mits-5.0"
            rules_dir.mkdir(parents=True)

            # Create profile
            profiles_dir = rules_dir / "profiles"
            profiles_dir.mkdir(parents=True)

            profile_data = {
                "name": "test-profile",
                "description": "Test profile",
                "enabled_levels": ["WellFormed", "XSD"],
                "severity_overrides": {"XSD:SCHEMA_MISSING": "warning"},
                "intake_limits": {"max_bytes": 5242880, "timeout_seconds": 15},
            }

            import yaml

            with open(profiles_dir / "test-profile.yaml", "w") as f:
                yaml.dump(profile_data, f)

            engine = ValidationEngine(profile="test-profile", rules_dir=Path(temp_dir) / "rules")
            profile_info = engine.get_profile_info()

            assert profile_info["name"] == "test-profile"
            assert profile_info["description"] == "Test profile"
            assert profile_info["levels"] == ["WellFormed", "XSD"]
            assert profile_info["severity_overrides"]["XSD:SCHEMA_MISSING"] == "warning"
            assert profile_info["intake_limits"]["max_bytes"] == 5242880
            assert profile_info["intake_limits"]["timeout_seconds"] == 15

    def test_fallback_to_default_profile(self):
        """Test fallback to default profile when specified profile doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_dir = Path(temp_dir) / "rules" / "mits-5.0"
            rules_dir.mkdir(parents=True)

            # Create default profile
            profiles_dir = rules_dir / "profiles"
            profiles_dir.mkdir(parents=True)

            profile_data = {
                "name": "default",
                "description": "Default profile",
                "enabled_levels": ["WellFormed", "XSD"],
            }

            import yaml

            with open(profiles_dir / "default.yaml", "w") as f:
                yaml.dump(profile_data, f)

            # Try to use non-existent profile
            engine = ValidationEngine(profile="non-existent", rules_dir=Path(temp_dir) / "rules")
            profile_info = engine.get_profile_info()

            # Should fall back to default
            assert profile_info["name"] == "default"
            assert profile_info["levels"] == ["WellFormed", "XSD"]
