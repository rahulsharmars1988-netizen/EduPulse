"""
Generate a sample filled workbook for demo purposes.
Used by the "Download sample case" button and for testing.
"""
from __future__ import annotations

from io import BytesIO
from openpyxl import load_workbook

from .template import build_template_workbook
from .config import (
    SHEET_ICG, SHEET_DMM, SHEET_GPIS_SUPPLY, SHEET_GPIS_DEMAND,
)


ICG_SAMPLE = [
    ["School of Business", "Dr. A. Rao", "Yes", 3, "No", "Within 3 years", "Limited", "Permanent", "High"],
    ["School of Business", "Dr. B. Singh", "No", 5, "Yes", "7+ years", "Active", "Permanent", "Medium"],
    ["School of Business", "Ms. C. Khan", "No", 5, "Yes", "3–7 years", "Active", "Contract", "Medium"],
    ["School of Business", "Mr. D. Patel", "Yes", 2, "No", "3–7 years", "None", "Contract", "High"],
    ["School of Law", "Dr. E. Mehta", "Yes", 2, "Yes", "Within 3 years", "Limited", "Permanent", "Low"],
    ["School of Law", "Ms. F. Roy", "No", 4, "Yes", "7+ years", "Active", "Permanent", "Low"],
    ["School of CS", "Dr. G. Iyer", "Yes", 2, "No", "3–7 years", "None", "Visiting", "High"],
    ["School of CS", "Mr. H. Das", "No", 6, "Yes", "7+ years", "Limited", "Permanent", "High"],
    ["School of CS", "Dr. I. Nair", "No", 6, "Yes", "7+ years", "Active", "Permanent", "High"],
    ["School of Design", "Ms. J. Kapoor", "Yes", 1, "No", "7+ years", "None", "Professor of Practice", "Medium"],
]

DMM_SAMPLE = [
    ["BBA (General)",        "Stable",     "Moderate", "Moderate", "Medium", "Medium", "3–5 years", "Internal",   "Occasional", "Freshers",    "Low",       "Partial Match", "Moderate", "Moderate", "Medium", "Moderate Improvement"],
    ["B.Com (Hons)",         "Stable",     "Moderate", "Moderate", "Low",    "Medium", "3–5 years", "Internal",   "Occasional", "Freshers",    "Low",       "Partial Match", "Moderate", "Moderate", "Medium", "Moderate Improvement"],
    ["BBA (Business Analytics)","Improving","Strong", "High",    "Medium", "High",   "≤2 years", "Industry",    "Annual",     "Freshers",    "Moderate",  "High Match",    "High",     "Strong",   "High",   "Strong Improvement"],
    ["MBA",                  "Improving",  "Strong",   "High",     "High",   "High",   "≤2 years", "Industry",    "Annual",     "Mixed",       "High",      "High Match",    "High",     "Strong",   "High",   "Strong Improvement"],
    ["LLB",                  "Declining",  "Weak",     "Low",      "Medium", "Low",    "5+ years", "None",        "Rare",       "Freshers",    "Low",       "No Match",      "Low",      "Weak",     "Low",    "Limited Improvement"],
    ["BA (Journalism)",      "Declining",  "Weak",     "Low",      "Medium", "Low",    "5+ years", "Internal",    "Rare",       "Freshers",    "Low",       "Partial Match", "Low",      "Moderate", "Medium", "Limited Improvement"],
    ["B.Sc. (Computer Sci.)","Improving",  "Strong",   "High",     "Medium", "High",   "≤2 years", "Industry",    "Annual",     "Mixed",       "High",      "High Match",    "High",     "Strong",   "High",   "Strong Improvement"],
    ["M.Des.",               "Stable",     "Moderate", "Moderate", "High",   "Medium", "3–5 years", "Industry",   "Occasional", "Experienced", "Moderate",  "Partial Match", "Moderate", "Moderate", "Medium", "Moderate Improvement"],
    # Deliberate anti-gaming triggers: strong placement, no degree-job match, low institutional contribution
    ["MBA (Insurance)",      "Improving",  "Strong",   "Moderate", "High",   "Medium", "5+ years", "None",        "Rare",       "Experienced", "Moderate",  "No Match",      "Low",      "Moderate", "Medium", "Moderate Improvement"],
]

GPIS_SUPPLY_SAMPLE = [
    ["BBA (General)",             "Management",             "North India", 120, 90],
    ["B.Com (Hons)",              "Commerce",               "North India", 180, 150],
    ["BBA (Business Analytics)",  "Business Analytics",     "North India", 60,  60],
    ["MBA",                       "Management",             "Pan India",   120, 118],
    ["LLB",                       "Law",                    "North India", 120, 45],
    ["BA (Journalism)",           "Journalism",             "North India", 60,  20],
    ["B.Sc. (Computer Sci.)",     "Computer Science",       "North India", 120, 120],
    ["B.Sc. (Computer Sci.)",     "Computer Science",       "Pan India",   60,  55],
    ["M.Des.",                    "Design",                 "North India", 30,  22],
    ["M.Sc. (Cybersecurity)",     "Cybersecurity",          "Pan India",   60,  58],
]

GPIS_DEMAND_SAMPLE = [
    ["Management",         "North India", "Yes", "Moderate"],
    ["Management",         "Pan India",   "Yes", "High"],
    ["Commerce",           "North India", "Yes", "Moderate"],
    ["Business Analytics", "North India", "Yes", "High"],
    ["Business Analytics", "Pan India",   "Yes", "High"],
    ["Computer Science",   "North India", "Yes", "High"],
    ["Computer Science",   "Pan India",   "Yes", "High"],
    ["Cybersecurity",      "Pan India",   "Yes", "High"],
    ["Design",             "North India", "Yes", "Moderate"],
    ["Law",                "North India", "Yes", "Low"],
    ["Journalism",         "North India", "No",  "Low"],
]


def _fill_sheet(ws, rows):
    for r, row in enumerate(rows, start=2):
        for c, val in enumerate(row, start=1):
            ws.cell(row=r, column=c, value=val)


def sample_case_bytes() -> bytes:
    wb = build_template_workbook()
    _fill_sheet(wb[SHEET_ICG], ICG_SAMPLE)
    _fill_sheet(wb[SHEET_DMM], DMM_SAMPLE)
    _fill_sheet(wb[SHEET_GPIS_SUPPLY], GPIS_SUPPLY_SAMPLE)
    _fill_sheet(wb[SHEET_GPIS_DEMAND], GPIS_DEMAND_SAMPLE)
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


# Variant 2 — a healthier case (for comparison demos)
def sample_case_v2_bytes() -> bytes:
    wb = build_template_workbook()
    icg_v2 = [
        ["School of Business", "Dr. A. Rao", "No", 5, "Yes", "7+ years", "Active", "Permanent", "Medium"],
        ["School of Business", "Dr. B. Singh", "No", 6, "Yes", "7+ years", "Active", "Permanent", "Medium"],
        ["School of Business", "Ms. C. Khan", "No", 5, "Yes", "3–7 years", "Active", "Permanent", "Low"],
        ["School of Business", "Mr. D. Patel", "No", 5, "Yes", "3–7 years", "Active", "Permanent", "Low"],
        ["School of Law", "Dr. E. Mehta", "No", 4, "Yes", "7+ years", "Active", "Permanent", "Low"],
        ["School of CS", "Dr. G. Iyer", "No", 4, "Yes", "3–7 years", "Active", "Permanent", "High"],
        ["School of CS", "Mr. H. Das", "No", 6, "Yes", "7+ years", "Active", "Permanent", "High"],
        ["School of CS", "Dr. I. Nair", "No", 6, "Yes", "7+ years", "Active", "Permanent", "High"],
        ["School of Design", "Ms. J. Kapoor", "No", 3, "Yes", "7+ years", "Active", "Permanent", "Medium"],
    ]
    dmm_v2 = [
        ["BBA (General)",        "Improving", "Strong", "High", "Medium", "High", "≤2 years", "Industry", "Annual", "Mixed", "Moderate", "High Match", "High", "Strong", "High", "Strong Improvement"],
        ["B.Com (Hons)",         "Stable",    "Moderate","High", "Low",    "Medium","≤2 years","Industry","Annual",  "Freshers","Low",    "High Match", "High", "Strong", "High", "Strong Improvement"],
        ["MBA",                  "Improving", "Strong", "High", "High",   "High", "≤2 years", "Industry", "Annual", "Experienced","High","High Match", "High", "Strong", "High", "Strong Improvement"],
        ["B.Sc. (Computer Sci.)","Improving", "Strong", "High", "Medium", "High", "≤2 years", "Industry", "Annual", "Mixed", "High",     "High Match", "High", "Strong", "High", "Strong Improvement"],
        ["M.Des.",               "Stable",    "Moderate","High","High",   "Medium","≤2 years","Industry","Annual",  "Experienced","Moderate","High Match","High","Strong","High","Strong Improvement"],
    ]
    supply_v2 = [
        ["BBA (General)",             "Management",             "North India", 120, 115],
        ["B.Com (Hons)",              "Commerce",               "North India", 120, 115],
        ["MBA",                       "Management",             "Pan India",   120, 120],
        ["B.Sc. (Computer Sci.)",     "Computer Science",       "North India", 120, 120],
        ["M.Des.",                    "Design",                 "North India", 30,  28],
    ]
    demand_v2 = [
        ["Management",        "North India", "Yes", "High"],
        ["Management",        "Pan India",   "Yes", "High"],
        ["Commerce",          "North India", "Yes", "High"],
        ["Computer Science",  "North India", "Yes", "High"],
        ["Design",            "North India", "Yes", "Moderate"],
    ]
    _fill_sheet(wb[SHEET_ICG], icg_v2)
    _fill_sheet(wb[SHEET_DMM], dmm_v2)
    _fill_sheet(wb[SHEET_GPIS_SUPPLY], supply_v2)
    _fill_sheet(wb[SHEET_GPIS_DEMAND], demand_v2)
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()
