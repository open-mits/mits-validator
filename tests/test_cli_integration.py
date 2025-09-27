"""Integration tests for CLI functionality."""

import json
import tempfile
from pathlib import Path

import pytest
from mits_validator.cli import app
from typer.testing import CliRunner

runner = CliRunner()


class TestCLIIntegration:
    """Test CLI functionality."""

    def test_cli_version(self):
        """Test CLI version command."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "0.1" in result.stdout

    def test_cli_validate_file_success(self):
        """Test CLI validation with valid XML file."""
        # Create a temporary XML file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?><root><item>test</item></root>')
            xml_file = Path(f.name)

        try:
            result = runner.invoke(app, ["validate", "--file", str(xml_file)])
            # Should exit with code 1 due to XSD validation errors
            assert result.exit_code == 1
            assert "Validation failed" in result.stdout or "❌" in result.stdout
        finally:
            xml_file.unlink()

    def test_cli_validate_file_json(self):
        """Test CLI validation with JSON output."""
        # Create a temporary XML file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?><root><item>test</item></root>')
            xml_file = Path(f.name)

        try:
            result = runner.invoke(app, ["validate", "--file", str(xml_file), "--json"])
            # Should exit with code 1 due to XSD validation errors
            assert result.exit_code == 1

            # Should be valid JSON (may have debug output mixed in)
            output = result.stdout
            # Remove any debug output before the JSON
            if "{" in output:
                json_start = output.find("{")
                json_output = output[json_start:]
                try:
                    json.loads(json_output)
                except json.JSONDecodeError:
                    pytest.fail("Output should be valid JSON")
        finally:
            xml_file.unlink()

    def test_cli_validate_file_not_found(self):
        """Test CLI validation with non-existent file."""
        result = runner.invoke(app, ["validate", "--file", "/non/existent/file.xml"])
        assert result.exit_code == 1
        assert "does not exist" in result.stdout or "does not exist" in result.stderr

    def test_cli_validate_no_input(self):
        """Test CLI validation with no input."""
        result = runner.invoke(app, ["validate"])
        assert result.exit_code == 1
        assert "Must provide either" in result.stdout or "Must provide either" in result.stderr

    def test_cli_validate_both_inputs(self):
        """Test CLI validation with both file and URL."""
        result = runner.invoke(
            app, ["validate", "--file", "test.xml", "--url", "http://example.com"]
        )
        assert result.exit_code == 1
        assert "Cannot provide both" in result.stdout or "Cannot provide both" in result.stderr

    def test_cli_validate_url_timeout(self):
        """Test CLI validation with URL that will timeout."""
        result = runner.invoke(app, ["validate", "--url", "http://httpbin.org/delay/10"])
        # Should timeout and exit with error
        assert result.exit_code == 1
        assert "Error:" in result.stdout or "Error:" in result.stderr

    def test_cli_validate_profile(self):
        """Test CLI validation with different profile."""
        # Create a temporary XML file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?><root><item>test</item></root>')
            xml_file = Path(f.name)

        try:
            result = runner.invoke(
                app, ["validate", "--file", str(xml_file), "--profile", "pms-publisher"]
            )
            # Should exit with code 1 due to XSD validation errors
            assert result.exit_code == 1
        finally:
            xml_file.unlink()
