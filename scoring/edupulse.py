"""
Integrated EduPulse engine.

v1.2.1 — proportional penalties + score ceilings, override caps only.
"""
from __future__ import annotations

from typing import Dict, Any
from ..config import EDUPULSE_WEIGHTS, EDUPULSE_THRESHOLDS


CRITICAL_ICG = 30.0
CRITICAL_DMM = 40.0
CRITICAL_GPIS = 40.0

PENALTY_FACTOR_ICG = 0.4
PENALTY_FACTOR_DMM = 0.25
PENALTY_FACTOR_GPIS = 0.2

CEILING_ICG_CRITICAL = 55.0
CEILING_MULTI_CRITICAL = 45.0


def _state_for(score: float) -> str:
    for threshold, label in EDUPULSE_THRESHOLDS:
        if score >= threshold:
            return label
    return EDUPULSE_THRESHOLDS[-1][1]


def _apply_penalties(icg, dmm, gpis) -> tuple[float, list[dict]]:
    total = 0.0
    records: list[dict] = []

    if icg and icg.get("available") and icg.get("score") is not None and icg["score"] < CRITICAL_ICG:
        p = (CRITICAL_ICG - icg["score"]) * PENALTY_FACTOR_ICG
        total += p
        records.append({
            "framework": "ICG", "score": icg["score"],
            "threshold": CRITICAL_ICG, "penalty": round(p, 2),
            "reason": f"ICG score {icg['score']:.1f} below critical threshold {CRITICAL_ICG:.0f}.",
        })
    if dmm and dmm.get("available") and dmm.get("score") is not None and dmm["score"] < CRITICAL_DMM:
        p = (CRITICAL_DMM - dmm["score"]) * PENALTY_FACTOR_DMM
        total += p
        records.append({
            "framework": "DMM", "score": dmm["score"],
            "threshold": CRITICAL_DMM, "penalty": round(p, 2),
            "reason": f"DMM score {dmm['score']:.1f} below critical threshold {CRITICAL_DMM:.0f}.",
        })
    if gpis and gpis.get("available") and gpis.get("score") is not None and gpis["score"] < CRITICAL_GPIS:
        p = (CRITICAL_GPIS - gpis["score"]) * PENALTY_FACTOR_GPIS
        total += p
        records.append({
            "framework": "GPIS", "score": gpis["score"],
            "threshold": CRITICAL_GPIS, "penalty": round(p, 2),
            "reason": f"GPIS score {gpis['score']:.1f} below critical threshold {CRITICAL_GPIS:.0f}.",
        })
    return total, records


def _count_critical(icg, dmm, gpis) -> list[str]:
    critical = []
    if icg and icg.get("available") and icg.get("score") is not None and icg["score"] < CRITICAL_ICG:
        critical.append("ICG")
    if dmm and dmm.get("available") and dmm.get("score") is not None and dmm["score"] < CRITICAL_DMM:
        critical.append("DMM")
    if gpis and gpis.get("available") and gpis.get("score") is not None and gpis["score"] < CRITICAL_GPIS:
        critical.append("GPIS")
    return critical


def _apply_ceilings(score: float, critical: list[str]) -> tuple[float, str | None]:
    ceiling_reason = None
    if len(critical) >= 2 and score > CEILING_MULTI_CRITICAL:
        ceiling_reason = (
            f"{len(critical)} frameworks below critical thresholds "
            f"({', '.join(critical)}); integrated score capped at {CEILING_MULTI_CRITICAL:.0f}."
        )
        score = CEILING_MULTI_CRITICAL
    elif "ICG" in critical and score > CEILING_ICG_CRITICAL:
        ceiling_reason = (
            f"ICG score below {CRITICAL_ICG:.0f}; integrated score capped at "
            f"{CEILING_ICG_CRITICAL:.0f} to reflect continuity failure."
        )
        score = CEILING_ICG_CRITICAL
    return score, ceiling_reason


def _state_override(critical: list[str], base_state: str) -> tuple[str, str | None]:
    if len(critical) >= 2:
        if base_state in ("Thriving", "Healthy", "Stretched"):
            return "Fragile", (
                f"{len(critical)} frameworks below critical thresholds "
                f"({', '.join(critical)}); state capped at Fragile."
            )
        return base_state, None

    if "ICG" in critical:
        if base_state in ("Thriving", "Healthy"):
            return "At Risk", (
                f"ICG score below {CRITICAL_ICG:.0f} prevents a Healthy/Thriving rating; "
                f"state capped at At Risk."
            )
        return base_state, None

    return base_state, None


def _confidence_label(avg_coverage: float, framework_count: int) -> str:
    if framework_count <= 1:
        if avg_coverage >= 85:
            return "Low"
        return "Low"
    if avg_coverage >= 85:
        band = "High"
    elif avg_coverage >= 60:
        band = "Medium"
    else:
        band = "Low"
    if framework_count == 2:
        if band == "High":
            band = "Medium"
        elif band == "Medium":
            band = "Low"
    return band


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

    raw_normalised = weighted_sum / present_weight

    penalty_total, penalty_records = _apply_penalties(icg, dmm, gpis)
    penalised = max(0.0, raw_normalised - penalty_total)

    critical = _count_critical(icg, dmm, gpis)
    capped_score, ceiling_reason = _apply_ceilings(penalised, critical)

    base_state = _state_for(capped_score)
    final_state, override_reason = _state_override(critical, base_state)

    reason_parts = [r for r in (ceiling_reason, override_reason) if r]
    combined_reason = " ".join(reason_parts) if reason_parts else None

    coverages = [r.get("coverage_pct", 0) for r in (icg, dmm, gpis) if r and r.get("available")]
    avg_coverage = sum(coverages) / len(coverages) if coverages else 0
    framework_count = 3 - len(missing)
    confidence = _confidence_label(avg_coverage, framework_count)

    signed = []
    for k, d in contributions.items():
        if d["score"] is not None:
            delta = d["score"] - raw_normalised
            signed.append((k, delta))
    pulls_down = sorted([(k, v) for k, v in signed if v < 0], key=lambda kv: kv[1])
    pulls_up = sorted([(k, v) for k, v in signed if v > 0], key=lambda kv: kv[1], reverse=True)

    return {
        "available": True,
        "score": round(capped_score, 1),
        "state": final_state,
        "confidence": confidence,
        "coverage_pct": round(avg_coverage, 1),
        "contributions": contributions,
        "missing_frameworks": missing,
        "pulls_down": pulls_down,
        "pulls_up": pulls_up,
        "raw_score": round(raw_normalised, 1),
        "penalty_total": round(penalty_total, 1),
        "penalties": penalty_records,
        "base_state": base_state,
        "override_reason": combined_reason,
    }
