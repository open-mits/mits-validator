from __future__ import annotations

import json
from pathlib import Path

import httpx
import typer
from typer import Option

from mits_validator import __version__
from mits_validator.models import ValidationRequest
from mits_validator.validation import ValidationEngine, build_v1_envelope

app = typer.Typer(name="mits-validate", add_completion=False, help="MITS XML feed validator CLI")


@app.command()
def version() -> None:
    """Show the version of mits-validator."""
    typer.echo(__version__)


@app.command()
def validate(
    file: Path | None = Option(None, "--file", "-f", help="Path to XML file to validate"),
    url: str | None = Option(None, "--url", "-u", help="URL to XML content to validate"),
    profile: str = Option("default", "--profile", "-p", help="Validation profile to use"),
    json_output: bool = Option(False, "--json", "-j", help="Output results in JSON format"),
) -> None:
    """Validate MITS XML feed from file or URL."""
    if not file and not url:
        typer.echo("Error: Must provide either --file or --url", err=True)
        raise typer.Exit(1)
    
    if file and url:
        typer.echo("Error: Cannot provide both --file and --url", err=True)
        raise typer.Exit(1)
    
    try:
        if file:
            _validate_file(file, profile, json_output)
        else:
            _validate_url(url, profile, json_output)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


def _validate_file(file_path: Path, profile: str, json_output: bool) -> None:
    """Validate XML file."""
    if not file_path.exists():
        typer.echo(f"Error: File {file_path} does not exist", err=True)
        raise typer.Exit(1)
    
    content = file_path.read_bytes()
    content_type = "application/xml"
    
    # Create validation request
    validation_request = ValidationRequest(
        content=content,
        content_type=content_type,
        source="file",
        url=None,
        filename=file_path.name,
        size_bytes=len(content),
    )
    
    # Initialize validation engine
    engine = ValidationEngine(profile=profile)
    
    # Perform validation
    results = engine.validate(content, content_type)
    
    # Build response
    response_data = build_v1_envelope(validation_request, results, profile, 0)
    
    if json_output:
        print(json.dumps(response_data, indent=2))
    else:
        _print_human_readable(response_data)
    
    # Exit with appropriate code
    if response_data["summary"]["errors"] > 0:
        raise typer.Exit(1)


def _validate_url(url: str, profile: str, json_output: bool) -> None:
    """Validate XML from URL."""
    try:
        # Fetch URL content
        timeout = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=5.0)
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            
            content = response.content
            content_type = response.headers.get("content-type", "application/octet-stream")
            
            # Create validation request
            validation_request = ValidationRequest(
                content=content,
                content_type=content_type,
                source="url",
                url=url,
                filename=None,
                size_bytes=len(content),
            )
            
            # Initialize validation engine
            engine = ValidationEngine(profile=profile)
            
            # Perform validation
            results = engine.validate(content, content_type)
            
            # Build response
            response_data = build_v1_envelope(validation_request, results, profile, 0)
            
            if json_output:
                print(json.dumps(response_data, indent=2))
            else:
                _print_human_readable(response_data)
            
            # Exit with appropriate code
            if response_data["summary"]["errors"] > 0:
                raise typer.Exit(1)
                
    except httpx.TimeoutException:
        typer.echo("Error: Request timed out", err=True)
        raise typer.Exit(1)
    except httpx.HTTPStatusError as e:
        typer.echo(f"Error: HTTP {e.response.status_code}", err=True)
        raise typer.Exit(1)
    except httpx.RequestError as e:
        typer.echo(f"Error: Network request failed: {e}", err=True)
        raise typer.Exit(1)


def _print_human_readable(response_data: dict) -> None:
    """Print human-readable validation results."""
    summary = response_data["summary"]
    findings = response_data["findings"]
    
    # Print summary
    if summary["valid"]:
        typer.echo("✅ Validation passed")
    else:
        typer.echo("❌ Validation failed")
    
    typer.echo(f"Errors: {summary['errors']}, Warnings: {summary['warnings']}")
    
    # Print findings
    if findings:
        typer.echo("\nFindings:")
        for finding in findings:
            if finding["level"] == "error":
                level_icon = "🔴"
            elif finding["level"] == "warning":
                level_icon = "🟡"
            else:
                level_icon = "🔵"
            typer.echo(f"  {level_icon} [{finding['code']}] {finding['message']}")


@app.callback()
def main() -> None:
    """MITS XML feed validator CLI."""
    pass


if __name__ == "__main__":
    app()
