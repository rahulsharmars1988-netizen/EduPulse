"""
Integrated EduPulse engine.

Combines the three framework scores into a single institutional-health
score and state. This is NOT an average of subjective ratings — each
framework contributes a deterministic numeric score that is weighted.
"""
from __future__ import annotations

from typing import Dict, Any
from config import EDUPULSE_WEIGHTS, EDUPULSE_THRESHOLDS


def _state_for(score: float) -> str:
    for threshold, label in EDUPULSE_THRESHOLDS:
        if score >= threshold:
            return label
    return EDUPULSE_THRESHOLDS[-1][1]


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
        }

    normalised = weighted_sum / present_weight
    final_state = _state_for(normalised)

    coverages = [r.get("coverage_pct", 0) for r in (icg, dmm, gpis) if r and r.get("available")]
    avg_coverage = sum(coverages) / len(coverages) if coverages else 0

    if missing:
        avg_coverage *= (1 - 0.15 * len(missing))

    if avg_coverage >= 85 and not missing:
        confidence = "High"
    elif avg_coverage >= 60:
        confidence = "Medium"
    else:
        confidence = "Low"

    signed = []
    for k, d in contributions.items():
        if d["score"] is not None:
            delta = d["score"] - normalised
            signed.append((k, delta))
    pulls_down = sorted([(k, v) for k, v in signed if v < 0], key=lambda kv: kv[1])
    pulls_up = sorted([(k, v) for k, v in signed if v > 0], key=lambda kv: kv[1], reverse=True)

    return {
        "available": True,
        "score": round(normalised, 1),
        "state": final_state,
        "confidence": confidence,
        "coverage_pct": round(avg_coverage, 1),
        "contributions": contributions,
        "missing_frameworks": missing,
        "pulls_down": pulls_down,
        "pulls_up": pulls_up,
    }
