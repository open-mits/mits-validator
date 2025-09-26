from __future__ import annotations

import typer

from mits_validator import __version__

app = typer.Typer(name="mits-validate", add_completion=False, help="MITS XML feed validator CLI")


@app.command()
def version() -> None:
    """Show the version of mits-validator."""
    typer.echo(__version__)


@app.callback()
def main() -> None:
    """MITS XML feed validator CLI."""
    pass


if __name__ == "__main__":
    app()
