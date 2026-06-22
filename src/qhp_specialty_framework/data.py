"""Specialty codes from the CMS matrices and flowchart (PY2027)."""

# ────────────────────────────────────────────────────────────────────
# Physician specialties (from flowchart)
# Select up to two specialties and/or may designate one subspecialty
# ────────────────────────────────────────────────────────────────────

PHYSICIAN_SPECIALTIES = {
    "002": "Family Medicine",
    "003": "Internal Medicine",
    "101": "Primary Care Pediatrics",
    "007": "Allergy and Immunology",
    "011": "Dermatology",
    "037": "Emergency Medicine",
    "022": "Oncology-Radiation",
    "026": "Physical Medicine & Rehabilitation",
    "029": "Psychiatry",
}

PHYSICIAN_FALLBACK = {
    "001": "General Practice",
}

PHYSICIAN_SUBSPECIALTIES = {
    "008": "Cardiology",
    "012": "Endocrinology",
    "014": "Gastroenterology",
    "017": "Infectious Disease",
    "018": "Nephrology",
    "019": "Neurology",
    "030": "Pulmonology",
    "031": "Rheumatology",
    "021": "Oncology-Surgical Medical",
    "004": "Geriatrics",
    "800": "Addiction Medicine Physician",
}

# ────────────────────────────────────────────────────────────────────
# Surgeon specialties (from flowchart)
# Set 1: select ONE specialty
# Set 2: select up to TWO specialties
# Cannot mix across sets. Also may select Surgical Subspecialty (021).
# ────────────────────────────────────────────────────────────────────

SURGEON_SPECIALTIES_SET1 = {
    "015": "General Surgery",
    "013": "ENT/Otolaryngology",
    "020": "Neurosurgery",
    "023": "Ophthalmology",
    "025": "Orthopedic Surgery",
    "016": "Gynecology/OBGYN",
    "027": "Plastic Surgery",
    "033": "Urology",
}

SURGEON_SPECIALTIES_SET2 = {
    "035": "Cardiothoracic Surgeon",
    "034": "Vascular Surgeon",
}

SURGEON_SPECIALTIES = {**SURGEON_SPECIALTIES_SET1, **SURGEON_SPECIALTIES_SET2}

SURGEON_SUBSPECIALTIES = {
    "021": "Oncology-Surgical/Medical",
}

# ────────────────────────────────────────────────────────────────────
# Dentist specialties (from flowchart)
# Select up to two specialties and/or may designate one subspecialty
# ────────────────────────────────────────────────────────────────────

DENTIST_SPECIALTIES = {
    "201": "Dental-General",
    "P201": "Dental-General(Pediatric)",
}

DENTIST_SUBSPECIALTIES = {
    "204": "Dental-Endodontist",
    "202": "Dental-Orthodontist",
    "203": "Dental-Periodontist",
    "206": "Dental-Prosthodontist",
}

# ────────────────────────────────────────────────────────────────────
# Advanced Practitioner specialties (from flowchart)
# Generalist path
# ────────────────────────────────────────────────────────────────────

ADVANCED_PRACTITIONER_SPECIALTIES = {
    "006": "Primary Care Advanced Practice Registered Nurse",
    "A006": "Primary Care APRN-Adult",
    "P006": "Primary Care APRN-Pediatric",
    "005": "Primary Care-Physician Assistant",
}

ADVANCED_PRACTITIONER_BH_SPECIALTIES = {
    "108": "Behavioral Health APRN",
}

# ────────────────────────────────────────────────────────────────────
# Behavioral Health specialties (from flowchart)
# Select one specialty and/or may designate up to two subspecialties
# ────────────────────────────────────────────────────────────────────

BEHAVIORAL_HEALTH_SPECIALTIES = {
    "102": "Social Worker",
    "107": "Counselor (Mental Health and Professional)",
    "103": "Psychologist",
}

BEHAVIORAL_HEALTH_SUBSPECIALTIES = {
    "105": "Marriage and Family Therapist",
    "106": "Addiction (Substance Use Disorder) Counselor",
    "801": "Behavioral Analyst",
}

# ────────────────────────────────────────────────────────────────────
# Allied Health specialties (from flowchart)
# Select Allied Health Professionals grouping and one specialty
# ────────────────────────────────────────────────────────────────────

ALLIED_HEALTH_SPECIALTIES = {
    "010": "Chiropractor",
    "028": "Podiatry",
    "049": "Physical Therapy",
    "051": "Speech Therapy",
    "050": "Occupational Therapy",
}
