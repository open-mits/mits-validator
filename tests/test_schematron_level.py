"""Tests for Schematron validation level."""

import tempfile
from pathlib import Path

from mits_validator.levels.schematron import SchematronValidator
from mits_validator.models import FindingLevel


class TestSchematronValidator:
    """Test Schematron validation level."""

    def test_no_rules_loaded(self):
        """Test behavior when no Schematron rules are available."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_dir = Path(temp_dir) / "rules" / "mits-5.0"
            rules_dir.mkdir(parents=True)
            
            validator = SchematronValidator(rules_dir.parent, "mits-5.0")
            result = validator.validate(b'<?xml version="1.0"?><root><test>content</test></root>')
            
            assert result.level == "Schematron"
            assert len(result.findings) == 1
            assert result.findings[0].code == "SCHEMATRON:NO_RULES_LOADED"
            assert result.findings[0].level == FindingLevel.INFO
            assert "No Schematron rules available" in result.findings[0].message

    def test_rules_directory_exists_but_empty(self):
        """Test behavior when rules directory exists but is empty."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_dir = Path(temp_dir) / "rules" / "mits-5.0" / "schematron"
            rules_dir.mkdir(parents=True)
            
            validator = SchematronValidator(Path(temp_dir) / "rules", "mits-5.0")
            result = validator.validate(b'<?xml version="1.0"?><root><test>content</test></root>')
            
            assert result.level == "Schematron"
            assert len(result.findings) == 1
            assert result.findings[0].code == "SCHEMATRON:NO_RULES_LOADED"
            assert result.findings[0].level == FindingLevel.INFO

    def test_rules_directory_with_files(self):
        """Test behavior when rules directory contains .sch files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_dir = Path(temp_dir) / "rules" / "mits-5.0" / "schematron"
            rules_dir.mkdir(parents=True)
            
            # Create a dummy .sch file
            (rules_dir / "rules.sch").write_text('<?xml version="1.0"?><schema></schema>')
            
            validator = SchematronValidator(Path(temp_dir) / "rules", "mits-5.0")
            result = validator.validate(b'<?xml version="1.0"?><root><test>content</test></root>')
            
            assert result.level == "Schematron"
            assert len(result.findings) == 0  # No findings when rules are available

    def test_xml_parsing_error(self):
        """Test behavior when XML parsing fails."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_dir = Path(temp_dir) / "rules" / "mits-5.0" / "schematron"
            rules_dir.mkdir(parents=True)
            
            # Create a dummy .sch file
            (rules_dir / "rules.sch").write_text('<?xml version="1.0"?><schema></schema>')
            
            validator = SchematronValidator(Path(temp_dir) / "rules", "mits-5.0")
            result = validator.validate(b'<invalid xml content')
            
            assert result.level == "Schematron"
            assert len(result.findings) == 1
            assert result.findings[0].code == "SCHEMATRON:RULE_FAILURE"
            assert result.findings[0].level == FindingLevel.ERROR
            assert "XML parsing failed" in result.findings[0].message

    def test_resource_load_failure(self):
        """Test behavior when resource loading fails."""
        # Use a non-existent directory to trigger resource load failure
        validator = SchematronValidator(Path("/non/existent/path"), "mits-5.0")
        result = validator.validate(b'<?xml version="1.0"?><root><test>content</test></root>')
        
        assert result.level == "Schematron"
        assert len(result.findings) == 1
        assert result.findings[0].code == "SCHEMATRON:NO_RULES_LOADED"
        assert result.findings[0].level == FindingLevel.INFO
        assert "No Schematron rules available" in result.findings[0].message

    def test_get_name(self):
        """Test get_name method."""
        validator = SchematronValidator()
        assert validator.get_name() == "Schematron"

    def test_duration_tracking(self):
        """Test that duration is tracked correctly."""
        validator = SchematronValidator()
        result = validator.validate(b'<?xml version="1.0"?><root><test>content</test></root>')
        
        assert result.duration_ms >= 0
        assert isinstance(result.duration_ms, int)
