"""
Unit tests for the Asset Validator.
Run with: python -m pytest tests/ -v
"""

import pytest
from asset_validator import AssetValidator, AssetReport, ValidationResult


@pytest.fixture
def validator():
    """Return a fresh AssetValidator instance."""
    return AssetValidator()


# ─── Naming Convention Tests ────────────────────────────────────────────────

class TestNamingConvention:
    def test_valid_name(self, validator):
        report = validator.validate("char_hero_rig_v001", "/fake/path.mb")
        check = next(r for r in report.results if r.check_name == "naming_convention")
        assert check.passed

    def test_invalid_name_no_version(self, validator):
        report = validator.validate("char_hero_rig", "/fake/path.mb")
        check = next(r for r in report.results if r.check_name == "naming_convention")
        assert not check.passed

    def test_invalid_name_uppercase(self, validator):
        report = validator.validate("Char_Hero_Rig_v001", "/fake/path.mb")
        check = next(r for r in report.results if r.check_name == "naming_convention")
        assert not check.passed

    def test_invalid_name_spaces(self, validator):
        report = validator.validate("char hero rig v001", "/fake/path.mb")
        check = next(r for r in report.results if r.check_name == "naming_convention")
        assert not check.passed

    def test_valid_name_different_departments(self, validator):
        for name in ["char_hero_rig_v001", "prop_sword_model_v010", "env_forest_light_v100"]:
            report = validator.validate(name, "/fake/path.mb")
            check = next(r for r in report.results if r.check_name == "naming_convention")
            assert check.passed, f"Expected {name} to pass naming convention"


# ─── File Extension Tests ────────────────────────────────────────────────────

class TestFileExtension:
    def test_valid_mb_extension(self, validator):
        report = validator.validate("char_hero_rig_v001", "/fake/path.mb")
        check = next(r for r in report.results if r.check_name == "file_extension")
        assert check.passed

    def test_valid_abc_extension(self, validator):
        report = validator.validate("char_hero_rig_v001", "/fake/path.abc")
        check = next(r for r in report.results if r.check_name == "file_extension")
        assert check.passed

    def test_valid_usd_extension(self, validator):
        report = validator.validate("char_hero_rig_v001", "/fake/path.usd")
        check = next(r for r in report.results if r.check_name == "file_extension")
        assert check.passed

    def test_invalid_psd_extension(self, validator):
        report = validator.validate("char_hero_rig_v001", "/fake/path.psd")
        check = next(r for r in report.results if r.check_name == "file_extension")
        assert not check.passed

    def test_invalid_txt_extension(self, validator):
        report = validator.validate("char_hero_rig_v001", "/fake/path.txt")
        check = next(r for r in report.results if r.check_name == "file_extension")
        assert not check.passed


# ─── Version Number Tests ────────────────────────────────────────────────────

class TestVersionNumber:
    def test_valid_version(self, validator):
        report = validator.validate("char_hero_rig_v001", "/fake/path.mb")
        check = next(r for r in report.results if r.check_name == "version_number")
        assert check.passed

    def test_invalid_version_zero(self, validator):
        report = validator.validate("char_hero_rig_v000", "/fake/path.mb")
        check = next(r for r in report.results if r.check_name == "version_number")
        assert not check.passed

    def test_valid_high_version(self, validator):
        report = validator.validate("char_hero_rig_v099", "/fake/path.mb")
        check = next(r for r in report.results if r.check_name == "version_number")
        assert check.passed


# ─── Metadata Tests ──────────────────────────────────────────────────────────

class TestMetadata:
    def test_valid_metadata(self, validator):
        metadata = {
            "asset_type": "char",
            "department": "rigging",
            "version": "001",
            "artist": "kramani"
        }
        report = validator.validate("char_hero_rig_v001", "/fake/path.mb", metadata)
        check = next(r for r in report.results if r.check_name == "metadata")
        assert check.passed

    def test_missing_metadata_key(self, validator):
        metadata = {"asset_type": "char", "department": "rigging"}
        report = validator.validate("char_hero_rig_v001", "/fake/path.mb", metadata)
        check = next(r for r in report.results if r.check_name == "metadata")
        assert not check.passed

    def test_no_metadata_skips_check(self, validator):
        report = validator.validate("char_hero_rig_v001", "/fake/path.mb")
        check_names = [r.check_name for r in report.results]
        assert "metadata" not in check_names


# ─── Report Tests ────────────────────────────────────────────────────────────

class TestAssetReport:
    def test_report_passed_when_all_checks_pass(self, validator):
        metadata = {
            "asset_type": "char",
            "department": "rigging",
            "version": "001",
            "artist": "kramani"
        }
        report = validator.validate("char_hero_rig_v001", "/fake/path.mb", metadata)
        # file_exists will fail since path is fake, but others should pass
        non_existence_checks = [r for r in report.results if r.check_name != "file_exists"]
        assert all(r.passed for r in non_existence_checks)

    def test_report_failed_checks_list(self, validator):
        report = validator.validate("INVALID NAME", "/fake/path.psd")
        assert len(report.failed_checks) > 0

    def test_report_summary_contains_asset_name(self, validator):
        report = validator.validate("char_hero_rig_v001", "/fake/path.mb")
        assert "char_hero_rig_v001" in report.summary()
