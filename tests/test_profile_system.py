"""Tests for profile system."""

import tempfile
from pathlib import Path

import yaml

from mits_validator.models import FindingLevel
from mits_validator.profile_loader import ProfileLoader, get_profile_loader
from mits_validator.profile_models import IntakeLimits, ProfileConfig, create_intake_limits


class TestProfileLoader:
    """Test profile loader functionality."""

    def test_load_valid_profile(self):
        """Test loading a valid profile."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_dir = Path(temp_dir) / "rules" / "mits-5.0" / "profiles"
            rules_dir.mkdir(parents=True)
            
            # Create a valid profile
            profile_data = {
                "name": "test-profile",
                "description": "Test profile for validation",
                "enabled_levels": ["WellFormed", "XSD", "Schematron"],
                "severity_overrides": {
                    "XSD:SCHEMA_MISSING": "warning",
                    "SCHEMATRON:NO_RULES_LOADED": "info"
                },
                "intake_limits": {
                    "max_bytes": 5242880,
                    "allowed_content_types": ["application/xml", "text/xml"],
                    "timeout_seconds": 15
                }
            }
            
            with open(rules_dir / "test-profile.yaml", "w") as f:
                yaml.dump(profile_data, f)
            
            loader = ProfileLoader(Path(temp_dir) / "rules")
            profile = loader.load_profile("test-profile", "mits-5.0")
            
            assert profile is not None
            assert profile.name == "test-profile"
            assert profile.description == "Test profile for validation"
            assert profile.enabled_levels == ["WellFormed", "XSD", "Schematron"]
            assert profile.severity_overrides["XSD:SCHEMA_MISSING"] == FindingLevel.WARNING
            assert profile.severity_overrides["SCHEMATRON:NO_RULES_LOADED"] == FindingLevel.INFO
            assert profile.intake_limits is not None
            assert profile.intake_limits.max_bytes == 5242880

    def test_load_missing_profile(self):
        """Test loading a non-existent profile."""
        with tempfile.TemporaryDirectory() as temp_dir:
            loader = ProfileLoader(Path(temp_dir) / "rules")
            profile = loader.load_profile("non-existent", "mits-5.0")
            
            assert profile is None

    def test_load_invalid_yaml(self):
        """Test loading a profile with invalid YAML."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_dir = Path(temp_dir) / "rules" / "mits-5.0" / "profiles"
            rules_dir.mkdir(parents=True)
            
            # Create invalid YAML
            with open(rules_dir / "invalid.yaml", "w") as f:
                f.write("invalid: yaml: content: [")
            
            loader = ProfileLoader(Path(temp_dir) / "rules")
            profile = loader.load_profile("invalid", "mits-5.0")
            
            assert profile is None

    def test_load_profile_with_invalid_severity(self):
        """Test loading a profile with invalid severity levels."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_dir = Path(temp_dir) / "rules" / "mits-5.0" / "profiles"
            rules_dir.mkdir(parents=True)
            
            # Create profile with invalid severity
            profile_data = {
                "name": "test-profile",
                "description": "Test profile",
                "enabled_levels": ["WellFormed"],
                "severity_overrides": {
                    "XSD:SCHEMA_MISSING": "invalid_severity",
                    "SCHEMATRON:NO_RULES_LOADED": "info"
                }
            }
            
            with open(rules_dir / "test-profile.yaml", "w") as f:
                yaml.dump(profile_data, f)
            
            loader = ProfileLoader(Path(temp_dir) / "rules")
            profile = loader.load_profile("test-profile", "mits-5.0")
            
            assert profile is not None
            # Invalid severity should be skipped
            assert "XSD:SCHEMA_MISSING" not in profile.severity_overrides
            assert "SCHEMATRON:NO_RULES_LOADED" in profile.severity_overrides
            assert profile.severity_overrides["SCHEMATRON:NO_RULES_LOADED"] == FindingLevel.INFO

    def test_get_available_profiles(self):
        """Test getting available profile names."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_dir = Path(temp_dir) / "rules" / "mits-5.0" / "profiles"
            rules_dir.mkdir(parents=True)
            
            # Create multiple profiles
            for name in ["default", "ils-receiver", "pms-publisher"]:
                profile_data = {
                    "name": name,
                    "description": f"{name} profile",
                    "enabled_levels": ["WellFormed"]
                }
                with open(rules_dir / f"{name}.yaml", "w") as f:
                    yaml.dump(profile_data, f)
            
            loader = ProfileLoader(Path(temp_dir) / "rules")
            profiles = loader.get_available_profiles("mits-5.0")
            
            assert set(profiles) == {"default", "ils-receiver", "pms-publisher"}

    def test_get_available_profiles_no_directory(self):
        """Test getting available profiles when directory doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            loader = ProfileLoader(Path(temp_dir) / "rules")
            profiles = loader.get_available_profiles("mits-5.0")
            
            assert profiles == []

    def test_get_profile_loader(self):
        """Test getting profile loader instance."""
        loader = get_profile_loader()
        assert isinstance(loader, ProfileLoader)
        
        # Test with custom rules dir
        custom_loader = get_profile_loader(Path("/custom/rules"))
        assert custom_loader.rules_dir == Path("/custom/rules")


class TestProfileModels:
    """Test profile model classes."""

    def test_profile_config_creation(self):
        """Test ProfileConfig creation."""
        config = ProfileConfig(
            name="test",
            description="Test config",
            enabled_levels=["WellFormed", "XSD"],
            severity_overrides={"XSD:SCHEMA_MISSING": FindingLevel.WARNING}
        )
        
        assert config.name == "test"
        assert config.description == "Test config"
        assert config.enabled_levels == ["WellFormed", "XSD"]
        assert config.severity_overrides["XSD:SCHEMA_MISSING"] == FindingLevel.WARNING

    def test_intake_limits_creation(self):
        """Test IntakeLimits creation."""
        limits = IntakeLimits(
            max_bytes=10485760,
            allowed_content_types=["application/xml", "text/xml"],
            timeout_seconds=30
        )
        
        assert limits.max_bytes == 10485760
        assert limits.allowed_content_types == ["application/xml", "text/xml"]
        assert limits.timeout_seconds == 30

    def test_create_intake_limits_from_data(self):
        """Test creating IntakeLimits from dictionary data."""
        data = {
            "max_bytes": 5242880,
            "allowed_content_types": ["application/xml"],
            "timeout_seconds": 15
        }
        
        limits = create_intake_limits(data)
        assert limits is not None
        assert limits.max_bytes == 5242880
        assert limits.allowed_content_types == ["application/xml"]
        assert limits.timeout_seconds == 15

    def test_create_intake_limits_none_data(self):
        """Test creating IntakeLimits from None data."""
        limits = create_intake_limits(None)
        assert limits is None

    def test_create_intake_limits_empty_data(self):
        """Test creating IntakeLimits from empty data."""
        limits = create_intake_limits({})
        assert limits is None
