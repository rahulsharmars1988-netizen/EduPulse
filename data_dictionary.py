"""
Data Dictionary Engine.

Every field in every sheet is declared here with its meaning, allowed values,
role in analysis, and validation logic. This is consumed by the template
generator (to produce the README sheet and dropdown lists), the validator,
and the interpretation engine.
"""
from __future__ import annotations

from .config import (
    ICG_COLUMNS, DMM_COLUMNS, GPIS_SUPPLY_COLUMNS, GPIS_DEMAND_COLUMNS,
    SHEET_ICG, SHEET_DMM, SHEET_GPIS_SUPPLY, SHEET_GPIS_DEMAND,
)

# role: what this field contributes to the analysis
DATA_DICTIONARY = {
    SHEET_ICG: {
        "Department": {
            "role": "Grouping field. Used for concentration & succession clustering.",
            "required": True,
        },
        "Faculty Name": {
            "role": "Identity field for faculty-level risk flags.",
            "required": True,
        },
        "Sole Expert": {
            "role": "Primary dependency signal. Yes = single point of failure.",
            "required": True,
        },
        "Number of Faculty in Subject": {
            "role": "Capacity context. Low count amplifies sole-expert risk.",
            "required": True,
        },
        "Backup Available": {
            "role": "Continuity buffer. No backup + sole expert = critical dependency.",
            "required": True,
        },
        "Retirement Horizon": {
            "role": "Time pressure on succession planning.",
            "required": True,
        },
        "Knowledge Transfer": {
            "role": "Succession readiness. None = tacit knowledge at risk.",
            "required": True,
        },
        "Employee Type": {
            "role": "Structural stability of the role.",
            "required": True,
        },
        "Market Demand for Skill": {
            "role": "External pull. High demand + non-permanent = attrition exposure.",
            "required": True,
        },
    },
    SHEET_DMM: {
        "Programme Name":         {"role": "Identity field for programme-level vitality.", "required": True},
        "Employment Trend":       {"role": "Alignment sub-score (market direction).",      "required": True},
        "Placement Status":       {"role": "Alignment sub-score (outcome strength).",      "required": True},
        "Alumni Relevance":       {"role": "Alignment sub-score (long-tail relevance).",   "required": True},
        "Fees Band":              {"role": "Value score input (cost side).",               "required": True},
        "Salary Band":            {"role": "Value score input (return side).",             "required": True},
        "Curriculum Recency":     {"role": "Adaptation sub-score (freshness).",            "required": True},
        "Revision Trigger":       {"role": "Adaptation sub-score (reason for change).",    "required": True},
        "Employer Engagement":    {"role": "Adaptation sub-score (industry linkage).",     "required": True},
        "Student Experience":     {"role": "Experience score (intake profile).",            "required": True},
        "Startup Signal":         {"role": "Experience score (entrepreneurship pulse).",   "required": True},
        "Degree–Job Alignment":   {"role": "Degree–Job Alignment score. Flags mismatch.",  "required": True},
        "Institutional Contribution": {"role": "Contribution score. Attributes outcome to institution vs external.", "required": True},
        "Delivery Discipline":    {"role": "Teaching Effectiveness sub-score.",            "required": True},
        "Teaching Engagement":    {"role": "Teaching Effectiveness sub-score.",            "required": True},
        "Learning Improvement":   {"role": "Teaching Effectiveness sub-score.",            "required": True},
    },
    SHEET_GPIS_SUPPLY: {
        "Programme Name":  {"role": "Identity of the supply-side unit.",   "required": True},
        "Domain":          {"role": "Supply domain classification.",        "required": True},
        "Geography":       {"role": "Supply geography classification.",     "required": True},
        "Intake Capacity": {"role": "Max seats available (supply).",        "required": True},
        "Actual Intake":   {"role": "Seats actually filled (realised demand capture).", "required": True},
    },
    SHEET_GPIS_DEMAND: {
        "Domain":              {"role": "Demand domain classification.",       "required": True},
        "Geography":           {"role": "Demand geography classification.",    "required": True},
        "Demand Presence":     {"role": "Is there market demand at all?",      "required": True},
        "Employment Strength": {"role": "How strong is that demand?",          "required": True},
    },
}


def columns_for(sheet_name: str):
    """Return the (label, spec) list for a sheet."""
    return {
        SHEET_ICG: ICG_COLUMNS,
        SHEET_DMM: DMM_COLUMNS,
        SHEET_GPIS_SUPPLY: GPIS_SUPPLY_COLUMNS,
        SHEET_GPIS_DEMAND: GPIS_DEMAND_COLUMNS,
    }[sheet_name]


def allowed_values_for(sheet_name: str, column_label: str):
    """Return the allowed-value list for a column, or None if free text / numeric."""
    for label, spec in columns_for(sheet_name):
        if label == column_label:
            if isinstance(spec, list):
                return spec
            return None
    raise KeyError(f"{column_label} not in {sheet_name}")
