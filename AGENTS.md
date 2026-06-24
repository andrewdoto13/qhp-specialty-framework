# QHP Specialty Framework — Agent Context

## Project overview

Python library implementing the CMS Provider Specialty Framework decision logic and specialty compatibility validation matrices for QHP Network Adequacy certification (PY2027). Validates provider specialty/subspecialty combinations against CMS rules before submission.

## Structure

```
src/qhp_specialty_framework/
├── __init__.py         # Public API exports
├── models.py           # Enums (ProviderGrouping), dataclasses (ProviderRecord, ValidationResult, ValidationError)
├── data.py             # 53 specialty codes organized by grouping (Physician, Surgeon, Dentist, etc.)
├── matrices.py         # CompatibilityMatrices — hardcoded from CMS Excel
├── classify.py         # Flowchart decision tree: grouping → ProviderGrouping
├── validate.py         # 6 grouping-specific validators + batch validation
└── convenience.py      # validate_specialty_codes() — auto-infer grouping from codes
tests/
├── test_classify.py    # Provider classification (9 tests)
├── test_validate.py    # Grouping validation rules (11 tests)
└── test_convenience.py # Convenience API (13 tests)
data/                   # Source CMS files (NA Template, flowchart)
docs/                   # BUILD_WALKTHROUGH.md
```

## Conventions

- **Python 3.10+**, `src/` layout, `pyproject.toml` (setuptools)
- Tests via `pytest` — run with `python -m pytest -v`
- Data model: `ProviderRecord` → `validate_provider()` → `ValidationResult` (`.is_valid`, `.errors`, `.warnings`)
- Convenience entry point: `validate_specialty_codes(codes)` — separates specialties/subspecialties, infers grouping, validates
- Specialty codes are CMS NA Template codes (e.g., `"003"` = Internal Medicine, `"008"` = Cardiology)
- 7 provider groupings: Physician, Surgeon, Dentist, Advanced Practitioner, Behavioral Health, Allied Health, Facility

## Key rules by grouping

| Grouping | Specialty limit | Subspecialty limit | Special rules |
|---|---|---|---|
| Physician | Max 2 | Max 1 | Subspecialty must be compatible with at least one specialty (NA V14/V15 matrices) |
| Surgeon | Set 1: max 1 / Set 2: max 2 | Max 1 (021) | Cannot mix Set 1 and Set 2 |
| Dentist | Max 2 | Max 1 | — |
| Advanced Practitioner | At least 1 | — | — |
| Behavioral Health | Max 2 | Max 2 | — |
| Allied Health | Max 1 | — | — |
| Facility | — | — | No specialty validation |

## Gotchas

- Surgeon Set 1 vs Set 2 is enforced separately — a surgeon can have 1 Set 1 specialty OR up to 2 Set 2 specialties, never both
- Physician subspecialties must be matrix-compatible with at least one listed specialty (NA V15)
- Physician specialty pairs must also be matrix-compatible (NA V14)
- `ProviderRecord` derives `is_*` booleans from `provider_grouping` — no need to pass them separately
- `convenience.py` builds a reverse code index on first call — it's lazy-loaded
- Unknown codes produce warnings, not errors

## Do not

- Add new specialty codes without verifying against the CMS source data
- Change grouping enum values in `models.py` — they must match CMS terminology exactly
- Modify `data.py` constants without updating `convenience.py`'s reverse code index builder
- Introduce new dependencies without adding them to `pyproject.toml`
- Skip tests when changing validation logic in `validate.py` — each grouping has dedicated tests

## Dependencies

- Runtime: None (stdlib only)
- Dev: `pytest`

## Running

```bash
pip install -e ".[dev]"
python -m pytest -v
```
