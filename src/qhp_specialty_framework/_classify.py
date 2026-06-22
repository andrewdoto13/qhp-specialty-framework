"""Classify provider into grouping (flowchart decision tree logic)."""

from qhp_specialty_framework._models import ProviderGrouping


def classify_provider(
    is_md_or_do: bool = False,
    is_surgeon: bool = False,
    is_dentist: bool = False,
    is_np_or_pa: bool = False,
    is_behavioral_health: bool = False,
    is_facility: bool = False,
) -> ProviderGrouping:
    """
    Apply the Provider Specialty Framework decision tree to classify a provider.

    Decision flow (from the Visio flowchart):

    1. Is the provider an MD or DO?
       ├─ Yes → Is the provider a surgeon?
       │         ├─ Yes → Surgeon
       │         └─ No  → Physician
       └─ No  → Continue to next decision

    2. Is the provider a DDS/DMD (dentist)?
       └─ Yes → Dentist

    3. Is the provider an NP or PA?
       └─ Yes → Advanced Practitioner

    4. Is the provider a behavioral health provider?
       └─ Yes → Behavioral Health

    5. Otherwise → Allied Health Professional
    """
    if is_facility:
        return ProviderGrouping.FACILITY

    if is_md_or_do:
        if is_surgeon:
            return ProviderGrouping.SURGEON
        return ProviderGrouping.PHYSICIAN

    if is_dentist:
        return ProviderGrouping.DENTIST

    if is_np_or_pa:
        return ProviderGrouping.ADVANCED_PRACTITIONER

    if is_behavioral_health:
        return ProviderGrouping.BEHAVIORAL_HEALTH

    return ProviderGrouping.ALLIED_HEALTH
