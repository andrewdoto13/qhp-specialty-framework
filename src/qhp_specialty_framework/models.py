"""Data models: enums, dataclasses for providers and validation results."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ProviderGrouping(str, Enum):
    """Provider groupings from the flowchart decision tree."""

    PHYSICIAN = "Physician"
    SURGEON = "Surgeon"
    DENTIST = "Dentist"
    ADVANCED_PRACTITIONER = "Advanced Practitioner"
    BEHAVIORAL_HEALTH = "Behavioral Health"
    ALLIED_HEALTH = "Allied Health Professional"
    FACILITY = "Facility"


@dataclass
class ValidationError:
    """A single validation error or warning."""

    rule: str  # e.g. "NA V14"
    severity: str  # "error" or "warning"
    message: str


@dataclass
class ProviderRecord:
    """A provider as submitted on the NA Template."""

    npi: str
    provider_grouping: ProviderGrouping
    specialties: list[str] = field(default_factory=list)
    subspecialties: list[str] = field(default_factory=list)

    @property
    def is_md_or_do(self) -> bool:
        return self.provider_grouping in (
            ProviderGrouping.PHYSICIAN,
            ProviderGrouping.SURGEON,
        )

    @property
    def is_surgeon(self) -> bool:
        return self.provider_grouping == ProviderGrouping.SURGEON

    @property
    def is_dentist(self) -> bool:
        return self.provider_grouping == ProviderGrouping.DENTIST

    @property
    def is_np_or_pa(self) -> bool:
        return self.provider_grouping == ProviderGrouping.ADVANCED_PRACTITIONER

    @property
    def is_behavioral_health(self) -> bool:
        return self.provider_grouping == ProviderGrouping.BEHAVIORAL_HEALTH

    @property
    def is_facility(self) -> bool:
        return self.provider_grouping == ProviderGrouping.FACILITY


@dataclass
class ValidationResult:
    """Result of validating a provider record."""

    provider: ProviderRecord
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, rule: str, message: str) -> None:
        self.errors.append(ValidationError(rule=rule, severity="error", message=message))

    def add_warning(self, rule: str, message: str) -> None:
        self.warnings.append(ValidationError(rule=rule, severity="warning", message=message))
