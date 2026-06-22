"""Tests for validate_specialty_codes (convenience API)."""

from qhp_specialty_framework import validate_specialty_codes


class TestConvenienceAPI:
    """Tests that mirror the interactive test cases from the build walkthrough."""

    def test_surgeon_set1_plus_set2_invalid(self):
        """016 (Gynecology, Set1) + 034 (Vascular, Set2) — cannot mix."""
        result = validate_specialty_codes(["016", "034"])
        assert not result.is_valid
        assert any("cannot mix" in e.message.lower() for e in result.errors)

    def test_physician_specialty_plus_subspecialty(self):
        """003 (Internal Medicine) + 008 (Cardiology) — valid."""
        result = validate_specialty_codes(["003", "008"])
        assert result.is_valid

    def test_dentist_two_specs_plus_sub(self):
        """201 + P201 (2 specialties) + 203 (1 subspecialty) — valid."""
        result = validate_specialty_codes(["201", "P201", "203"])
        assert result.is_valid

    def test_dentist_specialty_plus_subspecialty(self):
        """201 (specialty) + 202 (subspecialty) — valid."""
        result = validate_specialty_codes(["201", "202"])
        assert result.is_valid

    def test_physician_three_codes_valid(self):
        """003 + 007 (2 specialties) + 031 (1 subspecialty) — valid."""
        result = validate_specialty_codes(["003", "007", "031"])
        assert result.is_valid

    def test_physician_three_specialties_invalid(self):
        """002 + 003 + 037 (3 specialties) — exceeds max 2."""
        result = validate_specialty_codes(["002", "003", "037"])
        assert not result.is_valid
        assert any("maximum is 2" in e.message for e in result.errors)

    def test_surgeon_set1_plus_set2_general_surgery(self):
        """015 (General Surgery, Set1) + 035 (Cardiothoracic, Set2) — cannot mix."""
        result = validate_specialty_codes(["015", "035"])
        assert not result.is_valid

    def test_surgeon_two_set2(self):
        """035 + 034 (both Set2) — valid."""
        result = validate_specialty_codes(["035", "034"])
        assert result.is_valid

    def test_empty_codes(self):
        result = validate_specialty_codes([])
        assert not result.is_valid
        assert any("No specialty codes" in e.message for e in result.errors)

    def test_unknown_code_warning(self):
        result = validate_specialty_codes(["003", "999"])
        assert any("Unknown specialty code" in w.message for w in result.warnings)

    def test_grouping_inferred(self):
        result = validate_specialty_codes(["003", "008"])
        assert result.provider.provider_grouping.value == "Physician"

    def test_surgeon_grouping_inferred(self):
        result = validate_specialty_codes(["015", "034"])
        assert result.provider.provider_grouping.value == "Surgeon"

    def test_dentist_grouping_inferred(self):
        result = validate_specialty_codes(["201", "202"])
        assert result.provider.provider_grouping.value == "Dentist"
