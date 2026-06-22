"""Validation: apply framework rules + matrices."""

from qhp_specialty_framework._classify import classify_provider
from qhp_specialty_framework._data import (
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
    SURGEON_SPECIALTIES,
    SURGEON_SPECIALTIES_SET1,
    SURGEON_SPECIALTIES_SET2,
    SURGEON_SUBSPECIALTIES,
)
from qhp_specialty_framework._matrices import CompatibilityMatrices
from qhp_specialty_framework._models import (
    ProviderGrouping,
    ProviderRecord,
    ValidationResult,
)


def validate_provider(
    provider: ProviderRecord,
    matrices: CompatibilityMatrices,
) -> ValidationResult:
    """
    Validate a provider record against the CMS framework rules and matrices.

    Checks:
    - NA V13: Provider Specialty Framework (correct grouping)
    - NA V14: Physician Specialty Compatibility Matrix
    - NA V15: Physician Subspecialty Compatibility Matrix
    - Grouping-specific specialty count rules
    """
    result = ValidationResult(provider=provider)

    grouping = provider.provider_grouping

    # ── NA V13: Verify grouping matches credentials ──
    expected_grouping = classify_provider(
        is_md_or_do=provider.is_md_or_do,
        is_surgeon=provider.is_surgeon,
        is_dentist=provider.is_dentist,
        is_np_or_pa=provider.is_np_or_pa,
        is_behavioral_health=provider.is_behavioral_health,
        is_facility=provider.is_facility,
    )
    if grouping != expected_grouping:
        result.add_error(
            "NA V13",
            f"Provider grouping '{grouping.value}' does not match expected "
            f"'{expected_grouping.value}' based on credentials. "
            f"MD/DO={provider.is_md_or_do}, Surgeon={provider.is_surgeon}, "
            f"Dentist={provider.is_dentist}, NP/PA={provider.is_np_or_pa}, "
            f"BehavioralHealth={provider.is_behavioral_health}",
        )

    # ── Grouping-specific specialty validation ──
    specialties = provider.specialties
    subspecialties = provider.subspecialties

    if grouping == ProviderGrouping.PHYSICIAN:
        _validate_physician(specialties, subspecialties, matrices, result)
    elif grouping == ProviderGrouping.SURGEON:
        _validate_surgeon(specialties, subspecialties, result)
    elif grouping == ProviderGrouping.DENTIST:
        _validate_dentist(specialties, subspecialties, result)
    elif grouping == ProviderGrouping.ADVANCED_PRACTITIONER:
        _validate_advanced_practitioner(specialties, result)
    elif grouping == ProviderGrouping.BEHAVIORAL_HEALTH:
        _validate_behavioral_health(specialties, subspecialties, result)
    elif grouping == ProviderGrouping.ALLIED_HEALTH:
        _validate_allied_health(specialties, result)

    return result


def validate_providers(
    providers: list[ProviderRecord],
    matrices: CompatibilityMatrices | None = None,
) -> list[ValidationResult]:
    """Validate a list of provider records."""
    if matrices is None:
        matrices = CompatibilityMatrices()
    return [validate_provider(p, matrices) for p in providers]


# ────────────────────────────────────────────────────────────────────
# Grouping-specific validators
# ────────────────────────────────────────────────────────────────────


def _validate_physician(
    specialties: list[str],
    subspecialties: list[str],
    matrices: CompatibilityMatrices,
    result: ValidationResult,
) -> None:
    """
    Physician grouping rules (from flowchart):
    - Select up to two specialties from Physician Specialties
    - May designate one subspecialty
    - Also may select: Allergy and Immunology (007), Addiction Medicine Physician (800)
    - May select Gynecology in addition to Family Medicine if certified in obstetrics
    - Issuers should not separately list primary care subtypes alongside Family Medicine
    """
    if len(specialties) > 2:
        result.add_error(
            "NA V13",
            f"Physician has {len(specialties)} specialties; maximum is 2.",
        )

    for code in specialties:
        if code not in PHYSICIAN_SPECIALTIES and code != "800":
            result.add_warning(
                "NA V13",
                f"Specialty code '{code}' is not in the standard Physician Specialties list.",
            )

    # NA V14: Check specialty-to-specialty compatibility
    for i, code_a in enumerate(specialties):
        for code_b in specialties[i + 1:]:
            if not matrices.are_specialties_compatible(code_a, code_b):
                name_a = PHYSICIAN_SPECIALTIES.get(code_a, code_a)
                name_b = PHYSICIAN_SPECIALTIES.get(code_b, code_b)
                result.add_error(
                    "NA V14",
                    f"Specialties '{name_a}' ({code_a}) and '{name_b}' ({code_b}) "
                    f"are not compatible per the Physician Specialty Compatibility Matrix.",
                )

    if len(subspecialties) > 1:
        result.add_error(
            "NA V13",
            f"Physician has {len(subspecialties)} subspecialties; maximum is 1.",
        )

    # NA V15: Check subspecialty-to-specialty compatibility
    for sub_code in subspecialties:
        compatible_with_any = False
        for spec_code in specialties:
            if matrices.is_subspecialty_compatible_with_specialty(sub_code, spec_code):
                compatible_with_any = True
                break
        if not compatible_with_any and specialties:
            sub_name = PHYSICIAN_SUBSPECIALTIES.get(sub_code, sub_code)
            result.add_error(
                "NA V15",
                f"Subspecialty '{sub_name}' ({sub_code}) is not compatible with any "
                f"of the reported specialties: {specialties}.",
            )

    # Primary Care subtype rule
    family_medicine = "002" in specialties
    primary_care_subtypes = {"003", "101", "004"}
    if family_medicine:
        for code in specialties:
            if code in primary_care_subtypes:
                result.add_warning(
                    "NA V13",
                    f"Primary Care subtype '{PHYSICIAN_SPECIALTIES.get(code, code)}' "
                    f"listed alongside Family Medicine. Issuers should not separately list "
                    f"primary care subtypes as additional specialty types alongside Family Medicine.",
                )


def _validate_surgeon(
    specialties: list[str],
    subspecialties: list[str],
    result: ValidationResult,
) -> None:
    """
    Surgeon grouping rules (from flowchart):
    - Set 1: select no more than one option
    - Set 2: select up to two options
    - Cannot mix specialties across Set 1 and Set 2
    """
    set1_codes = set(SURGEON_SPECIALTIES_SET1.keys())
    set2_codes = set(SURGEON_SPECIALTIES_SET2.keys())

    in_set1 = [c for c in specialties if c in set1_codes]
    in_set2 = [c for c in specialties if c in set2_codes]

    if in_set1 and in_set2:
        result.add_error(
            "NA V13",
            f"Surgeon cannot mix specialties across Set 1 and Set 2. "
            f"Set 1: {[SURGEON_SPECIALTIES_SET1.get(c, c) for c in in_set1]}, "
            f"Set 2: {[SURGEON_SPECIALTIES_SET2.get(c, c) for c in in_set2]}.",
        )

    if len(in_set1) > 1:
        result.add_error(
            "NA V13",
            f"Surgeon Set 1 allows max 1 specialty; got {len(in_set1)}: "
            f"{[SURGEON_SPECIALTIES_SET1.get(c, c) for c in in_set1]}.",
        )

    if len(in_set2) > 2:
        result.add_error(
            "NA V13",
            f"Surgeon Set 2 allows max 2 specialties; got {len(in_set2)}: "
            f"{[SURGEON_SPECIALTIES_SET2.get(c, c) for c in in_set2]}.",
        )

    for code in specialties:
        if code not in SURGEON_SPECIALTIES:
            result.add_warning(
                "NA V13",
                f"Specialty code '{code}' is not in the standard Surgeon Specialties list.",
            )


def _validate_dentist(
    specialties: list[str],
    subspecialties: list[str],
    result: ValidationResult,
) -> None:
    """
    Dentist grouping rules (from flowchart):
    - Select up to two specialties from Dental Specialties
    - May designate one subspecialty from Dental Subspecialties
    """
    if len(specialties) > 2:
        result.add_error(
            "NA V13",
            f"Dentist has {len(specialties)} specialties; maximum is 2.",
        )

    for code in specialties:
        if code not in DENTIST_SPECIALTIES:
            result.add_warning(
                "NA V13",
                f"Specialty code '{code}' is not in the standard Dental Specialties list.",
            )

    if len(subspecialties) > 1:
        result.add_error(
            "NA V13",
            f"Dentist has {len(subspecialties)} subspecialties; maximum is 1.",
        )

    for code in subspecialties:
        if code not in DENTIST_SUBSPECIALTIES:
            result.add_warning(
                "NA V13",
                f"Subspecialty code '{code}' is not in the standard Dental Subspecialties list.",
            )


def _validate_advanced_practitioner(
    specialties: list[str],
    result: ValidationResult,
) -> None:
    """
    Advanced Practitioner grouping rules (from flowchart):
    - PAs: Please select Primary Care
    - NPs: Select only if the provider is an NP
    - APRNs: acceptable as PCP or Behavioral Health Provider
    """
    if not specialties:
        result.add_error(
            "NA V13",
            "Advanced Practitioner must have at least one specialty.",
        )
        return

    all_ap = set(ADVANCED_PRACTITIONER_SPECIALTIES) | set(ADVANCED_PRACTITIONER_BH_SPECIALTIES)
    for code in specialties:
        if code not in all_ap:
            result.add_warning(
                "NA V13",
                f"Specialty code '{code}' is not in the standard Advanced Practitioner list.",
            )


def _validate_behavioral_health(
    specialties: list[str],
    subspecialties: list[str],
    result: ValidationResult,
) -> None:
    """
    Behavioral Health grouping rules (from flowchart):
    - Select up to two specialties from Behavioral Health Specialties
    - Up to two subspecialties from Behavioral Health Subspecialties
    - Select only if the provider is a behavioral health provider
    """
    if len(specialties) > 2:
        result.add_error(
            "NA V13",
            f"Behavioral Health provider has {len(specialties)} specialties; maximum is 2.",
        )

    for code in specialties:
        if code not in BEHAVIORAL_HEALTH_SPECIALTIES:
            result.add_warning(
                "NA V13",
                f"Specialty code '{code}' is not in the standard Behavioral Health list.",
            )

    if len(subspecialties) > 2:
        result.add_error(
            "NA V13",
            f"Behavioral Health provider has {len(subspecialties)} subspecialties; maximum is 2.",
        )


def _validate_allied_health(
    specialties: list[str],
    result: ValidationResult,
) -> None:
    """
    Allied Health grouping rules (from flowchart):
    - Only if none of the above groupings apply
    - Select one specialty from Allied Health Specialties
    """
    if len(specialties) > 1:
        result.add_error(
            "NA V13",
            f"Allied Health provider has {len(specialties)} specialties; maximum is 1.",
        )

    for code in specialties:
        if code not in ALLIED_HEALTH_SPECIALTIES:
            result.add_warning(
                "NA V13",
                f"Specialty code '{code}' is not in the standard Allied Health list.",
            )
