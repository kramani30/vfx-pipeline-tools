"""
Asset Validator
---------------
A pipeline utility for validating VFX assets before they are
published to production. Checks naming conventions, file existence,
required metadata, and hierarchy integrity.

This is a standalone utility that can be integrated into any
DCC tool (Maya, Houdini, Nuke) or run as part of a CI/CD pipeline.
"""

import os
import re
from dataclasses import dataclass, field
from typing import Optional


# ─── Data Classes ───────────────────────────────────────────────────────────

@dataclass
class ValidationResult:
    """Result of a single validation check."""
    check_name: str
    passed: bool
    message: str


@dataclass
class AssetReport:
    """Full validation report for an asset."""
    asset_name: str
    asset_path: str
    results: list[ValidationResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """Return True if all checks passed."""
        return all(r.passed for r in self.results)

    @property
    def failed_checks(self) -> list[ValidationResult]:
        """Return list of failed checks."""
        return [r for r in self.results if not r.passed]

    def summary(self) -> str:
        """Return a human-readable summary of the validation report."""
        status = "PASSED" if self.passed else "FAILED"
        lines = [
            f"Asset: {self.asset_name}",
            f"Path: {self.asset_path}",
            f"Status: {status}",
            f"Checks: {len(self.results)} total, {len(self.failed_checks)} failed",
        ]
        if self.failed_checks:
            lines.append("Failed checks:")
            for check in self.failed_checks:
                lines.append(f"  - {check.check_name}: {check.message}")
        return "\n".join(lines)


# ─── Validators ─────────────────────────────────────────────────────────────

class AssetValidator:
    """
    Validates VFX assets against production pipeline standards.

    Usage:
        validator = AssetValidator()
        report = validator.validate("char_hero_rig_v001", "/path/to/asset.mb")
        print(report.summary())
    """

    NAMING_PATTERN = re.compile(
        r"^[a-z]+_[a-z]+_[a-z]+_v\d{3}$"
    )

    ALLOWED_EXTENSIONS = {".mb", ".ma", ".abc", ".usd", ".fbx", ".obj"}

    REQUIRED_METADATA_KEYS = ["asset_type", "department", "version", "artist"]

    def validate(
        self,
        asset_name: str,
        asset_path: str,
        metadata: Optional[dict] = None
    ) -> AssetReport:
        """
        Run all validation checks on an asset.

        Args:
            asset_name: Name of the asset (e.g. char_hero_rig_v001)
            asset_path: Full path to the asset file
            metadata: Optional dictionary of asset metadata

        Returns:
            AssetReport with results of all checks
        """
        report = AssetReport(asset_name=asset_name, asset_path=asset_path)

        report.results.append(self._check_naming_convention(asset_name))
        report.results.append(self._check_file_extension(asset_path))
        report.results.append(self._check_file_exists(asset_path))
        report.results.append(self._check_version_number(asset_name))

        if metadata is not None:
            report.results.append(self._check_metadata(metadata))

        return report

    def _check_naming_convention(self, asset_name: str) -> ValidationResult:
        """Check that asset name follows the convention: type_name_dept_vXXX."""
        passed = bool(self.NAMING_PATTERN.match(asset_name))
        return ValidationResult(
            check_name="naming_convention",
            passed=passed,
            message="OK" if passed else (
                f"'{asset_name}' does not match pattern: type_name_dept_vXXX "
                f"(e.g. char_hero_rig_v001)"
            )
        )

    def _check_file_extension(self, asset_path: str) -> ValidationResult:
        """Check that the file has an allowed extension."""
        ext = os.path.splitext(asset_path)[1].lower()
        passed = ext in self.ALLOWED_EXTENSIONS
        return ValidationResult(
            check_name="file_extension",
            passed=passed,
            message="OK" if passed else (
                f"Extension '{ext}' not allowed. "
                f"Allowed: {', '.join(sorted(self.ALLOWED_EXTENSIONS))}"
            )
        )

    def _check_file_exists(self, asset_path: str) -> ValidationResult:
        """Check that the file exists on disk."""
        passed = os.path.exists(asset_path)
        return ValidationResult(
            check_name="file_exists",
            passed=passed,
            message="OK" if passed else f"File not found: {asset_path}"
        )

    def _check_version_number(self, asset_name: str) -> ValidationResult:
        """Check that the version number is greater than 0."""
        match = re.search(r"v(\d{3})$", asset_name)
        if not match:
            return ValidationResult(
                check_name="version_number",
                passed=False,
                message="Could not extract version number from asset name"
            )
        version = int(match.group(1))
        passed = version > 0
        return ValidationResult(
            check_name="version_number",
            passed=passed,
            message="OK" if passed else "Version number must be greater than 0"
        )

    def _check_metadata(self, metadata: dict) -> ValidationResult:
        """Check that all required metadata keys are present."""
        missing = [k for k in self.REQUIRED_METADATA_KEYS if k not in metadata]
        passed = len(missing) == 0
        return ValidationResult(
            check_name="metadata",
            passed=passed,
            message="OK" if passed else f"Missing required metadata keys: {missing}"
        )


# ─── Run ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    validator = AssetValidator()

    # Valid asset
    report = validator.validate(
        asset_name="char_hero_rig_v001",
        asset_path="/path/to/char_hero_rig_v001.mb",
        metadata={
            "asset_type": "char",
            "department": "rigging",
            "version": "001",
            "artist": "kramani"
        }
    )
    print(report.summary())
    print()

    # Invalid asset
    report2 = validator.validate(
        asset_name="HeroRig_Final_FINAL",
        asset_path="/path/to/HeroRig_Final_FINAL.psd",
    )
    print(report2.summary())
