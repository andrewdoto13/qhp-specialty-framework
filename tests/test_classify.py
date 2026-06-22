"""Tests for classify_provider (flowchart decision tree)."""

from qhp_specialty_framework import classify_provider, ProviderGrouping


class TestClassifyProvider:
    def test_md_is_physician(self):
        assert classify_provider(is_md_or_do=True) == ProviderGrouping.PHYSICIAN

    def test_md_surgeon_is_surgeon(self):
        assert classify_provider(is_md_or_do=True, is_surgeon=True) == ProviderGrouping.SURGEON

    def test_dentist(self):
        assert classify_provider(is_dentist=True) == ProviderGrouping.DENTIST

    def test_np_pa_is_advanced_practitioner(self):
        assert classify_provider(is_np_or_pa=True) == ProviderGrouping.ADVANCED_PRACTITIONER

    def test_behavioral_health(self):
        assert classify_provider(is_behavioral_health=True) == ProviderGrouping.BEHAVIORAL_HEALTH

    def test_default_is_allied_health(self):
        assert classify_provider() == ProviderGrouping.ALLIED_HEALTH

    def test_facility(self):
        assert classify_provider(is_facility=True) == ProviderGrouping.FACILITY

    def test_md_takes_priority_over_dentist(self):
        # MD/DO check comes first in the decision tree
        assert classify_provider(is_md_or_do=True, is_dentist=True) == ProviderGrouping.PHYSICIAN

    def test_surgeon_requires_md(self):
        # Surgeon flag alone doesn't classify as surgeon — needs MD/DO
        assert classify_provider(is_surgeon=True) == ProviderGrouping.ALLIED_HEALTH
