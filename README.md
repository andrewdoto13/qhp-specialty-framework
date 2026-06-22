# QHP Provider Specialty Framework

Python implementation of the CMS Provider Specialty Framework decision logic and specialty compatibility validation matrices for QHP Network Adequacy certification (PY2027).

## What it does

Validates provider specialty/subspecialty combinations against the CMS framework rules:

- **Classifies providers** into 7 groupings via the flowchart decision tree (Physician, Surgeon, Dentist, Advanced Practitioner, Behavioral Health, Allied Health, Facility)
- **Enforces specialty count limits** per grouping (e.g. physicians: max 2 specialties + 1 subspecialty; surgeons: Set 1 max 1 or Set 2 max 2, no mixing)
- **Checks compatibility matrices** — 9×9 specialty-to-specialty grid and 11×9 subspecialty-to-specialty grid from the CMS Excel file

## Quick start

```python
from qhp_specialty_framework import validate_specialty_codes

# Pass in specialty codes, get back valid/invalid with errors
result = validate_specialty_codes(["003", "008"])
print(result.is_valid)  # True — Internal Medicine + Cardiology

result = validate_specialty_codes(["015", "035"])
print(result.is_valid)  # False — Surgeon Set 1 + Set 2 mix
```

The function automatically:
1. Separates specialties from subspecialties
2. Infers the provider grouping from the codes
3. Validates against all framework rules

## Files

| File | Description |
|---|---|
| `qhp_specialty_framework.py` | Main module — all logic, data, and validation |
| `PY2027_NA_Template.xlsx` | CMS NA Template (source for specialty codes) |
| `framework_flowchart.png` | Rendered flowchart from the embedded EMF image |
| `framework_flowchart.svg` | Intermediate SVG from EMF conversion |
| `BUILD_WALKTHROUGH.md` | Detailed walkthrough of how this was built |

## Source data

CMS QHP Certification Network Adequacy materials:
https://www.qhpcertification.cms.gov/QHP/applicationmaterials/Network-Adequacy

File: `PY2027-NA-Provider-Specialty-Framework-Matrices-v1-0-v1.xlsx`
