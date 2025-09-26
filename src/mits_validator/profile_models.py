"""Profile models for validation configuration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mits_validator.models import FindingLevel


@dataclass
class ProfileConfig:
    """Configuration for a validation profile."""

    name: str
    description: str
    enabled_levels: list[str]
    severity_overrides: dict[str, FindingLevel]
    intake_limits: dict[str, Any] | None = None


@dataclass
class IntakeLimits:
    """Intake limits for a profile."""

    max_bytes: int | None = None
    allowed_content_types: list[str] | None = None
    timeout_seconds: int | None = None


def create_intake_limits(data: dict[str, Any] | None) -> IntakeLimits | None:
    """Create IntakeLimits from dictionary data."""
    if not data:
        return None

    return IntakeLimits(
        max_bytes=data.get("max_bytes"),
        allowed_content_types=data.get("allowed_content_types"),
        timeout_seconds=data.get("timeout_seconds"),
    )
