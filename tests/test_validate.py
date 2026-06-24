"""Tests for validate_provider (grouping-specific rules + matrices)."""

from qhp_specialty_framework import (
    CompatibilityMatrices,
    ProviderGrouping,
    ProviderRecord,
    validate_provider,
)


class TestPhysicianValidation:
    def test_valid_family_medicine(self):
        p = ProviderRecord(
            npi="123",
            provider_grouping=ProviderGrouping.PHYSICIAN,
            specialties=["002"],
        )
        assert validate_provider(p, CompatibilityMatrices()).is_valid

    def test_incompatible_specialties(self):
        """Psychiatry (029) + Dermatology (011) are incompatible."""
        p = ProviderRecord(
            npi="123",
            provider_grouping=ProviderGrouping.PHYSICIAN,
            specialties=["029", "011"],
        )
        result = validate_provider(p, CompatibilityMatrices())
        assert not result.is_valid
        assert any("NA V14" in e.rule for e in result.errors)

    def test_valid_specialty_plus_subspecialty(self):
        """Internal Medicine (003) + Cardiology (008) is valid."""
        p = ProviderRecord(
            npi="123",
            provider_grouping=ProviderGrouping.PHYSICIAN,
            specialties=["003"],
            subspecialties=["008"],
        )
        assert validate_provider(p, CompatibilityMatrices()).is_valid

    def test_three_specialties_exceeds_max(self):
        p = ProviderRecord(
            npi="123",
            provider_grouping=ProviderGrouping.PHYSICIAN,
            specialties=["002", "003", "037"],
        )
        result = validate_provider(p, CompatibilityMatrices())
        assert not result.is_valid
        assert any("maximum is 2" in e.message for e in result.errors)

    def test_incompatible_subspecialty(self):
        """Family Medicine (002) + Cardiology subspecialty (008) is invalid."""
        p = ProviderRecord(
            npi="123",
            provider_grouping=ProviderGrouping.PHYSICIAN,
            specialties=["002"],
            subspecialties=["008"],
        )
        result = validate_provider(p, CompatibilityMatrices())
        assert not result.is_valid
        assert any("NA V15" in e.rule for e in result.errors)


class TestSurgeonValidation:
    def test_valid_set1(self):
        p = ProviderRecord(
            npi="123",
            provider_grouping=ProviderGrouping.SURGEON,
            specialties=["015"],  # General Surgery
        )
        assert validate_provider(p, CompatibilityMatrices()).is_valid

    def test_valid_set2_two(self):
        p = ProviderRecord(
            npi="123",
            provider_grouping=ProviderGrouping.SURGEON,
            specialties=["035", "034"],  # Cardiothoracic + Vascular
        )
        assert validate_provider(p, CompatibilityMatrices()).is_valid

    def test_cannot_mix_sets(self):
        p = ProviderRecord(
            npi="123",
            provider_grouping=ProviderGrouping.SURGEON,
            specialties=["016", "034"],  # Gynecology (Set1) + Vascular (Set2)
        )
        result = validate_provider(p, CompatibilityMatrices())
        assert not result.is_valid
        assert any("cannot mix" in e.message.lower() for e in result.errors)


class TestDentistValidation:
    def test_valid_two_specialties_plus_subspecialty(self):
        p = ProviderRecord(
            npi="123",
            provider_grouping=ProviderGrouping.DENTIST,
            specialties=["201", "P201"],
            subspecialties=["203"],
        )
        assert validate_provider(p, CompatibilityMatrices()).is_valid

    def test_valid_specialty_plus_subspecialty(self):
        p = ProviderRecord(
            npi="123",
            provider_grouping=ProviderGrouping.DENTIST,
            specialties=["201"],
            subspecialties=["202"],
        )
        assert validate_provider(p, CompatibilityMatrices()).is_valid


class TestWrongGrouping:
    def test_grouping_properties(self):
        """Derived booleans match grouping."""
        p = ProviderRecord(
            npi="123",
            provider_grouping=ProviderGrouping.PHYSICIAN,
        )
        assert p.is_md_or_do is True
        assert p.is_surgeon is False
        assert p.is_dentist is False
