from __future__ import annotations

import sys

from typer.testing import CliRunner

from mits_validator import __version__
from mits_validator.cli import app, version

runner = CliRunner()

def test_cli_version() -> None:
    """Test CLI version command."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.output

def test_cli_help() -> None:
    """Test CLI help command."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "MITS XML feed validator CLI" in result.output

def test_version_function() -> None:
    """Test version function directly."""
    # This is a bit of a hack, but we need to test the function
    # We'll capture the output
    from io import StringIO
    
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    
    try:
        version()
        output = sys.stdout.getvalue()
        assert __version__ in output
    finally:
        sys.stdout = old_stdout
