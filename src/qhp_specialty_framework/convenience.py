"""Convenience: validate specialty codes directly."""

from __future__ import annotations

from typing import Optional

from qhp_specialty_framework.classify import classify_provider
from qhp_specialty_framework.data import (
    ALLIED_HEALTH_SPECIALTIES,
    ADVANCED_PRACTITIONER_BH_SPECIALTIES,
    ADVANCED_PRACTITIONER_SPECIALTIES,
    BEHAVIORAL_HEALTH_SPECIALTIES,
    BEHAVIORAL_HEALTH_SUBSPECIALTIES,
    DENTIST_SPECIALTIES,
    DENTIST_SUBSPECIALTIES,
    PHYSICIAN_FALLBACK,
    PHYSICIAN_SPECIALTIES,
    PHYSICIAN_SUBSPECIALTIES,
    SURGEON_SPECIALTIES_SET1,
    SURGEON_SPECIALTIES_SET2,
    SURGEON_SUBSPECIALTIES,
)
from qhp_specialty_framework.matrices import CompatibilityMatrices
from qhp_specialty_framework.models import (
    ProviderGrouping,
    ProviderRecord,
    ValidationResult,
)
from qhp_specialty_framework.validate import validate_provider

# Reverse lookup: code → (grouping, is_subspecialty)
_CODE_TO_GROUPING: dict[str, tuple[ProviderGrouping, bool]] = {}


def _build_code_index() -> None:
    """Build a reverse index from specialty code to grouping."""
    if _CODE_TO_GROUPING:
        return

    # ponytail: dict comp replaces 40 lines of explicit loops
    mappings: list[tuple[dict[str, str], ProviderGrouping, bool]] = [
        (SURGEON_SPECIALTIES_SET1, ProviderGrouping.SURGEON, False),
        (SURGEON_SPECIALTIES_SET2, ProviderGrouping.SURGEON, False),
        (SURGEON_SUBSPECIALTIES, ProviderGrouping.SURGEON, True),
        (PHYSICIAN_SPECIALTIES, ProviderGrouping.PHYSICIAN, False),
        (PHYSICIAN_FALLBACK, ProviderGrouping.PHYSICIAN, False),
        (PHYSICIAN_SUBSPECIALTIES, ProviderGrouping.PHYSICIAN, True),
        (DENTIST_SPECIALTIES, ProviderGrouping.DENTIST, False),
        (DENTIST_SUBSPECIALTIES, ProviderGrouping.DENTIST, True),
        (ADVANCED_PRACTITIONER_SPECIALTIES, ProviderGrouping.ADVANCED_PRACTITIONER, False),
        (ADVANCED_PRACTITIONER_BH_SPECIALTIES, ProviderGrouping.ADVANCED_PRACTITIONER, False),
        (BEHAVIORAL_HEALTH_SPECIALTIES, ProviderGrouping.BEHAVIORAL_HEALTH, False),
        (BEHAVIORAL_HEALTH_SUBSPECIALTIES, ProviderGrouping.BEHAVIORAL_HEALTH, True),
        (ALLIED_HEALTH_SPECIALTIES, ProviderGrouping.ALLIED_HEALTH, False),
    ]
    for codes, grouping, is_sub in mappings:
        for code in codes:
            _CODE_TO_GROUPING[code] = (grouping, is_sub)


def validate_specialty_codes(
    codes: list[str],
    provider_grouping: Optional[ProviderGrouping] = None,
    matrices: Optional[CompatibilityMatrices] = None,
) -> ValidationResult:
    """
    Validate a list of specialty/subspecialty codes.

    The simplest way to use the framework. Pass in a list of codes and get
    back whether they form a valid combination.

    Parameters
    ----------
    codes : list[str]
        Specialty and subspecialty codes to validate (e.g. ["003", "008"]).
    provider_grouping : ProviderGrouping, optional
        Override the inferred grouping. If omitted, the grouping is inferred
        from the codes themselves.
    matrices : CompatibilityMatrices, optional
        Pre-loaded matrices. Created on demand if omitted.

    Returns
    -------
    ValidationResult
        Contains errors and warnings. Check ``result.is_valid``.

    Examples
    --------
    >>> result = validate_specialty_codes(["003", "008"])
    >>> result.is_valid
    True  # Internal Medicine + Cardiology subspecialty

    >>> result = validate_specialty_codes(["015", "035"])
    >>> result.is_valid
    False  # Surgeon Set 1 + Set 2 mix
    """
    _build_code_index()
    if matrices is None:
        matrices = CompatibilityMatrices()

    if not codes:
        result = ValidationResult(
            provider=ProviderRecord(npi="", provider_grouping=ProviderGrouping.PHYSICIAN)
        )
        result.add_error("NA V13", "No specialty codes provided.")
        return result

    # Separate specialties from subspecialties
    specialties: list[str] = []
    subspecialties: list[str] = []
    unknown_codes: list[str] = []

    for code in codes:
        info = _CODE_TO_GROUPING.get(code)
        if info is None:
            unknown_codes.append(code)
        elif info[1]:  # is_subspecialty
            subspecialties.append(code)
        else:
            specialties.append(code)

    # Infer grouping from codes
    if provider_grouping is None:
        groupings = set()
        for code in codes:
            info = _CODE_TO_GROUPING.get(code)
            if info:
                groupings.add(info[0])

        if len(groupings) == 1:
            provider_grouping = groupings.pop()
        elif len(groupings) > 1:
            priority = [
                ProviderGrouping.SURGEON,
                ProviderGrouping.DENTIST,
                ProviderGrouping.ADVANCED_PRACTITIONER,
                ProviderGrouping.BEHAVIORAL_HEALTH,
                ProviderGrouping.PHYSICIAN,
                ProviderGrouping.ALLIED_HEALTH,
            ]
            for g in priority:
                if g in groupings:
                    provider_grouping = g
                    break
        else:
            provider_grouping = ProviderGrouping.PHYSICIAN

    # Ensure provider_grouping is set (should always be, but type checker needs it)
    assert provider_grouping is not None

    # Build a ProviderRecord and validate
    provider = ProviderRecord(
        npi="",
        provider_grouping=provider_grouping,
        specialties=specialties,
        subspecialties=subspecialties,
    )

    result = validate_provider(provider, matrices)

    for code in unknown_codes:
        result.add_warning(
            "NA V13",
            f"Unknown specialty code '{code}' — not recognized in any grouping.",
        )

    return result
