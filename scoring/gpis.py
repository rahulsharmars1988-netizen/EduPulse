"""
GPIS — Geo-Pedagogical / Market Alignment System.

Matches supply rows (programme × domain × geography × capacity × actual
intake) against demand rows (domain × geography × demand presence ×
employment strength). Per-row alignment state rolls up to an institutional
state via seat-weighted aggregation.
"""
from __future__ import annotations

from typing import Dict, Any
import pandas as pd

EMP_STRENGTH_SCORE = {"High": 100, "Moderate": 60, "Low": 25}


def _utilization(row) -> float:
    cap = row.get("Intake Capacity")
    act = row.get("Actual Intake")
    if cap is None or cap == 0 or pd.isna(cap):
        return 0.0
    if act is None or pd.isna(act):
        return 0.0
    return float(act) / float(cap) * 100


def _classify(demand_presence, emp_strength, util) -> str:
    """Map a supply row to one of the six GPIS states."""
    if demand_presence != "Yes":
        return "Mismatch"

    if emp_strength == "High":
        if util >= 100:
            return "Undersupply"      # demand strong, we're at/over capacity — room to expand
        if util >= 70:
            return "Strong Alignment"
        if util >= 40:
            return "Weak Alignment"   # demand exists, we're failing to fill
        return "Weak Alignment"
    if emp_strength == "Moderate":
        if 50 <= util <= 100:
            return "Approximate Alignment"
        if util > 100:
            return "Approximate Alignment"
        return "Weak Alignment"
    # Low employment strength
    if util < 30:
        return "Oversupply"           # low demand and we can't fill anyway
    return "Oversupply"


def _row_score(state: str, util: float) -> float:
    base = {
        "Strong Alignment": 88, "Approximate Alignment": 72,
        "Undersupply": 60, "Weak Alignment": 42,
        "Oversupply": 32, "Mismatch": 18,
    }[state]
    # minor adjustment for extreme under-utilization
    if state == "Weak Alignment" and util < 40:
        base -= 5
    return max(0, min(100, base))


def score_gpis(supply: pd.DataFrame, demand: pd.DataFrame) -> Dict[str, Any]:
    if supply is None or supply.empty:
        return {"available": False, "reason": "No supply rows provided."}
    if demand is None or demand.empty:
        return {"available": False, "reason": "No demand rows provided."}

    supply = supply.copy().reset_index(drop=True)
    demand = demand.copy()
    # build a lookup map: (Domain, Geography) -> (presence, strength)
    demand_map = {}
    for _, d in demand.iterrows():
        key = (d.get("Domain"), d.get("Geography"))
        demand_map[key] = (d.get("Demand Presence"), d.get("Employment Strength"))

    rows = []
    for _, s in supply.iterrows():
        key = (s.get("Domain"), s.get("Geography"))
        # Geography fallback: if specific India geography not in demand, try Pan India
        presence, strength = demand_map.get(key, (None, None))
        if presence is None:
            pan_key = (s.get("Domain"), "Pan India")
            presence, strength = demand_map.get(pan_key, (None, None))
        if presence is None:
            # no demand record at all for this domain-geo → treat as Mismatch
            presence, strength = "No", "Low"
        util = _utilization(s)
        state = _classify(presence, strength, util)
        rows.append({
            "Programme Name": s.get("Programme Name"),
            "Domain": s.get("Domain"),
            "Geography": s.get("Geography"),
            "Intake Capacity": s.get("Intake Capacity") or 0,
            "Actual Intake": s.get("Actual Intake") or 0,
            "Utilization %": round(util, 1),
            "Demand Presence": presence,
            "Employment Strength": strength,
            "State": state,
            "Score": round(_row_score(state, util), 1),
        })
    per_row = pd.DataFrame(rows)

    # seat-weighted aggregate (weight by Intake Capacity; fall back to row count)
    weights = per_row["Intake Capacity"].astype(float)
    if weights.sum() == 0:
        weights = pd.Series([1] * len(per_row))
    overall_score = float((per_row["Score"] * weights).sum() / weights.sum())

    # state distribution
    state_dist = per_row.groupby("State").agg(
        Rows=("State", "count"),
        Seats=("Intake Capacity", "sum"),
        Filled=("Actual Intake", "sum"),
    ).reindex(["Strong Alignment", "Approximate Alignment", "Undersupply",
               "Weak Alignment", "Oversupply", "Mismatch"], fill_value=0)
    state_dist["Seat %"] = (state_dist["Seats"] / max(state_dist["Seats"].sum(), 1) * 100).round(1)

    # institution state logic
    seat_pct = state_dist["Seat %"].to_dict()
    good = seat_pct.get("Strong Alignment", 0) + seat_pct.get("Approximate Alignment", 0)
    mismatch = seat_pct.get("Mismatch", 0)
    oversupply = seat_pct.get("Oversupply", 0)
    undersupply = seat_pct.get("Undersupply", 0)

    if good >= 70 and mismatch < 10:
        overall_state = "Strong Alignment"
    elif good >= 50 and mismatch < 20:
        overall_state = "Approximate Alignment"
    elif mismatch >= 30:
        overall_state = "Mismatch"
    elif oversupply >= 30:
        overall_state = "Oversupply"
    elif undersupply >= 30 and good >= 30:
        overall_state = "Undersupply"
    else:
        overall_state = "Weak Alignment"

    # summary drivers
    drivers = []
    if mismatch > 0:
        drivers.append(f"{mismatch:.0f}% of seats sit in domain–geography pairs with no demand signal.")
    if oversupply > 0:
        drivers.append(f"{oversupply:.0f}% of seats sit in areas with low employment strength.")
    if undersupply > 0:
        drivers.append(f"{undersupply:.0f}% of seats are in strong-demand areas operating at or above capacity.")
    if good > 0:
        drivers.append(f"{good:.0f}% of seats are well-aligned with demand.")

    under_util = per_row[per_row["Utilization %"] < 50]
    if not under_util.empty:
        drivers.append(f"{len(under_util)} supply row(s) operate below 50% utilization.")

    coverage = per_row[["Demand Presence", "Employment Strength"]].notna().sum().sum()
    total_cells = len(per_row) * 2
    coverage_pct = coverage / max(total_cells, 1) * 100

    return {
        "available": True,
        "state": overall_state,
        "score": round(overall_score, 1),
        "per_row": per_row,
        "state_distribution": state_dist.reset_index(),
        "key_drivers": drivers,
        "coverage_pct": round(coverage_pct, 1),
        "underutilized_rows": under_util.reset_index(drop=True),
    }
