"""
EduPulse — core configuration, constants, and locked master lists.

EduPulse = Institutional Health Diagnostics Engine.
It is NOT a ranking system, compliance dashboard, or data warehouse.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Versioning / traceability
# ---------------------------------------------------------------------------
APP_NAME = "EduPulse"
APP_TAGLINE = "Institutional Health Diagnostics Engine"
LOGIC_VERSION = "1.0.0"
TEMPLATE_VERSION = "1.0.0"

# ---------------------------------------------------------------------------
# Sheet names (LOCKED — the system owns the template shape)
# ---------------------------------------------------------------------------
SHEET_README = "README"
SHEET_ICG = "ICG_Input"
SHEET_DMM = "DMM_Input"
SHEET_GPIS_SUPPLY = "GPIS_Supply"
SHEET_GPIS_DEMAND = "GPIS_Demand"
SHEET_LOOKUPS = "LOOKUPS"

REQUIRED_SHEETS = [SHEET_ICG, SHEET_DMM, SHEET_GPIS_SUPPLY, SHEET_GPIS_DEMAND]

# ---------------------------------------------------------------------------
# Column specifications per sheet (LOCKED)
# Each entry: (column_label, allowed_values_or_type)
# type markers: "text", "int"
# ---------------------------------------------------------------------------
ICG_COLUMNS = [
    ("Department", "text"),
    ("Faculty Name", "text"),
    ("Sole Expert", ["Yes", "No"]),
    ("Number of Faculty in Subject", "int"),
    ("Backup Available", ["Yes", "No"]),
    ("Retirement Horizon", ["Within 3 years", "3–7 years", "7+ years"]),
    ("Knowledge Transfer", ["Active", "Limited", "None"]),
    ("Employee Type", ["Permanent", "Contract", "Professor of Practice", "Visiting", "Industry Fellow"]),
    ("Market Demand for Skill", ["High", "Medium", "Low"]),
]

DMM_COLUMNS = [
    ("Programme Name", "text"),
    ("Employment Trend", ["Improving", "Stable", "Declining"]),
    ("Placement Status", ["Strong", "Moderate", "Weak", "NA"]),
    ("Alumni Relevance", ["High", "Moderate", "Low"]),
    ("Fees Band", ["Low", "Medium", "High"]),
    ("Salary Band", ["Low", "Medium", "High"]),
    ("Curriculum Recency", ["≤2 years", "3–5 years", "5+ years"]),
    ("Revision Trigger", ["Industry", "Internal", "Compliance", "None"]),
    ("Employer Engagement", ["Annual", "Occasional", "Rare"]),
    ("Student Experience", ["Freshers", "Mixed", "Experienced"]),
    ("Startup Signal", ["High", "Moderate", "Low", "NA"]),
    ("Degree–Job Alignment", ["High Match", "Partial Match", "No Match"]),
    ("Institutional Contribution", ["High", "Moderate", "Low"]),
    ("Delivery Discipline", ["Strong", "Moderate", "Weak"]),
    ("Teaching Engagement", ["High", "Medium", "Low"]),
    ("Learning Improvement", ["Strong Improvement", "Moderate Improvement", "Limited Improvement"]),
]

GPIS_SUPPLY_COLUMNS = [
    ("Programme Name", "text"),
    ("Domain", "domain"),
    ("Geography", "geography"),
    ("Intake Capacity", "int"),
    ("Actual Intake", "int"),
]

GPIS_DEMAND_COLUMNS = [
    ("Domain", "domain"),
    ("Geography", "geography"),
    ("Demand Presence", ["Yes", "No"]),
    ("Employment Strength", ["High", "Moderate", "Low"]),
]

# ---------------------------------------------------------------------------
# Locked Domain Master List
# ---------------------------------------------------------------------------
DOMAINS = [
    "Commerce", "Finance", "Accounting", "Banking", "Economics",
    "Management", "Marketing", "Human Resources", "Entrepreneurship",
    "Business Analytics", "Data Analytics", "Statistics",
    "Computer Applications", "Information Technology", "Computer Science",
    "Artificial Intelligence", "Cybersecurity",
    "Law", "Public Policy", "Governance",
    "Education", "Teacher Education", "Psychology",
    "Media", "Communication", "Journalism",
    "Design", "Fine Arts",
    "Hospitality", "Tourism",
    "Healthcare", "Public Health", "Pharmacy", "Biotechnology",
    "Agriculture", "Environmental Studies", "Sustainability", "ESG",
    "Logistics", "Supply Chain", "International Business",
    "Engineering",
]

# ---------------------------------------------------------------------------
# Locked Geography Master List
# ---------------------------------------------------------------------------
GEOGRAPHIES_INDIA = [
    "North India", "South India", "East India", "West India",
    "Central India", "Pan India",
]
GEOGRAPHIES_INTERNATIONAL = [
    "South Asia", "Southeast Asia", "Middle East", "Africa",
    "Europe", "North America", "Latin America", "Oceania", "Global",
]
GEOGRAPHIES = GEOGRAPHIES_INDIA + GEOGRAPHIES_INTERNATIONAL

# ---------------------------------------------------------------------------
# Reporting modes
# ---------------------------------------------------------------------------
MODE_INTERNAL = "internal"
MODE_EXTERNAL = "external"
REPORTING_MODES = [MODE_INTERNAL, MODE_EXTERNAL]

# ---------------------------------------------------------------------------
# Framework state labels (LOCKED)
# ---------------------------------------------------------------------------
ICG_STATES = ["Resilient", "Stable", "Vulnerable", "Priority Action"]
DMM_STATES = ["Anabolic", "Transitional", "Static", "Catabolic"]
GPIS_STATES = [
    "Strong Alignment", "Approximate Alignment",
    "Oversupply", "Undersupply", "Weak Alignment", "Mismatch",
]
EDUPULSE_STATES = ["Thriving", "Healthy", "Stretched", "Fragile", "Critical"]

# Numeric anchors (0–100) per state (used in integrated scoring)
ICG_STATE_SCORES = {
    "Resilient": 85,
    "Stable": 70,
    "Vulnerable": 45,
    "Priority Action": 25,
}
DMM_STATE_SCORES = {
    "Anabolic": 85,
    "Transitional": 65,
    "Static": 47,
    "Catabolic": 25,
}
GPIS_STATE_SCORES = {
    "Strong Alignment": 88,
    "Approximate Alignment": 72,
    "Undersupply": 58,
    "Weak Alignment": 45,
    "Oversupply": 35,
    "Mismatch": 20,
}

# Integrated EduPulse weights
EDUPULSE_WEIGHTS = {"ICG": 0.30, "DMM": 0.40, "GPIS": 0.30}

EDUPULSE_THRESHOLDS = [
    (80, "Thriving"),
    (65, "Healthy"),
    (50, "Stretched"),
    (35, "Fragile"),
    (0,  "Critical"),
]

# ---------------------------------------------------------------------------
# Adoption-safe vocabulary (external mode softens labels)
# ---------------------------------------------------------------------------
EXTERNAL_LABEL_SOFTENERS = {
    "Priority Action": "Attention Needed",
    "Catabolic": "In Decline",
    "Mismatch": "Alignment Gap",
    "Oversupply": "Capacity Exceeds Visible Demand",
    "Critical": "Under Pressure",
    "Fragile": "At Risk",
}


def soften_label(label: str, mode: str) -> str:
    """Return an adoption-safe label for external reporting mode."""
    if mode == MODE_EXTERNAL and label in EXTERNAL_LABEL_SOFTENERS:
        return EXTERNAL_LABEL_SOFTENERS[label]
    return label
