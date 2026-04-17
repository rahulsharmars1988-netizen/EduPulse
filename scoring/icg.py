"""
ICG — Institutional Continuity / Faculty System.

Deterministic rule-based scoring. Every faculty row produces a succession
risk score, an attrition risk score, and a combined faculty risk score.
Institution-level state is derived from aggregate risk distribution and
dependency concentration.
"""
from __future__ import annotations

from typing import Dict, Any
import pandas as pd

# ---------------------------------------------------------------------------
# Per-row rule tables
# ---------------------------------------------------------------------------
SOLE_EXPERT_POINTS = {"Yes": 30, "No": 0}
RETIREMENT_POINTS = {"Within 3 years": 30, "3–7 years": 15, "7+ years": 0}
KT_POINTS = {"None": 25, "Limited": 12, "Active": 0}
BACKUP_POINTS = {"No": 15, "Yes": 0}
EMPTYPE_POINTS = {
    "Permanent": 0, "Industry Fellow": 15, "Professor of Practice": 15,
    "Contract": 20, "Visiting": 25,
}
DEMAND_POINTS = {"Low": 0, "Medium": 10, "High": 20}


def _succession_risk(row) -> int:
    return (
        SOLE_EXPERT_POINTS.get(row.get("Sole Expert"), 0)
        + RETIREMENT_POINTS.get(row.get("Retirement Horizon"), 0)
        + KT_POINTS.get(row.get("Knowledge Transfer"), 0)
        + BACKUP_POINTS.get(row.get("Backup Available"), 0)
    )  # max = 100


def _attrition_risk(row) -> int:
    base = (
        EMPTYPE_POINTS.get(row.get("Employee Type"), 0)
        + DEMAND_POINTS.get(row.get("Market Demand for Skill"), 0)
    )  # max = 45
    # compounding: non-permanent staff with high external demand
    if row.get("Employee Type") != "Permanent" and row.get("Market Demand for Skill") == "High":
        base += 10
    # scale to 0-100
    return min(int(base / 55 * 100), 100)


def _risk_level(combined: float) -> str:
    if combined >= 60:
        return "High"
    if combined >= 30:
        return "Medium"
    return "Low"


def score_icg(df: pd.DataFrame) -> Dict[str, Any]:
    """Return the ICG result dict. Expects columns per config.ICG_COLUMNS."""
    if df is None or df.empty:
        return {
            "available": False,
            "reason": "No faculty rows provided.",
        }

    df = df.copy()
    # compute scores
    df["Succession Risk"] = df.apply(_succession_risk, axis=1).astype(int)
    df["Attrition Risk"] = df.apply(_attrition_risk, axis=1).astype(int)
    # combined — weighted toward the higher of the two to reflect worst-case exposure
    df["Combined Risk"] = (0.6 * df[["Succession Risk", "Attrition Risk"]].max(axis=1)
                           + 0.4 * df[["Succession Risk", "Attrition Risk"]].mean(axis=1))
    df["Risk Level"] = df["Combined Risk"].map(_risk_level)

    total = len(df)
    high = int((df["Risk Level"] == "High").sum())
    med = int((df["Risk Level"] == "Medium").sum())
    low = int((df["Risk Level"] == "Low").sum())

    pct_high = high / total * 100
    # dependency concentration: sole-expert with no backup
    sole_no_backup_mask = (df["Sole Expert"] == "Yes") & (df["Backup Available"] == "No")
    sole_no_backup = int(sole_no_backup_mask.sum())
    pct_sole_no_backup = sole_no_backup / total * 100

    # retirement wave
    retire_soon = int((df["Retirement Horizon"] == "Within 3 years").sum())
    pct_retire_soon = retire_soon / total * 100

    # institutional state
    if pct_high >= 30 or pct_sole_no_backup >= 25 or pct_retire_soon >= 25:
        state = "Priority Action"
    elif pct_high >= 15 or pct_sole_no_backup >= 15:
        state = "Vulnerable"
    elif pct_high >= 5 or pct_sole_no_backup >= 5:
        state = "Stable"
    else:
        state = "Resilient"

    # department concentration
    dept_agg = (df.groupby("Department")
                  .agg(Faculty_Count=("Faculty Name", "count"),
                       Avg_Combined_Risk=("Combined Risk", "mean"),
                       High_Risk=("Risk Level", lambda s: (s == "High").sum()),
                       Sole_Experts=("Sole Expert", lambda s: (s == "Yes").sum()))
                  .sort_values("Avg_Combined_Risk", ascending=False))
    dept_agg["Avg_Combined_Risk"] = dept_agg["Avg_Combined_Risk"].round(1)
    dept_agg["High_Risk_%"] = (dept_agg["High_Risk"] / dept_agg["Faculty_Count"] * 100).round(1)

    # key flagged faculty (top 10 by combined risk)
    flagged = (df[["Department", "Faculty Name", "Risk Level",
                   "Succession Risk", "Attrition Risk", "Combined Risk",
                   "Sole Expert", "Backup Available",
                   "Retirement Horizon", "Knowledge Transfer",
                   "Employee Type", "Market Demand for Skill"]]
               .sort_values("Combined Risk", ascending=False)
               .head(10)
               .reset_index(drop=True))
    flagged["Combined Risk"] = flagged["Combined Risk"].round(1)

    # key drivers (human-readable)
    drivers = []
    if pct_sole_no_backup >= 10:
        drivers.append(f"{pct_sole_no_backup:.0f}% of faculty are sole experts without a backup.")
    if pct_retire_soon >= 15:
        drivers.append(f"{pct_retire_soon:.0f}% of faculty are within 3 years of retirement.")
    kt_gap = (df["Knowledge Transfer"] == "None").sum()
    if kt_gap:
        drivers.append(f"{kt_gap} role(s) show no active knowledge-transfer practice.")
    nonperm_hi = ((df["Employee Type"] != "Permanent") & (df["Market Demand for Skill"] == "High")).sum()
    if nonperm_hi:
        drivers.append(f"{nonperm_hi} non-permanent role(s) operate in high-demand skill markets (attrition exposure).")

    # coverage: % of required fields filled
    required_cols = ["Sole Expert", "Backup Available", "Retirement Horizon",
                     "Knowledge Transfer", "Employee Type", "Market Demand for Skill"]
    filled = df[required_cols].notna().sum().sum()
    coverage = filled / (len(df) * len(required_cols)) * 100

    return {
        "available": True,
        "state": state,
        "score": round(_state_to_score(state, pct_high, pct_sole_no_backup), 1),
        "faculty_count": total,
        "high_risk_count": high,
        "medium_risk_count": med,
        "low_risk_count": low,
        "pct_high_risk": round(pct_high, 1),
        "pct_sole_no_backup": round(pct_sole_no_backup, 1),
        "pct_retire_soon": round(pct_retire_soon, 1),
        "dept_concentration": dept_agg.reset_index(),
        "flagged_faculty": flagged,
        "key_drivers": drivers,
        "coverage_pct": round(coverage, 1),
        "detail_df": df,
    }


def _state_to_score(state: str, pct_high: float, pct_sole_no_backup: float) -> float:
    """Smooth numeric score — used for the integrated EduPulse calculation."""
    # base anchor
    base = {"Resilient": 88, "Stable": 72, "Vulnerable": 50, "Priority Action": 28}[state]
    # adjust within the band by risk density
    penalty = 0.3 * pct_high + 0.2 * pct_sole_no_backup
    score = max(0.0, min(100.0, base - penalty * 0.2))
    return score
