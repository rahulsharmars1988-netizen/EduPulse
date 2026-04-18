"""
Integrated EduPulse engine.

Combines the three framework scores into a single institutional-health
score and state. This is NOT an average of subjective ratings — each
framework contributes a deterministic numeric score that is weighted.

v1.2 — non-compensatory logic:
  * Critical thresholds penalise the weighted average (ICG<30, DMM<40, GPIS<40).
  * State overrides: ICG<30 → "At Risk"; 2+ frameworks critical → "Fragile".
  * Healthy ceiling: if ICG<30, the integrated state can never be Healthy/Thriving.
"""
from __future__ import annotations

from typing import Dict, Any
from ..config import EDUPULSE_WEIGHTS, EDUPULSE_THRESHOLDS


# Non-compensatory thresholds
CRITICAL_ICG = 30.0
CRITICAL_DMM = 40.0
CRITICAL_GPIS = 40.0

# Penalty points subtracted from the weighted score when a framework is critical
PENALTY_ICG = 12.0
PENALTY_DMM = 8.0
PENALTY_GPIS = 6.0


def _state_for(score: float) -> str:
    for threshold, label in EDUPULSE_THRESHOLDS:
        if score >= threshold:
            return label
    return EDUPULSE_THRESHOLDS[-1][1]


def _apply_penalties(icg, dmm, gpis) -> tuple[float, list[dict]]:
    """Return (total_penalty, list_of_penalty_records)."""
    total = 0.0
    records: list[dict] = []

    if icg and icg.get("available") and icg.get("score") is not None and icg["score"] < CRITICAL_ICG:
        total += PENALTY_ICG
        records.append({
            "framework": "ICG", "score": icg["score"],
            "threshold": CRITICAL_ICG, "penalty": PENALTY_ICG,
            "reason": f"ICG score {icg['score']:.1f} below critical threshold {CRITICAL_ICG:.0f}.",
        })
    if dmm and dmm.get("available") and dmm.get("score") is not None and dmm["score"] < CRITICAL_DMM:
        total += PENALTY_DMM
        records.append({
            "framework": "DMM", "score": dmm["score"],
            "threshold": CRITICAL_DMM, "penalty": PENALTY_DMM,
            "reason": f"DMM score {dmm['score']:.1f} below critical threshold {CRITICAL_DMM:.0f}.",
        })
    if gpis and gpis.get("available") and gpis.get("score") is not None and gpis["score"] < CRITICAL_GPIS:
        total += PENALTY_GPIS
        records.append({
            "framework": "GPIS", "score": gpis["score"],
            "threshold": CRITICAL_GPIS, "penalty": PENALTY_GPIS,
            "reason": f"GPIS score {gpis['score']:.1f} below critical threshold {CRITICAL_GPIS:.0f}.",
        })
    return total, records


def _state_override(icg, dmm, gpis, base_state: str) -> tuple[str, str | None]:
    """
    Apply non-compensatory state overrides.
    Returns (final_state, reason_or_None).
    """
    # Count critical frameworks
    critical = []
    if icg and icg.get("available") and icg.get("score") is not None and icg["score"] < CRITICAL_ICG:
        critical.append("ICG")
    if dmm and dmm.get("available") and dmm.get("score") is not None and dmm["score"] < CRITICAL_DMM:
        critical.append("DMM")
    if gpis and gpis.get("available") and gpis.get("score") is not None and gpis["score"] < CRITICAL_GPIS:
        critical.append("GPIS")

    # Rule 1: 2+ frameworks critical → Fragile (unless already worse, i.e. Critical)
    if len(critical) >= 2:
        if base_state == "Critical":
            return "Critical", (
                f"{len(critical)} frameworks below critical thresholds ({', '.join(critical)}); "
                f"integrated score remains in the Critical band."
            )
        return "Fragile", (
            f"{len(critical)} frameworks below critical thresholds ({', '.join(critical)}); "
            f"overall state forced to Fragile regardless of weighted score."
        )

    # Rule 2: ICG<30 alone → cannot be Healthy/Thriving; floor is "At Risk"
    if "ICG" in critical:
        if base_state in ("Thriving", "Healthy"):
            return "At Risk", (
                f"ICG score below {CRITICAL_ICG:.0f} blocks a Healthy/Thriving rating; "
                f"overall state capped at At Risk."
            )
        if base_state == "Stretched":
            return "At Risk", (
                f"ICG score below {CRITICAL_ICG:.0f} — continuity failure dominates the "
                f"integrated reading; state elevated to At Risk."
            )
        # Fragile / Critical already reflect worse positions; keep them.
        return base_state, (
            f"ICG below {CRITICAL_ICG:.0f} acknowledged; "
            f"base state {base_state} already reflects continuity failure."
        )

    return base_state, None


def integrate_edupulse(icg: Dict[str, Any], dmm: Dict[str, Any], gpis: Dict[str, Any]) -> Dict[str, Any]:
    contributions = {}
    present_weight = 0.0
    weighted_sum = 0.0
    missing = []

    for key, res in [("ICG", icg), ("DMM", dmm), ("GPIS", gpis)]:
        w = EDUPULSE_WEIGHTS[key]
        if res and res.get("available"):
            contributions[key] = {
                "weight": w,
                "score": res["score"],
                "state": res["state"],
                "contribution": round(w * res["score"], 2),
            }
            weighted_sum += w * res["score"]
            present_weight += w
        else:
            missing.append(key)
            contributions[key] = {"weight": w, "score": None, "state": None, "contribution": None}

    if present_weight == 0:
        return {
            "available": False,
            "reason": "No framework produced a usable score.",
            "contributions": contributions,
            "missing": missing,
            "penalties": [],
            "penalty_total": 0.0,
            "raw_score": None,
            "override_reason": None,
        }

    # Normalised weighted score (against available weight)
    raw_normalised = weighted_sum / present_weight

    # Apply non-compensatory penalties
    penalty_total, penalty_records = _apply_penalties(icg, dmm, gpis)
    penalised = max(0.0, raw_normalised - penalty_total)

    # Base state from penalised score
    base_state = _state_for(penalised)

    # Apply state overrides
    final_state, override_reason = _state_override(icg, dmm, gpis, base_state)

    # Confidence: coverage-weighted
    coverages = [r.get("coverage_pct", 0) for r in (icg, dmm, gpis) if r and r.get("available")]
    avg_coverage = sum(coverages) / len(coverages) if coverages else 0

    # Framework presence penalty for confidence
    if missing:
        avg_coverage *= (1 - 0.15 * len(missing))

    if avg_coverage >= 85 and not missing:
        confidence = "High"
    elif avg_coverage >= 60:
