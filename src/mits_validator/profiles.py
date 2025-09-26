from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from mits_validator.models import ValidationLevel


class ProfileType(str, Enum):
    """Validation profile types."""

    DEFAULT = "default"
    PMS = "pms"  # Property Management System
    ILS = "ils"  # Internet Listing Service
    MARKETPLACE = "marketplace"


@dataclass
class ValidationProfile:
    """Validation profile configuration."""

    name: str
    description: str
    levels: list[ValidationLevel]
    max_size_mb: int
    timeout_seconds: int
    allowed_content_types: list[str]


# Profile configurations
PROFILES: dict[ProfileType, ValidationProfile] = {
    ProfileType.DEFAULT: ValidationProfile(
        name="default",
        description="Default validation profile with all levels",
        levels=[ValidationLevel.WELLFORMED, ValidationLevel.XSD, ValidationLevel.SCHEMATRON],
        max_size_mb=10,
        timeout_seconds=30,
        allowed_content_types=["application/xml", "text/xml", "application/octet-stream"],
    ),
    ProfileType.PMS: ValidationProfile(
        name="pms",
        description="Property Management System validation profile",
        levels=[ValidationLevel.WELLFORMED, ValidationLevel.XSD],
        max_size_mb=5,
        timeout_seconds=15,
        allowed_content_types=["application/xml", "text/xml"],
    ),
    ProfileType.ILS: ValidationProfile(
        name="ils",
        description="Internet Listing Service validation profile",
        levels=[ValidationLevel.WELLFORMED, ValidationLevel.XSD, ValidationLevel.SCHEMATRON],
        max_size_mb=20,
        timeout_seconds=45,
        allowed_content_types=["application/xml", "text/xml", "application/octet-stream"],
    ),
    ProfileType.MARKETPLACE: ValidationProfile(
        name="marketplace",
        description="Marketplace validation profile with strict rules",
        levels=[ValidationLevel.WELLFORMED, ValidationLevel.XSD, ValidationLevel.SCHEMATRON],
        max_size_mb=50,
        timeout_seconds=60,
        allowed_content_types=["application/xml", "text/xml"],
    ),
}


def get_profile(profile_name: str | None = None) -> ValidationProfile:
    """Get validation profile by name."""
    if not profile_name:
        return PROFILES[ProfileType.DEFAULT]

    try:
        profile_type = ProfileType(profile_name.lower())
        return PROFILES[profile_type]
    except ValueError:
        # Unknown profile, return default
        return PROFILES[ProfileType.DEFAULT]


def get_available_profiles() -> list[str]:
    """Get list of available profile names."""
    return [profile.value for profile in ProfileType]
