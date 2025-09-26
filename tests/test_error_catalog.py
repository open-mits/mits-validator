"""Tests for error catalog enforcement."""

import re
from pathlib import Path

from mits_validator.errors import ERROR_CATALOG, get_error_definition


class TestErrorCatalog:
    """Test error catalog completeness and consistency."""

    def test_all_error_codes_registered(self):
        """Test that all error codes used in codebase are registered in catalog."""
        # Find all error codes used in the codebase
        used_codes = set()
        
        # Search for error codes in source files
        src_dir = Path("src/mits_validator")
        for py_file in src_dir.rglob("*.py"):
            content = py_file.read_text()
            # Find patterns like "INTAKE:BOTH_INPUTS", "XSD:SCHEMA_MISSING", etc.
            matches = re.findall(r'"[A-Z_]+:[A-Z_]+"', content)
            for match in matches:
                code = match.strip('"')
                used_codes.add(code)
        
        # Check that all used codes are in the catalog
        missing_codes = used_codes - set(ERROR_CATALOG.keys())
        assert not missing_codes, (
            f"Error codes used in codebase but not in catalog: {missing_codes}"
        )

    def test_catalog_consistency(self):
        """Test that all catalog entries have consistent structure."""
        for code, definition in ERROR_CATALOG.items():
            # Check that code matches the definition
            assert definition.code == code, f"Code mismatch for {code}"
            
            # Check required fields are present
            assert definition.title, f"Missing title for {code}"
            assert definition.description, f"Missing description for {code}"
            assert definition.remediation, f"Missing remediation for {code}"
            assert definition.level, f"Missing level for {code}"
            
            # Check severity is valid
            assert definition.severity in ["error", "warning", "info"], (
                f"Invalid severity for {code}"
            )

    def test_get_error_definition(self):
        """Test error definition retrieval."""
        # Test existing code
        definition = get_error_definition("INTAKE:BOTH_INPUTS")
        assert definition is not None
        assert definition.code == "INTAKE:BOTH_INPUTS"
        assert definition.severity == "error"
        
        # Test non-existing code
        definition = get_error_definition("NONEXISTENT:CODE")
        assert definition is None

    def test_error_code_format(self):
        """Test that all error codes follow the CATEGORY:SUBCODE format."""
        for code in ERROR_CATALOG.keys():
            assert ":" in code, f"Error code {code} must contain ':' separator"
            parts = code.split(":")
            assert len(parts) == 2, f"Error code {code} must have exactly one ':' separator"
            category, subcode = parts
            assert category.isupper(), f"Category {category} must be uppercase"
            assert subcode.isupper(), f"Subcode {subcode} must be uppercase"
            assert "_" in subcode or subcode.isalpha(), (
                f"Subcode {subcode} must contain underscores or be alphabetic"
            )

    def test_no_duplicate_codes(self):
        """Test that there are no duplicate error codes."""
        codes = list(ERROR_CATALOG.keys())
        assert len(codes) == len(set(codes)), "Duplicate error codes found in catalog"

    def test_catalog_coverage(self):
        """Test that catalog covers all major error categories."""
        categories = set()
        for code in ERROR_CATALOG.keys():
            category = code.split(":")[0]
            categories.add(category)
        
        expected_categories = {
            "INTAKE", "WELLFORMED", "XSD", "SCHEMATRON", "ENGINE", "NETWORK", "URL"
        }
        assert categories == expected_categories, (
            f"Missing categories: {expected_categories - categories}"
        )

    def test_error_messages_are_human_readable(self):
        """Test that error messages are human-readable and actionable."""
        for code, definition in ERROR_CATALOG.items():
            # Check title is concise
            assert len(definition.title) <= 50, f"Title too long for {code}: {definition.title}"
            
            # Check description is informative
            assert len(definition.description) >= 10, f"Description too short for {code}"
            assert len(definition.description) <= 200, f"Description too long for {code}"
            
            # Check remediation is actionable
            assert len(definition.remediation) >= 10, f"Remediation too short for {code}"
            assert len(definition.remediation) <= 200, f"Remediation too long for {code}"
            
            # Check messages don't contain technical jargon without explanation
            technical_terms = ["exception", "traceback", "stack", "debug"]
            for term in technical_terms:
                assert term not in definition.description.lower(), (
                    f"Technical jargon in description for {code}"
                )
                assert term not in definition.remediation.lower(), (
                    f"Technical jargon in remediation for {code}"
                )
