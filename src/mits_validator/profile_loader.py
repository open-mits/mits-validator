"""Profile loader for validation configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from mits_validator.models import FindingLevel
from mits_validator.profile_models import ProfileConfig, create_intake_limits


class ProfileLoader:
    """Loader for validation profiles."""

    def __init__(self, rules_dir: Path | None = None) -> None:
        self.rules_dir = rules_dir or Path("rules")

    def load_profile(self, profile_name: str, version: str = "mits-5.0") -> ProfileConfig | None:
        """Load a profile by name."""
        profile_file = self.rules_dir / version / "profiles" / f"{profile_name}.yaml"

        if not profile_file.exists():
            return None

        try:
            with open(profile_file) as f:
                data = yaml.safe_load(f)

            return self._parse_profile(data)
        except Exception:
            return None

    def _parse_profile(self, data: dict[str, Any]) -> ProfileConfig:
        """Parse profile data into ProfileConfig."""
        # Parse severity overrides
        severity_overrides = {}
        if "severity_overrides" in data:
            for code, severity_str in data["severity_overrides"].items():
                try:
                    severity_overrides[code] = FindingLevel(severity_str.lower())
                except (ValueError, AttributeError):
                    # Skip invalid severity levels
                    continue

        # Parse intake limits
        intake_limits = None
        if "intake_limits" in data:
            intake_limits = create_intake_limits(data["intake_limits"])

        return ProfileConfig(
            name=data.get("name", "unknown"),
            description=data.get("description", ""),
            enabled_levels=data.get("enabled_levels", []),
            severity_overrides=severity_overrides,
            intake_limits=intake_limits,
        )

    def get_available_profiles(self, version: str = "mits-5.0") -> list[str]:
        """Get list of available profile names."""
        profiles_dir = self.rules_dir / version / "profiles"
        if not profiles_dir.exists():
            return []

        return [f.stem for f in profiles_dir.glob("*.yaml")]


def get_profile_loader(rules_dir: Path | None = None) -> ProfileLoader:
    """Get a profile loader instance."""
    return ProfileLoader(rules_dir)
