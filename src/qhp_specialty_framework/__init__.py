"""
QHP Network Adequacy Provider Specialty Framework & Matrices (PY2027 v1.0)

Implements the CMS Provider Specialty Framework decision logic and specialty
compatibility validation matrices from:
  https://www.qhpcertification.cms.gov/QHP/applicationmaterials/Network-Adequacy
"""

from qhp_specialty_framework.classify import classify_provider
from qhp_specialty_framework.matrices import CompatibilityMatrices
from qhp_specialty_framework.models import (
    ProviderGrouping,
    ProviderRecord,
    ValidationError,
    ValidationResult,
)
from qhp_specialty_framework.validate import validate_provider, validate_providers
from qhp_specialty_framework.convenience import validate_specialty_codes

__all__ = [
    "classify_provider",
    "CompatibilityMatrices",
    "ProviderGrouping",
    "ProviderRecord",
    "ValidationError",
    "ValidationResult",
    "validate_provider",
    "validate_providers",
    "validate_specialty_codes",
]
