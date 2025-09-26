"""Tests for Semantic validation level."""

import tempfile
from pathlib import Path

from mits_validator.levels.semantic import SemanticValidator
from mits_validator.models import FindingLevel


class TestSemanticValidator:
    """Test Semantic validation level."""

    def test_no_catalogs_loaded(self):
        """Test behavior when no catalogs are available."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_dir = Path(temp_dir) / "rules" / "mits-5.0"
            rules_dir.mkdir(parents=True)
            
            validator = SemanticValidator(Path(temp_dir) / "rules", "mits-5.0")
            result = validator.validate(b'<?xml version="1.0"?><root><test>content</test></root>')
            
        assert result.level == "Semantic"
        assert len(result.findings) == 1
        assert result.findings[0].code == "SEMANTIC:ENUM_UNKNOWN"
        assert result.findings[0].level == FindingLevel.INFO
        assert "No catalogs available" in result.findings[0].message

    def test_catalogs_loaded_successfully(self):
        """Test behavior when catalogs are loaded successfully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_dir = Path(temp_dir) / "rules" / "mits-5.0"
            catalogs_dir = rules_dir / "catalogs"
            enums_dir = catalogs_dir / "enums"
            specializations_dir = catalogs_dir / "item-specializations"
            schemas_dir = rules_dir / "schemas"
            
            for dir_path in [catalogs_dir, enums_dir, specializations_dir, schemas_dir]:
                dir_path.mkdir(parents=True)
            
            # Create minimal catalog files
            (catalogs_dir / "charge-classes.json").write_text('[]')
            (enums_dir / "charge-requirement.json").write_text('[]')
            (specializations_dir / "parking.json").write_text('{}')
            
            # Create minimal schemas
            (schemas_dir / "charge-classes.schema.json").write_text('{"type": "array"}')
            (schemas_dir / "enum.schema.json").write_text('{"type": "array"}')
            (schemas_dir / "parking.schema.json").write_text('{"type": "object"}')
            
            validator = SemanticValidator(Path(temp_dir) / "rules", "mits-5.0")
            result = validator.validate(b'<?xml version="1.0"?><root><test>content</test></root>')
            
            assert result.level == "Semantic"
            # Should have no findings when catalogs are loaded successfully
            assert len(result.findings) == 0

    def test_catalogs_loaded_but_empty(self):
        """Test behavior when catalogs are loaded but empty."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_dir = Path(temp_dir) / "rules" / "mits-5.0"
            catalogs_dir = rules_dir / "catalogs"
            enums_dir = catalogs_dir / "enums"
            specializations_dir = catalogs_dir / "item-specializations"
            schemas_dir = rules_dir / "schemas"
            
            for dir_path in [catalogs_dir, enums_dir, specializations_dir, schemas_dir]:
                dir_path.mkdir(parents=True)
            
            # Create empty catalog files
            (catalogs_dir / "charge-classes.json").write_text('[]')
            (enums_dir / "charge-requirement.json").write_text('[]')
            (specializations_dir / "parking.json").write_text('{}')
            
            # Create minimal schemas
            (schemas_dir / "charge-classes.schema.json").write_text('{"type": "array"}')
            (schemas_dir / "enum.schema.json").write_text('{"type": "array"}')
            (schemas_dir / "parking.schema.json").write_text('{"type": "object"}')
            
            validator = SemanticValidator(Path(temp_dir) / "rules", "mits-5.0")
            result = validator.validate(b'<?xml version="1.0"?><root><test>content</test></root>')
            
            assert result.level == "Semantic"
            # Should have no findings when catalogs are loaded successfully
            assert len(result.findings) == 0

    def test_level_crash(self):
        """Test behavior when semantic validation crashes."""
        # Use invalid rules directory to trigger crash
        validator = SemanticValidator(Path("/non/existent/path"), "mits-5.0")
        result = validator.validate(b'<?xml version="1.0"?><root><test>content</test></root>')
        
        assert result.level == "Semantic"
        assert len(result.findings) == 1
        assert result.findings[0].code == "SEMANTIC:ENUM_UNKNOWN"
        assert result.findings[0].level == FindingLevel.INFO
        assert "No catalogs available" in result.findings[0].message

    def test_get_name(self):
        """Test get_name method."""
        validator = SemanticValidator()
        assert validator.get_name() == "Semantic"

    def test_duration_tracking(self):
        """Test that duration is tracked correctly."""
        validator = SemanticValidator()
        result = validator.validate(b'<?xml version="1.0"?><root><test>content</test></root>')
        
        assert result.duration_ms >= 0
        assert isinstance(result.duration_ms, int)
