"""
DMM — Programme Vitality / Outcome System.

Seven sub-scores per programme on a 0–100 scale, then a weighted overall
DMM score. Final state bucketed into Anabolic / Transitional / Static /
Catabolic. Anti-gaming flags capture placement-without-alignment and
outcome-without-contribution patterns.
"""
from __future__ import annotations

from typing import Dict, Any, List
import pandas as pd

# ---------------------------------------------------------------------------
# Per-field rule tables
# ---------------------------------------------------------------------------
EMPLOYMENT_TREND = {"Improving": 100, "Stable": 60, "Declining": 20}
PLACEMENT_STATUS = {"Strong": 100, "Moderate": 60, "Weak": 25, "NA": 50}
ALUMNI = {"High": 100, "Moderate": 60, "Low": 25}

CURRICULUM = {"≤2 years": 100, "3–5 years": 60, "5+ years": 20}
REVISION = {"Industry": 100, "Compliance": 65, "Internal": 50, "None": 10}
EMPLOYER_ENG = {"Annual": 100, "Occasional": 55, "Rare": 20}

STUDENT_EXP = {"Experienced": 90, "Mixed": 65, "Freshers": 45}
STARTUP = {"High": 100, "Moderate": 60, "Low": 25, "NA": 50}

DJA = {"High Match": 100, "Partial Match": 55, "No Match": 15}
CONTRIBUTION = {"High": 100, "Moderate": 55, "Low": 15}

DELIVERY = {"Strong": 100, "Moderate": 60, "Weak": 25}
TEACH_ENG = {"High": 100, "Medium": 60, "Low": 25}
LEARN_IMP = {"Strong Improvement": 100, "Moderate Improvement": 60, "Limited Improvement": 25}

# value matrix: rows = fees band (Low/Med/High), cols = salary band (Low/Med/High)
VALUE_MATRIX = {
    ("Low", "Low"): 55, ("Low", "Medium"): 80, ("Low", "High"): 100,
    ("Medium", "Low"): 30, ("Medium", "Medium"): 60, ("Medium", "High"): 85,
    ("High", "Low"): 10, ("High", "Medium"): 40, ("High", "High"): 65,
}

# overall weights (sum = 1)
DMM_WEIGHTS = {
    "Alignment": 0.20,
    "Adaptation": 0.15,
    "Experience": 0.05,
    "Value": 0.10,
    "Degree-Job Alignment": 0.15,
    "Contribution": 0.15,
    "Teaching Effectiveness": 0.20,
}


def _avg(values: List[float]) -> float:
    vals = [v for v in values if v is not None]
    return sum(vals) / len(vals) if vals else 0.0


def _lookup(table, key, default=None):
    return table.get(key, default) if key is not None else default


def _row_scores(row) -> Dict[str, float]:
    alignment = _avg([
        _lookup(EMPLOYMENT_TREND, row.get("Employment Trend")),
        _lookup(PLACEMENT_STATUS, row.get("Placement Status")),
        _lookup(ALUMNI, row.get("Alumni Relevance")),
    ])
    adaptation = _avg([
        _lookup(CURRICULUM, row.get("Curriculum Recency")),
        _lookup(REVISION, row.get("Revision Trigger")),
        _lookup(EMPLOYER_ENG, row.get("Employer Engagement")),
    ])
    experience = _avg([
        _lookup(STUDENT_EXP, row.get("Student Experience")),
        _lookup(STARTUP, row.get("Startup Signal")),
    ])
    value = VALUE_MATRIX.get((row.get("Fees Band"), row.get("Salary Band")), 50.0)
    dja = _lookup(DJA, row.get("Degree–Job Alignment"), 50.0)
    contribution = _lookup(CONTRIBUTION, row.get("Institutional Contribution"), 50.0)
    teaching = _avg([
        _lookup(DELIVERY, row.get("Delivery Discipline")),
        _lookup(TEACH_ENG, row.get("Teaching Engagement")),
        _lookup(LEARN_IMP, row.get("Learning Improvement")),
    ])

    return {
        "Alignment": alignment,
        "Adaptation": adaptation,
        "Experience": experience,
        "Value": value,
        "Degree-Job Alignment": dja,
        "Contribution": contribution,
        "Teaching Effectiveness": teaching,
    }


def _overall(subs: Dict[str, float]) -> float:
    return sum(DMM_WEIGHTS[k] * subs[k] for k in DMM_WEIGHTS)


def _state_for(score: float) -> str:
    if score >= 72:
        return "Anabolic"
    if score >= 55:
        return "Transitional"
    if score >= 40:
        return "Static"
    return "Catabolic"


def _anti_gaming(row, subs) -> List[dict]:
    """
    Produce richly-structured anti-gaming flag objects.

    Each flag: {category, severity, affected_unit, reason, suggested_action, visibility}
    visibility is always 'internal_only' — external reports must never leak raw flags.
    """
    flags: List[dict] = []
    prog = row.get("Programme Name", "—")

    def f(category, severity, reason, suggested_action):
        flags.append({
            "category": category,
            "severity": severity,
            "affected_unit": prog,
            "reason": reason,
            "suggested_action": suggested_action,
            "visibility": "internal_only",
        })

    if row.get("Placement Status") == "Strong" and row.get("Degree–Job Alignment") == "No Match":
        f("Degree–Job Attribution", "High",
          "Strong placement recorded despite no degree-to-job alignment.",
          "Audit placement records to determine whether outcomes map to programme intent; reposition if systemic.")

    if row.get("Placement Status") == "Strong" and row.get("Institutional Contribution") == "Low":
        f("Outcome Attribution", "High",
          "Strong outcomes with low declared institutional contribution.",
          "Document what the institution specifically contributed before publishing outcome claims.")

    if row.get("Student Experience") == "Experienced" and row.get("Placement Status") == "Strong":
        f("Experience Attribution", "Medium",
          "Experienced intake with strong placement — outcome may reflect prior experience rather than programme.",
          "Report value-added separately from raw placement where intake skews experienced.")

    if row.get("Salary Band") == "Low" and row.get("Fees Band") == "High":
        f("Cost–Value Gap", "Medium",
          "High fee band combined with low salary band indicates a fragile value proposition.",
          "Review fee positioning or invest in outcome uplift before next admission cycle.")

    if row.get("Curriculum Recency") == "5+ years" and row.get("Employment Trend") == "Improving":
        f("Curriculum Lag", "Medium",
          "Stale curriculum despite improving employment — a gap is likely forming.",
          "Schedule a curriculum revision cycle before outcomes disconnect from content.")

    if (subs["Contribution"] < 30) and (subs["Alignment"] > 70):
        f("Attribution Concern", "High",
          "High alignment not backed by institutional contribution.",
          "Validate whether outcomes are programme-led or market-led; separate the two in reporting.")

    if row.get("Revision Trigger") == "None" and row.get("Curriculum Recency") != "≤2 years":
        f("Revision Discipline", "Low",
          "No revision trigger declared for an older curriculum.",
          "Adopt an explicit revision cadence (industry/internal/compliance).")

    if row.get("Employer Engagement") == "Rare" and row.get("Placement Status") == "Strong":
        f("Engagement Gap", "Medium",
          "Strong placement without routine employer engagement is structurally brittle.",
          "Build formal employer interactions before outcomes soften.")

    return flags


def score_dmm(df: pd.DataFrame) -> Dict[str, Any]:
    if df is None or df.empty:
        return {"available": False, "reason": "No programmes provided."}

    df = df.copy().reset_index(drop=True)
    sub_rows = []
    overalls = []
    states = []
    flags_all = []
    for _, row in df.iterrows():
        subs = _row_scores(row)
        overall = _overall(subs)
        overalls.append(overall)
        states.append(_state_for(overall))
        sub_rows.append(subs)
        flags_all.append(_anti_gaming(row, subs))

    subs_df = pd.DataFrame(sub_rows).round(1)
    prog_result = pd.concat([df[["Programme Name"]].reset_index(drop=True), subs_df], axis=1)
    prog_result["DMM Score"] = [round(x, 1) for x in overalls]
    prog_result["DMM State"] = states
    prog_result["Flags"] = [
        "; ".join(f"[{f['severity']}] {f['category']}" for f in fl) if fl else ""
        for fl in flags_all
    ]

    # institution aggregate
    mean_score = round(sum(overalls) / len(overalls), 1)
    overall_state = _state_for(mean_score)

    # drivers: lowest sub-scores overall
    sub_means = subs_df.mean().round(1).to_dict()
    weakest = sorted(sub_means.items(), key=lambda kv: kv[1])[:3]
    strongest = sorted(sub_means.items(), key=lambda kv: kv[1], reverse=True)[:3]

    # catabolic / static programmes (action list)
    critical_progs = prog_result[prog_result["DMM State"].isin(["Catabolic", "Static"])]
    anabolic_progs = prog_result[prog_result["DMM State"] == "Anabolic"]

    # coverage
    required_cols = [lbl for lbl, _ in [
        ("Employment Trend", None), ("Placement Status", None), ("Alumni Relevance", None),
        ("Fees Band", None), ("Salary Band", None),
        ("Curriculum Recency", None), ("Revision Trigger", None), ("Employer Engagement", None),
        ("Student Experience", None), ("Startup Signal", None),
        ("Degree–Job Alignment", None), ("Institutional Contribution", None),
        ("Delivery Discipline", None), ("Teaching Engagement", None), ("Learning Improvement", None),
    ]]
    filled = df[required_cols].notna().sum().sum()
    coverage = filled / (len(df) * len(required_cols)) * 100

    drivers_text = []
    for name, val in weakest:
        drivers_text.append(f"Weakest sub-score: {name} ({val:.0f}/100).")
    for name, val in strongest[:1]:
        drivers_text.append(f"Strongest sub-score: {name} ({val:.0f}/100).")
    all_flags = [f for flist in flags_all for f in flist]
    if all_flags:
        high_sev = sum(1 for f in all_flags if f["severity"] == "High")
        drivers_text.append(
            f"{len(all_flags)} anti-gaming flag(s) across programmes "
            f"({high_sev} high-severity)."
        )

    return {
        "available": True,
        "state": overall_state,
        "score": mean_score,
        "programme_table": prog_result,
        "sub_means": sub_means,
        "strongest": strongest,
        "weakest": weakest,
        "critical_programmes": critical_progs.reset_index(drop=True),
        "anabolic_programmes": anabolic_progs.reset_index(drop=True),
        "anti_gaming_flags": all_flags,
        "key_drivers": drivers_text,
        "coverage_pct": round(coverage, 1),
    }
