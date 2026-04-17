"""
Cross-case Comparison Engine.

Compares up to 3 workspaces side-by-side. Pulls strengths/risks/actions
from the internal report if it exists (richer content); falls back to
external or to scoring-only summaries when reports haven't been run.
"""
from __future__ import annotations

from typing import List, Dict, Any
import pandas as pd


def _strengths_risks_actions(ws):
    """Extract up to 3 each of strengths / risks / actions from the best available report."""
    rpt = ws.internal_report or ws.external_report
    strengths: list = []
    risks: list = []
    actions: list = []

    if rpt:
        # Internal report — rich blocks
        summary = rpt.block("diagnostic_summary") or rpt.block("executive_summary")
        if summary and summary.bullets:
            strengths = summary.bullets[:3]
        strengths_block = rpt.block("strategic_strengths")
        if strengths_block and strengths_block.bullets:
            strengths = strengths_block.bullets[:3]

        risks_block = rpt.block("sensitive_risks") or rpt.block("watch_areas")
        if risks_block and risks_block.bullets:
            risks = risks_block.bullets[:3]

        actions_block = rpt.block("action_matrix")
        if actions_block and actions_block.meta:
            actions = (
                actions_block.meta.get("immediate", [])
                + actions_block.meta.get("near_term", [])
            )[:3]
        else:
            pri = rpt.block("improvement_priorities")
            if pri and pri.bullets:
                actions = pri.bullets[:3]

    # Fallback from raw scoring
    if not strengths:
        if ws.icg and ws.icg.get("available") and ws.icg.get("pct_high_risk", 0) < 10:
            strengths.append("Low structural faculty risk concentration.")
        if ws.dmm and ws.dmm.get("available"):
            for name, val in (ws.dmm.get("strongest") or [])[:2]:
                strengths.append(f"Strong vitality on {name} ({val:.0f}/100).")
    if not risks:
        if ws.icg and ws.icg.get("available") and ws.icg.get("pct_sole_no_backup", 0) >= 10:
            risks.append(f"{ws.icg['pct_sole_no_backup']:.0f}% sole-expert without backup.")
        if ws.dmm and ws.dmm.get("available"):
            for name, val in (ws.dmm.get("weakest") or [])[:2]:
                risks.append(f"Weak vitality on {name} ({val:.0f}/100).")
    if not actions:
        actions.append("Generate a report on the Analysis page to surface actions.")

    return strengths, risks, actions


def compare_cases(cases: List) -> Dict[str, Any]:
    if not cases:
        return {"available": False, "reason": "No cases provided."}

    rows = [c.summary_row() for c in cases]
    df = pd.DataFrame(rows)

    # score differences
    focus_cols = ["ICG Score", "DMM Score", "GPIS Score", "EduPulse Score"]
    deltas = {}
    if len(cases) >= 2:
        ref = df.iloc[0]
        for i in range(1, len(df)):
            label = f"{df.iloc[i]['Case']} vs {ref['Case']}"
            deltas[label] = {
                col: (df.iloc[i][col] - ref[col])
                if (pd.notna(df.iloc[i][col]) and pd.notna(ref[col])) else None
                for col in focus_cols
            }

    # per-case SRA
    strengths: Dict[str, list] = {}
    risks: Dict[str, list] = {}
    actions: Dict[str, list] = {}
    for c in cases:
        s, r, a = _strengths_risks_actions(c)
        strengths[c.name] = s
        risks[c.name] = r
        actions[c.name] = a

    # narrative paragraph
    lines = []
    best = max(cases, key=lambda c: (c.integrated or {}).get("score") or 0)
    worst = min(cases, key=lambda c: (c.integrated or {}).get("score") or 0)
    best_state = (best.integrated or {}).get("state", "—")
    worst_state = (worst.integrated or {}).get("state", "—")
    lines.append(
        f"Across the {len(cases)} case(s) compared, <b>{best.name}</b> records the strongest "
        f"EduPulse signal (state: {best_state}, score: {(best.integrated or {}).get('score')}), "
        f"while <b>{worst.name}</b> sits at the lower end "
        f"(state: {worst_state}, score: {(worst.integrated or {}).get('score')})."
    )

    for fw, col_score, col_state in [
        ("ICG", "ICG Score", "ICG State"),
        ("DMM", "DMM Score", "DMM State"),
        ("GPIS", "GPIS Score", "GPIS State"),
    ]:
        if df[col_score].notna().any():
            best_row = df.loc[df[col_score].idxmax()]
            worst_row = df.loc[df[col_score].idxmin()]
            if best_row["Case"] != worst_row["Case"]:
                lines.append(
                    f"On <b>{fw}</b>, {best_row['Case']} leads "
                    f"({best_row[col_state]}, {best_row[col_score]}) and "
                    f"{worst_row['Case']} trails "
                    f"({worst_row[col_state]}, {worst_row[col_score]})."
                )

    narrative = " ".join(lines)

    return {
        "available": True,
        "summary_df": df,
        "deltas": deltas,
        "strengths": strengths,
        "risks": risks,
        "actions": actions,
        "narrative": narrative,
        "best_case": best.name,
        "worst_case": worst.name,
    }
