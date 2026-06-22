# QHP Provider Specialty Framework — Build Walkthrough

## The Problem

CMS publishes a "Provider Specialty Framework and Matrices" Excel file for QHP Network Adequacy certification. It contains:

- **Two compatibility matrices** (Y/N grids) for physician specialties and subspecialties
- **An embedded Visio flowchart** (as an EMF image) showing the decision tree for classifying providers into groupings
- A "Provider Specialty Framework" sheet that's mostly empty except for the embedded image

The task: download the file, extract all the data including the flowchart, and write a Python function that applies the matrices and decision logic to validate provider specialty combinations.

## Step 1: Finding and Downloading the File

The file lives on the CMS QHP Certification site, a Salesforce SPA:

```
https://www.qhpcertification.cms.gov/QHP/applicationmaterials/Network-Adequacy
```

The download link doesn't point directly to the file — it triggers a JavaScript redirect through Salesforce's file hosting (`spidr.file.force.com`). A direct `curl` returns HTML. Had to parse the JavaScript redirect handler in the page source to extract the actual download URL with session parameters.

**Result:** `PY2027-NA-Provider-Specialty-Framework-Matrices-v1-0-v1.xlsx` (318KB)

## Step 2: Analyzing the Excel Structure

Opened with `openpyxl`. Four sheets:

| Sheet | Content |
|---|---|
| `Overview` | Instructions and notes |
| `Phys Specialty Compat Matrix` | 9×9 Y/N grid — physician specialty compatibility |
| `Phys Subspecialty Compat Matrix` | 11×9 Y/N grid — subspecialty-to-specialty compatibility |
| `Provider Specialty Framework` | Empty except for an embedded 1.3MB EMF image |

The matrices were straightforward to parse — row headers are specialty codes, column headers are specialty codes, cells are Y/N.

## Step 3: The Flowchart Problem

The `Provider Specialty Framework` sheet contained the Visio flowchart embedded as an EMF (Enhanced Metafile) vector image — a Windows-native format. The challenge: **extract the decision logic, specialty names, codes, and set groupings from a binary image format on macOS.**

### What didn't work (and why)

| Tool | Result |
|---|---|
| `Pillow` | Detects EMF format but can't render it |
| `ImageMagick` | Needs `libEMF` compiled in — not included in the Homebrew build |
| `libwmf` (`wmf2svg`) | Only handles WMF, not EMF |
| `chafa` | Terminal ASCII art renderer — doesn't support EMF |
| `inkscape` | Could theoretically open EMF, but `brew install` timed out (1.2GB download) |
| SSH to Windows machine | Timed out — no access |

### The workaround: EMF text extraction

Since EMF files store text labels as UTF-16LE strings in the binary, I used Python regex to extract all readable text:

```python
import re
data = open("image1.emf", "rb").read()
texts = re.findall(rb'\x00([A-Za-z0-9 /&\-\(\)\?]+)\x00', data)
```

This recovered the decision tree logic and specialty names — **but lost all spatial layout information**. I could see "Select no more than one option from Set 1" but couldn't tell which specialties were in Set 1 vs Set 2 because that's determined by which box they appear in visually.

### The initial guess (wrong)

I guessed the Set 1/Set 2 split for surgeons based on specialty names alone:
- Set 1 (max 1): General, Plastic, Ortho, Neuro, Cardiothoracic, Vascular
- Set 2 (max 2): Urology, Oncology-Surgical, ENT, Ophthalmology

**This was wrong.** The user corrected me with test cases, but I couldn't verify the actual split without seeing the image.

## Step 4: Getting the Authoritative Specialty Codes

Downloaded the NA Template (`PY27_NA_Template.xlsx`) from the same CMS site. The "Specialty Types" tab contains all 53 individual specialty codes with names — the authoritative source for code-to-name mapping.

## Step 5: The Breakthrough — `libemf2svg` on macOS

The user asked me to research if there was a way to render EMF on macOS that I might have missed. This time I found **`libemf2svg`** — a Homebrew formula for converting EMF to SVG:

```bash
brew install libemf2svg
emf2svg-conv -i image1.emf -o flowchart.svg -p -v
```

The `-p` flag handles EMF+ records (the enhanced format used by modern Visio). The `-v` flag produces verbose output showing every EMF+ record being parsed.

Then converted SVG to PNG with `rsvg-convert` (already installed):

```
EMF → emf2svg-conv → SVG (284KB) → rsvg-convert → PNG (6167×1435, 1.4MB)
```

## Step 6: Extracting the Flowchart Data

With the rendered PNG, I could finally see the full decision tree. Every detail:

### Decision tree (5 branches)

```
Is the provider an MD or DO?
├─ Yes → Is the provider a surgeon?
│         ├─ Yes → Surgeon grouping
│         │         Set 1 (select ONE): 013, 015, 016, 020, 023, 025, 027, 033
│         │         Set 2 (up to TWO): 034, 035
│         │         Also may select: 021 (Oncology-Surgical/Medical)
│         └─ No  → Physician grouping
│                   Up to 2 specialties + 1 subspecialty
│                   Specialties: 002, 003, 101, 007, 011, 037, 022, 026, 029
│                   Subspecialties: 008, 012, 014, 017, 018, 019, 030, 031, 021, 004, 800
│                   Fallback: 001 (General Practice)
└─ No  → Is the provider a DDS/DMD/DDM?
          ├─ Yes → Dentist grouping (up to 2 specialties + 1 subspecialty)
          │         Specialties: 201, P201
          │         Subspecialties: 202, 203, 204, 206
          └─ No  → Is the provider a NP or PA?
                    ├─ Yes → Advanced Practitioner
                    │         Generalist: 006, A006, P006, 005
                    │         BH path: 108
                    └─ No  → Is the provider behavioral health?
                              ├─ Yes → Behavioral Health (1 specialty + up to 2 subspecialties)
                              │         Specialties: 102, 107, 103
                              │         Subspecialties: 105, 106, 801
                              └─ No  → Allied Health (1 specialty)
                                            010, 028, 049, 050, 051
```

### The Set 1/Set 2 correction

The flowchart revealed the actual split was **different** from my guess:

| My wrong guess (Set 1) | Actual Set 1 (select ONE) |
|---|---|
| General, Plastic, Ortho, Neuro, Cardiothoracic, Vascular | General, ENT, Neuro, Ophthalmology, Ortho, Gynecology/OBGYN, Plastic, Urology |

| My wrong guess (Set 2) | Actual Set 2 (up to TWO) |
|---|---|
| Urology, Oncology-Surgical, ENT, Ophthalmology | Cardiothoracic, Vascular |

Oncology-Surgical/Medical (021) is a subspecialty — "Also may select" in addition to the Set 1/2 choice.

## Step 7: Building the Python Module

The final module (`qhp_specialty_framework.py`, 1087 lines) has three layers:

### Layer 1: Data (lines 1–156)
All 53 specialty codes organized by grouping in `{code: name}` dictionaries. Surgeon codes split into Set 1 (8 codes) and Set 2 (2 codes).

### Layer 2: Core engine (lines 159–733)
- **`classify_provider()`** — applies the flowchart decision tree (boolean credential flags → grouping)
- **`validate_provider()`** — orchestrator: checks grouping matches credentials, dispatches to grouping-specific validator
- **`CompatibilityMatrices`** — loads Y/N grids from Excel or hardcoded data; two query methods
- **6 grouping-specific validators** — each enforces specialty count limits and compatibility rules

### Layer 3: Convenience API (lines 749–924)
**`validate_specialty_codes(codes)`** — the function you actually use. Takes a list of codes, does everything automatically:
1. Builds a reverse index mapping each code → (grouping, is_subspecialty)
2. Separates specialties from subspecialties
3. Infers the grouping from the codes
4. Builds a `ProviderRecord` and calls `validate_provider`

```python
from qhp_specialty_framework import validate_specialty_codes

result = validate_specialty_codes(["003", "008"])
# Automatically: 003→specialty, 008→subspecialty, grouping→Physician
# Checks: max 2 specialties ✓, max 1 subspecialty ✓, matrix compat ✓
print(result.is_valid)  # True
```

## Step 8: Testing

### Built-in demo (12 cases)

| # | Scenario | Result |
|---|---|---|
| 1 | Family Medicine only | ✓ Valid |
| 2 | Psychiatry + Dermatology | ✗ Incompatible per matrix |
| 3 | Internal Medicine + Cardiology subspecialty | ✓ Valid |
| 4 | MD classified as Allied Health | ✗ Wrong grouping |
| 5 | Surgeon, Set 1 (General Surgery) | ✓ Valid |
| 6 | Dentist (Dental-General + Orthodontist) | ✓ Valid |
| 7 | NP (Primary Care APRN) | ✓ Valid |
| 8 | BH (Psychologist + Counselor + MFT) | ✓ Valid |
| 9 | Surgeon, Set 1 + Set 2 mix | ✗ Cannot mix sets |
| 10 | Surgeon, two Set 2 specialties | ✓ Valid |
| 11 | Physician, 3 specialties (max 2) | ✗ Count exceeded |
| 12 | Family Med + Cardiology subspecialty | ✗ Sub not compatible with specialty |

### Interactive test cases (user-provided)

| Codes | Grouping | Result | Detail |
|---|---|---|---|
| `016, 034` | Surgeon | ✗ Invalid | Set 1 (Gynecology) + Set 2 (Vascular) — cannot mix |
| `003, 008` | Physician | ✓ Valid | Internal Medicine + Cardiology subspecialty |
| `201, P201, 203` | Dentist | ✓ Valid | 2 specialties + 1 subspecialty |
| `201, 202` | Dentist | ✓ Valid | 1 specialty + 1 subspecialty |
| `003, 007, 031` | Physician | ✓ Valid | 2 specialties (IM + Allergy) + 1 subspecialty (Rheumatology) |
| `002, 003, 037` | Physician | ✗ Invalid | 3 specialties exceeds max of 2 + warning about primary care subtypes |

## Files

| File | Description |
|---|---|
| `qhp_specialty_framework.py` | Python module (1087 lines) — all logic, data, and validation |
| `PY2027_NA_Template.xlsx` | CMS NA Template (authoritative specialty codes) |
| `framework_flowchart.png` | Rendered flowchart (6167×1435, 1.4MB) |
| `framework_flowchart.svg` | Intermediate SVG from EMF conversion (284KB) |
| `BUILD_WALKTHROUGH.md` | This document |
| `README.md` | Project overview and quick start |
| `requirements.txt` | Python dependencies (`openpyxl`) |
| `.gitignore` | Python/venv exclusions |

## Key Takeaways

- **EMF files on macOS:** `libemf2svg` (`brew install libemf2svg`) is the tool. Chain it with `rsvg-convert` for PNG output.
- **Salesforce SPA downloads:** Parse the JavaScript redirect handler to get the actual file URL.
- **EMF text extraction:** UTF-16LE string regex works for recovering labels, but you lose spatial layout — you need the rendered image to see groupings.
- **53 specialty codes** total across all groupings, plus 15 facility codes in the NA Template.
- **The convenience function** (`validate_specialty_codes`) is the right API — pass codes, get validation back. No need to manually separate specialties/subspecialties or pick groupings.
