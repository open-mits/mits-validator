from __future__ import annotations

from typing import Any

from mits_validator.errors import ERROR_CATALOG


def create_finding(
    code: str,
    message: str | None = None,
    location: dict[str, Any] | None = None,
    rule_ref: str | None = None,
) -> dict[str, Any]:
    """Create a standardized finding from error code."""
    definition = ERROR_CATALOG.get(code)
    if not definition:
        # Fallback for unknown codes
        return {
            "level": "error",
            "code": code,
            "message": message or f"Unknown error: {code}",
            "location": location,
            "rule_ref": rule_ref or "internal://Unknown",
        }

    return {
        "level": definition.severity.value,
        "code": code,
        "message": message or definition.description,
        "location": location,
        "rule_ref": rule_ref or f"internal://{definition.level}",
    }
