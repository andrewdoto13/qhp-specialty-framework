# QHP Provider Specialty Framework

Python implementation of the [CMS Provider Specialty Framework](https://www.qhpcertification.cms.gov/QHP/applicationmaterials/Network-Adequacy) decision logic and specialty compatibility matrices for **QHP Network Adequacy certification (PY2027)**.

---

## Why this exists

When health insurance plans apply for **Qualified Health Plan (QHP) certification** on the federal exchanges, they must prove their provider networks meet CMS network adequacy standards. Part of that proof is submitting a spreadsheet (the NA Template) listing every provider in the network with their specialty codes.

CMS publishes a set of rules — a flowchart and two compatibility matrices — that dictate which specialty/subspecialty combinations are valid for each provider type. These rules are enforced during the certification review. **Invalid combinations cause validation errors that can delay or reject the entire application.**

This library encodes those rules so you can **catch errors before submitting**. Instead of waiting weeks for CMS to flag a problem, you validate your provider data locally.

### The problem in plain terms

CMS says things like:

> *"Physicians may select up to two specialties and one subspecialty, but the subspecialty must be compatible with at least one of the reported specialties."*

Or:

> *"Surgeons cannot mix specialties across Set 1 and Set 2."*

If a plan submits a cardiologist with specialty codes that violate these rules, the application gets flagged. This library checks every rule automatically.

### Who is this for?

- **Health plan operations teams** preparing QHP certification submissions
- **Data teams** validating provider rosters before loading them into the NA Template
- **Anyone** who needs to programmatically enforce CMS specialty framework rules

---

## What it does

The framework validates provider specialty data against three layers of CMS rules:

| Layer | What it checks | Example |
|---|---|---|
| **Provider Classification** | Routes each provider through the CMS flowchart to determine their grouping (Physician, Surgeon, Dentist, etc.) | An MD who is also a surgeon → `Surgeon` grouping |
| **Specialty Count Limits** | Enforces how many specialties/subspecialties each grouping allows | Physicians: max 2 specialties + 1 subspecialty |
| **Compatibility Matrices** | Cross-references specialty pairs against CMS-approved compatibility grids | Internal Medicine + Cardiology ✓; Internal Medicine + Dermatology ✗ |

### The 7 provider groupings

The CMS flowchart classifies every provider into one of these buckets, each with its own rules:

| Grouping | Who it covers | Specialty rules |
|---|---|---|
| **Physician** | MDs/DOs who are not surgeons (Internal Medicine, Family Med, Psychiatry, etc.) | Max 2 specialties + 1 subspecialty |
| **Surgeon** | MDs/DOs with surgical specialties | Set 1: max 1 specialty. Set 2: max 2 specialties. Cannot mix sets. |
| **Dentist** | DDS/DMD providers | Max 2 specialties + 1 subspecialty |
| **Advanced Practitioner** | NPs and PAs | Must have at least one specialty |
| **Behavioral Health** | Social workers, psychologists, counselors | Max 2 specialties + 2 subspecialties |
| **Allied Health Professional** | Chiropractors, physical therapists, podiatrists, etc. | Max 1 specialty |
| **Facility** | Healthcare facilities | No specialty validation |

---

## Examples

### Example 1: Valid physician — Internal Medicine with Cardiology subspecialty

```python
from qhp_specialty_framework import validate_specialty_codes

result = validate_specialty_codes(["003", "008"])
# 003 = Internal Medicine (specialty)
# 008 = Cardiology (subspecialty)

print(result.is_valid)       # True
print(result.provider.provider_grouping)  # Physician
```

**What happened:** The framework recognized `003` as a physician specialty and `008` as a subspecialty, classified the provider as a Physician, confirmed the subspecialty is compatible with the specialty via the CMS matrix, and found no rule violations.

### Example 2: Invalid surgeon — mixing Set 1 and Set 2

```python
result = validate_specialty_codes(["015", "035"])
# 015 = General Surgery (Set 1)
# 035 = Cardiothoracic Surgery (Set 2)

print(result.is_valid)       # False
print(result.errors[0].message)
# "Surgeon cannot mix specialties across Set 1 and Set 2."
```

**What happened:** Both codes belong to the Surgeon grouping, but `015` is in Set 1 and `035` is in Set 2. CMS rules prohibit mixing — surgeons pick one set and stay in it.

### Example 3: Valid dentist — two specialties plus a subspecialty

```python
result = validate_specialty_codes(["201", "P201", "203"])
# 201 = Dental-General (specialty)
# P201 = Dental-General(Pediatric) (specialty)
# 203 = Dental-Periodontist (subspecialty)

print(result.is_valid)       # True
```

**What happened:** The dentist grouping allows up to 2 specialties and 1 subspecialty. This combination is within limits.

### Example 4: Invalid physician — too many specialties

```python
result = validate_specialty_codes(["002", "003", "037"])
# 002 = Family Medicine
# 003 = Internal Medicine
# 037 = Emergency Medicine

print(result.is_valid)       # False
print(result.errors[0].message)
# "Physician has 3 specialties; maximum is 2."
```

### Example 5: Batch validation

```python
from qhp_specialty_framework import validate_specialty_codes

providers = [
    (["003", "008"], "Dr. Smith - Internal Med/Cardiology"),
    (["015", "035"], "Dr. Jones - General Surgery/Cardiothoracic"),
    (["201", "202"], "Dr. Lee - General Dentistry/Orthodontics"),
]

for codes, label in providers:
    result = validate_specialty_codes(codes)
    status = "✓" if result.is_valid else "✗"
    print(f"{status} {label}")
# ✓ Dr. Smith - Internal Med/Cardiology
# ✗ Dr. Jones - General Surgery/Cardiothoracic
# ✓ Dr. Lee - General Dentistry/Orthodontics
```

---

## Quick start

Requires **Python 3.10+** (uses native type union syntax).

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
4. **Returns** errors and warnings

## API

| Function | Description |
|---|---|
| `validate_specialty_codes(codes)` | Convenience API — pass codes, get result |
| `validate_provider(provider, matrices)` | Validate a `ProviderRecord` with full control |
| `classify_provider(**credentials)` | Apply flowchart decision tree to get grouping |

### `validate_specialty_codes(codes, provider_grouping=None, matrices=None)`

The simplest entry point. Pass a list of CMS specialty/subspecialty codes and get back a `ValidationResult`.

**Parameters:**
- `codes` — List of specialty/subspecialty codes (e.g., `["003", "008"]`)
- `provider_grouping` — Override the inferred grouping (optional)
- `matrices` — Pre-loaded compatibility matrices (optional, created on demand)

**Returns:** `ValidationResult` with `is_valid`, `errors`, and `warnings` properties.

## Tests

```bash
pip install -e ".[dev]"
pytest -v
```

33 tests across 3 test files covering classification, validation, and the convenience API.

## Project structure

```
src/qhp_specialty_framework/
├── __init__.py         # Public API exports
├── models.py           # Enums, dataclasses (ProviderGrouping, ValidationResult)
├── data.py             # 53 specialty codes organized by grouping
├── matrices.py         # CompatibilityMatrices (hardcoded from CMS Excel)
├── classify.py         # Flowchart decision tree logic
├── validate.py         # 6 grouping-specific validators
└── convenience.py      # validate_specialty_codes()
tests/
├── test_classify.py    # 9 tests — provider classification
├── test_validate.py    # 11 tests — grouping validation rules
└── test_convenience.py # 13 tests — convenience API
data/                   # Source files (NA Template, flowchart)
docs/                   # BUILD_WALKTHROUGH.md
```

## Source data

CMS QHP Certification Network Adequacy materials:
https://www.qhpcertification.cms.gov/QHP/applicationmaterials/Network-Adequacy

File: `PY2027-NA-Provider-Specialty-Framework-Matrices-v1-0-v1.xlsx`

---

Built with Qwen 3.6 27B (MTP) running locally via [Hermes Agent](https://github.com/nousresearch/hermes-agent).
