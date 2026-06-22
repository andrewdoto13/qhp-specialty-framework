# QHP Provider Specialty Framework

Python implementation of the CMS Provider Specialty Framework decision logic and specialty compatibility validation matrices for QHP Network Adequacy certification (PY2027).

## What it does

Validates provider specialty/subspecialty combinations against the CMS framework rules:

- **Classifies providers** into 7 groupings via the flowchart decision tree (Physician, Surgeon, Dentist, Advanced Practitioner, Behavioral Health, Allied Health, Facility)
- **Enforces specialty count limits** per grouping (e.g. physicians: max 2 specialties + 1 subspecialty; surgeons: Set 1 max 1 or Set 2 max 2, no mixing)
- **Checks compatibility matrices** — 9×9 specialty-to-specialty grid and 11×9 subspecialty-to-specialty grid from the CMS Excel file

## Quick start

```bash
pip install -e .
```

```python
from qhp_specialty_framework import validate_specialty_codes

# Pass in specialty codes, get back valid/invalid with errors
result = validate_specialty_codes(["003", "008"])
print(result.is_valid)  # True — Internal Medicine + Cardiology

result = validate_specialty_codes(["015", "035"])
print(result.is_valid)  # False — Surgeon Set 1 + Set 2 mix
```

The function automatically:
1. **Separates** specialties from subspecialties
2. **Infers** the provider grouping from the codes
3. **Validates** the combination against all framework rules
4. **Returns** errors/warnings

## API

| Function | Description |
|---|---|
| `validate_specialty_codes(codes)` | Convenience API — pass codes, get result |
| `validate_provider(provider, matrices)` | Validate a ProviderRecord |
| `classify_provider(**credentials)` | Apply flowchart decision tree |

## Tests

```bash
pip install -e ".[dev]"
pytest -v
```

33 tests across 3 test files.

## Project structure

```
src/qhp_specialty_framework/
├── __init__.py         # Public API exports
├── models.py           # Enums, dataclasses
├── data.py             # 53 specialty codes
├── matrices.py         # CompatibilityMatrices
├── classify.py         # Flowchart decision tree
├── validate.py         # 6 grouping validators
└── convenience.py      # validate_specialty_codes()
tests/
├── test_classify.py    # 9 tests
├── test_validate.py    # 11 tests
└── test_convenience.py # 13 tests
data/                   # Source files (NA Template, flowchart)
docs/                   # BUILD_WALKTHROUGH.md
```

## Source data

CMS QHP Certification Network Adequacy materials:
https://www.qhpcertification.cms.gov/QHP/applicationmaterials/Network-Adequacy

File: `PY2027-NA-Provider-Specialty-Framework-Matrices-v1-0-v1.xlsx`
