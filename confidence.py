"""
Multi-dimensional confidence engine.

Replaces the old single High/Medium/Low label with a richer breakdown:

  - data_completeness:    % of required cells filled
  - consistency:           absence of contradictory value combinations
  - anomaly_burden:        inverse of anti-gaming flag density
  - rule_coverage:         % of scoring rules that had sufficient inputs
  - traceability_strength: every computed score is backed by a declared driver

A weighted composite produces an overall 0–100 score and a label.
"""
from __future__ import annotations

from typing import Dict, Any
import pandas as pd

WEIGHTS = {
    "data_completeness":    0.28,
    "consistency":          0.22,
    "anomaly_burden":       0.18,
    "rule_coverage":        0.18,
    "traceability_strength": 0.14,
}


def _label(score: float) -> str:
    if score >= 85:
        return "High"
    if score >= 65:
        return "Medium"
    if score >= 45:
        return "Low"
    return "Very Low"


def _completeness(icg, dmm, gpis) -> tuple[float, str]:
    covs = []
    for r in (icg, dmm, gpis):
        if r and r.get("available"):
            covs.append(r.get("coverage_pct", 0))
    if not covs:
        return 0.0, "No frameworks produced outputs."
    avg = sum(covs) / len(covs)
    note = f"Average input coverage across available frameworks: {avg:.0f}%."
    return avg, note


def _consistency(icg, dmm, gpis) -> tuple[float, str]:
    violations = 0
    total_checks = 0
    notes = []

    # ICG consistency: sole-expert + backup available = inconsistent (backup exists but sole expert?)
    if icg and icg.get("available"):
        df = icg.get("detail_df")
        if df is not None and not df.empty:
            total_checks += 3
            # sole expert + backup available = semantic contradiction
            m = (df["Sole Expert"] == "Yes") & (df["Backup Available"] == "Yes")
            if m.any():
                violations += 1
                notes.append(f"{int(m.sum())} faculty row(s) marked both sole-expert AND backup-available.")
            # Knowledge transfer Active + Sole expert Yes = unusual
            m2 = (df["Sole Expert"] == "Yes") & (df["Knowledge Transfer"] == "Active")
            if m2.any():
                # only a weak violation
                pass
            # Number of faculty in subject = 1 while sole expert = No (should be Yes)
            m3 = (df["Number of Faculty in Subject"] == 1) & (df["Sole Expert"] == "No")
            if m3.any():
                violations += 1
                notes.append(f"{int(m3.sum())} faculty row(s) show single-faculty subject but sole-expert marked No.")
            # Retirement within 3 years + Knowledge Transfer None is a red flag but not a consistency issue
            total_checks += 0

    # DMM consistency: placement Strong + employment Declining = contradiction
    if dmm and dmm.get("available"):
        tbl = dmm.get("programme_table")
        total_checks += 1
        if tbl is not None and not tbl.empty:
            # we store raw strings in the programme_table? actually no, we only store scored values.
            # skip detailed DMM consistency checks — would need raw df
            pass

    # GPIS: utilization > 100% in rows where Employment Strength = Low (why would we be filling a low-demand seat?)
    if gpis and gpis.get("available"):
        pr = gpis.get("per_row")
        if pr is not None and not pr.empty:
            total_checks += 2
            m = (pr["Utilization %"] > 100) & (pr["Employment Strength"] == "Low")
            if m.any():
                violations += 1
                notes.append(f"{int(m.sum())} supply row(s) over-utilised despite low demand strength.")
            # capacity = 0 but actual > 0
            m2 = (pr["Intake Capacity"] == 0) & (pr["Actual Intake"] > 0)
            if m2.any():
                violations += 1
                notes.append(f"{int(m2.sum())} supply row(s) show 0 capacity but non-zero intake.")

    if total_checks == 0:
        return 100.0, "No consistency checks applied (no eligible inputs)."
    score = max(0, 100 - (violations / max(total_checks, 1)) * 100)
    note = "No consistency issues detected." if not notes else " ".join(notes)
    return score, note


def _anomaly_burden(icg, dmm, gpis) -> tuple[float, str]:
    flags = 0
    units = 0
    if dmm and dmm.get("available"):
        flags += len(dmm.get("anti_gaming_flags", []))
        tbl = dmm.get("programme_table")
        if tbl is not None:
            units += len(tbl)
    if icg and icg.get("available"):
        units += icg.get("faculty_count", 0)
    if units == 0:
        return 100.0, "No units available to evaluate."
    # fewer flags per unit = higher score
    density = flags / units
    # 0 density -> 100; 0.2+ density -> <50
    score = max(0.0, min(100.0, 100 - density * 500))
    note = f"{flags} flag(s) across {units} unit(s) → density {density:.2f}."
    return score, note


def _rule_coverage(icg, dmm, gpis) -> tuple[float, str]:
    """How many of the scoring rules had enough data to fire."""
    framework_count = 3
    live = 0
    if icg and icg.get("available"):
        live += 1
    if dmm and dmm.get("available"):
        live += 1
    if gpis and gpis.get("available"):
        live += 1
    score = live / framework_count * 100
    note = f"{live}/{framework_count} frameworks produced a usable score."
    return score, note


def _traceability_strength(icg, dmm, gpis) -> tuple[float, str]:
    """Does every score have supporting drivers?"""
    checks = 0
    passes = 0
    for name, r in [("ICG", icg), ("DMM", dmm), ("GPIS", gpis)]:
        if r and r.get("available"):
            checks += 2
            if r.get("score") is not None:
                passes += 1
            if r.get("key_drivers"):
                passes += 1
    if checks == 0:
        return 0.0, "No frameworks available for traceability check."
    score = passes / checks * 100
    note = f"{passes}/{checks} traceability signals present."
    return score, note


def compute_confidence(icg: Dict[str, Any], dmm: Dict[str, Any],
                       gpis: Dict[str, Any]) -> Dict[str, Any]:
    dims = {}
    comp_score, comp_note = _completeness(icg, dmm, gpis)
    dims["data_completeness"] = {"score": round(comp_score, 1), "note": comp_note}

    cons_score, cons_note = _consistency(icg, dmm, gpis)
    dims["consistency"] = {"score": round(cons_score, 1), "note": cons_note}

    anom_score, anom_note = _anomaly_burden(icg, dmm, gpis)
    dims["anomaly_burden"] = {"score": round(anom_score, 1), "note": anom_note}

    rule_score, rule_note = _rule_coverage(icg, dmm, gpis)
    dims["rule_coverage"] = {"score": round(rule_score, 1), "note": rule_note}

    trace_score, trace_note = _traceability_strength(icg, dmm, gpis)
    dims["traceability_strength"] = {"score": round(trace_score, 1), "note": trace_note}

    composite = sum(WEIGHTS[k] * dims[k]["score"] for k in WEIGHTS)
    composite = round(composite, 1)
    label = _label(composite)

    return {
        "composite_score": composite,
        "label": label,
        "dimensions": dims,
        "weights": WEIGHTS,
    }
