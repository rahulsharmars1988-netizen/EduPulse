"""
Report composition.

v1.2.3 — intelligence layer upgrade: pattern-based balance insight,
rebuilt strategic insights, priority focus, enriched risk highlights,
framework-aware timeline projection.
"""
from __future__ import annotations

from typing import Any, List, Dict
import pandas as pd

from .report_policy import (
    ReportBlock, ReportTable,
    INTERNAL_ONLY, EXTERNAL_ONLY, BOTH,
)
from .config import soften_label, MODE_EXTERNAL, MODE_INTERNAL


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _fmt_score(v) -> str:
    return f"{v:.1f}" if isinstance(v, (int, float)) else "—"


def _fw_state(res: dict, mode: str) -> str:
    if not res or not res.get("available"):
        return "—"
    return soften_label(res.get("state") or "—", mode)


def _top_strengths_from_dmm(dmm) -> List[str]:
    if not dmm or not dmm.get("available"):
        return []
    return [f"{name} ({val:.0f}/100)" for name, val in dmm["strongest"][:3]]


def _top_weaknesses_from_dmm(dmm) -> List[str]:
    if not dmm or not dmm.get("available"):
        return []
    return [f"{name} ({val:.0f}/100)" for name, val in dmm["weakest"][:3]]


STATUS_LINES = {
    "Thriving":  "System operating at high maturity and stability.",
    "Healthy":   "System stable with minor optimization opportunities.",
    "Stretched": "System under pressure; requires targeted improvements.",
    "At Risk":   "Critical gaps affecting system performance.",
    "Fragile":   "Multiple structural weaknesses detected.",
    "Critical":  "System instability at foundational level.",
}


def _framework_scores(case) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for name, res in [("ICG", case.icg), ("DMM", case.dmm), ("GPIS", case.gpis)]:
        if res and res.get("available") and res.get("score") is not None:
            out[name] = float(res["score"])
    return out


def _critical_frameworks(case) -> List[str]:
    thresholds = {"ICG": 30.0, "DMM": 40.0, "GPIS": 40.0}
    out = []
    for name, res in [("ICG", case.icg), ("DMM", case.dmm), ("GPIS", case.gpis)]:
        if res and res.get("available") and res.get("score") is not None:
            if res["score"] < thresholds[name]:
                out.append(name)
    return out


def build_system_snapshot(case) -> Dict[str, Any]:
    integ = case.integrated or {}
    state = integ.get("state") or "—"
    score = integ.get("score")
    conf = (case.confidence or {}).get("label", "—")
    status_line = STATUS_LINES.get(state, f"System position: {state}.")
    return {
        "state": state,
        "score": score,
        "confidence": conf,
        "status_line": status_line,
    }


def build_balance_analysis(case) -> Dict[str, Any]:
    scores = _framework_scores(case)
    if not scores:
        return {
            "strongest_framework": None,
            "weakest_framework": None,
            "insight": "Insufficient framework data for balance analysis.",
        }
    if len(scores) == 1:
        only = next(iter(scores))
        return {
            "strongest_framework": only,
            "weakest_framework": only,
            "insight": f"Only {only} produced a usable score; a balance view is not available.",
        }

    strongest = max(scores, key=scores.get)
    weakest = min(scores, key=scores.get)
    spread = scores[strongest] - scores[weakest]

    if strongest == weakest:
        insight = f"Frameworks are balanced around {scores[strongest]:.0f}; no single driver dominates."
    elif strongest == "GPIS" and weakest == "ICG":
        insight = "High performance outcomes exist, but governance weakness creates scale risk."
    elif strongest == "ICG" and weakest == "DMM":
        insight = "Strong institutional control present, but digital capability gaps may limit efficiency and scalability."
    elif strongest == "DMM" and weakest == "GPIS":
        insight = "Digital maturity is strong, but outcomes are not translating into performance impact."
    elif spread > 25:
        insight = "Significant imbalance detected across frameworks, indicating uneven institutional development."
    else:
        insight = "Performance is relatively balanced across frameworks with no major structural imbalance."

    return {
        "strongest_framework": strongest,
        "weakest_framework": weakest,
        "insight": insight,
    }


def build_strategic_insights(case) -> List[str]:
    scores = _framework_scores(case)
    icg = scores.get("ICG")
    dmm = scores.get("DMM")
    gpis = scores.get("GPIS")

    insights: List[str] = []

    if icg is not None and icg < 30:
        insights.append("Governance instability may impact the institution's ability to sustain operations.")
    if dmm is not None and dmm < 40:
        insights.append("Digital maturity gaps may reduce operational efficiency and slow transformation initiatives.")
    if gpis is not None and gpis < 40:
        insights.append("Performance outcomes are below expected levels, indicating execution or delivery gaps.")

    if gpis is not None and icg is not None and gpis > 70 and icg < 40:
        insights.append("Expansion potential exists, but governance structures may not sustain scale.")
    if icg is not None and gpis is not None and icg > 70 and gpis < 40:
        insights.append("Strong control systems exist, but they are not translating into measurable performance outcomes.")
    if dmm is not None and dmm > 70:
        insights.append("Digital infrastructure provides a foundation for scalability and process optimization.")

    seen, out = set(), []
    for s in insights:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out[:5]


def build_priority_focus(case) -> str:
    scores = _framework_scores(case)
    icg = scores.get("ICG")

    if icg is not None and icg < 30:
        return "Strengthen governance and institutional control mechanisms"
    if not scores:
        return "Expand the input coverage before drawing conclusions"
    weakest = min(scores, key=scores.get)
    if weakest == "DMM":
        return "Enhance digital systems and process integration"
    if weakest == "GPIS":
        return "Improve performance execution and outcome delivery"
    return "Optimize and scale current institutional strengths"


def build_risk_highlights(case) -> List[str]:
    highlights: List[str] = []
    conf = (case.confidence or {}).get("label", "—")
    critical = _critical_frameworks(case)
    scores = _framework_scores(case)

    if "ICG" in critical:
        highlights.append("High risk of governance failure affecting institutional stability.")
    if len(critical) >= 2:
        highlights.append("Systemic weakness across multiple dimensions indicates structural instability.")
    if scores:
        strongest = max(scores, key=scores.get)
        weakest = min(scores, key=scores.get)
        spread = scores[strongest] - scores[weakest]
        if strongest != weakest and spread > 25:
            highlights.append("Imbalance across frameworks increases operational risk.")
    if conf == "Low":
        highlights.append("Low data confidence reduces reliability of decision-making.")

    seen, out = set(), []
    for r in highlights:
        if r not in seen:
            seen.add(r)
            out.append(r)
    return out[:3]


def build_timeline_projection(case) -> Dict[str, str]:
    integ = case.integrated or {}
    state = integ.get("state") or "—"
    scores = _framework_scores(case)
    weakest = min(scores, key=scores.get) if scores else None

    if weakest == "ICG":
        return {
            "0_3_months":  "Stabilize governance structures and ensure compliance.",
            "3_6_months":  "Implement control mechanisms and oversight systems.",
            "6_12_months": "Build governance maturity and resilience.",
        }
    if weakest == "DMM":
        return {
            "0_3_months":  "Address critical digital gaps.",
            "3_6_months":  "Integrate systems and improve process automation.",
            "6_12_months": "Scale digital transformation initiatives.",
        }
    if weakest == "GPIS":
        return {
            "0_3_months":  "Identify performance bottlenecks.",
            "3_6_months":  "Improve execution and monitoring systems.",
            "6_12_months": "Strengthen outcome delivery and impact.",
        }

    if state == "Thriving":
        return {
            "0_3_months":  "Optimise operating rhythms and close small gaps.",
            "3_6_months":  "Scale successful practices into adjacent areas.",
            "6_12_months": "Strengthen leadership position and document the playbook.",
        }
    if state == "Healthy":
        return {
            "0_3_months":  "Optimise the weakest layer without disrupting the rest.",
            "3_6_months":  "Invest in growth levers; monitor the weakest framework.",
            "6_12_months": "Move from healthy to thriving; strengthen leadership position.",
        }
    if state == "Stretched":
        return {
            "0_3_months":  "Stabilise the weakest framework and audit its drivers.",
            "3_6_months":  "Execute corrective actions; expect early movement.",
            "6_12_months": "Re-diagnose; a return to Healthy is realistic with discipline.",
        }
    if state in ("At Risk", "Attention Needed"):
        return {
            "0_3_months":  "Stabilisation required — close critical exposures first.",
            "3_6_months":  "Targeted correction — sequence highest-severity items.",
            "6_12_months": "Recovery possible — return to Stretched/Healthy is realistic.",
        }
    if state == "Fragile":
        return {
            "0_3_months":  "Multi-front stabilisation — protect continuity before growth.",
            "3_6_months":  "Coordinated correction across critical frameworks.",
            "6_12_months": "Partial recovery — incremental movement, not full restoration.",
        }
    return {
        "0_3_months":  "Emergency stabilisation — halt discretionary expansion.",
        "3_6_months":  "Rebuild the weakest framework; formalise oversight.",
        "6_12_months": "Structural recovery — multi-cycle arc with realistic milestones.",
    }


# ---------------------------------------------------------------------------
# Action priority (shared by internal + external composers)
# ---------------------------------------------------------------------------
def _action_priority(icg, dmm, gpis) -> Dict[str, List[str]]:
    immediate, near, monitor = [], [], []

    if icg and icg.get("available"):
        st = icg["state"]
        if st == "Priority Action":
            immediate.append("ICG: assign backup faculty for every sole-expert role and document succession protocols.")
            immediate.append("ICG: publish a 3-year succession roadmap for imminent retirements.")
        elif st == "Vulnerable":
            near.append("ICG: close knowledge-transfer gaps via documentation and co-teaching.")
            near.append("ICG: review retention tooling for non-permanent staff in high-demand markets.")
        else:
            monitor.append("ICG: maintain continuity practices; rerun this diagnostic each cycle.")

    if dmm and dmm.get("available"):
        crit = dmm.get("critical_programmes")
        if crit is not None and not crit.empty:
            immediate.append(
                f"DMM: intervene on {len(crit)} programme(s) in Static/Catabolic state."
            )
        weakest = dmm.get("weakest") or []
        for name, val in weakest:
            if val >= 60:
                continue
            if name == "Adaptation":
                near.append("DMM: commit to a 24-month curriculum revision cycle.")
            elif name == "Alignment":
                near.append("DMM: rebuild the alumni-employer loop where placement or alumni relevance has softened.")
            elif name == "Teaching Effectiveness":
                near.append("DMM: tie faculty review to measurable learning improvement.")
            elif name == "Value":
                near.append("DMM: re-examine fees-to-salary balance on contested programmes.")
            elif name == "Contribution":
                immediate.append("DMM: document what the institution actually adds before publishing outcome claims.")
            elif name == "Degree-Job Alignment":
                immediate.append("DMM: audit programme outcomes against realistic job-role taxonomy.")

    if gpis and gpis.get("available"):
        dist = gpis["state_distribution"].set_index("State")["Seat %"].to_dict()
        if dist.get("Mismatch", 0) >= 10:
            immediate.append("GPIS: re-examine mismatch rows — reposition, shift geography, or sunset.")
        if dist.get("Oversupply", 0) >= 15:
            near.append("GPIS: reduce seat allocation in low-employment-strength areas.")
        if dist.get("Undersupply", 0) >= 10:
            near.append("GPIS: expand capacity where demand is strong and capacity is saturated.")
        if dist.get("Weak Alignment", 0) >= 15:
            monitor.append("GPIS: strengthen marketing and employer engagement in weak-alignment rows.")

    if not (immediate or near or monitor):
        monitor.append("No priority actions at this time; refresh the diagnostic each cycle.")
    return {"immediate": immediate, "near_term": near, "monitor": monitor}


# ---------------------------------------------------------------------------
# Decision intelligence — rendered as report blocks
# ---------------------------------------------------------------------------
def _block_system_snapshot(case) -> ReportBlock:
    snap = build_system_snapshot(case)
    score_str = _fmt_score(snap["score"])
    head = f"<b>{snap['state']}</b> · Score {score_str}/100 · Confidence {snap['confidence']}"
    return ReportBlock(
        block_id="system_snapshot",
        title="System Snapshot",
        visibility=BOTH,
        headline=head,
        paragraphs=[snap["status_line"]],
        meta=snap,
        summary_text=f"System snapshot: {snap['state']} · Score {score_str}/100. {snap['status_line']}",
    )


def _block_balance_analysis(case) -> ReportBlock:
    bal = build_balance_analysis(case)
    paragraphs = [bal["insight"]]
    bullets = []
    if bal["strongest_framework"]:
        bullets.append(f"Strongest framework: <b>{bal['strongest_framework']}</b>")
    if bal["weakest_framework"] and bal["weakest_framework"] != bal["strongest_framework"]:
        bullets.append(f"Weakest framework: <b>{bal['weakest_framework']}</b>")

    integ = case.integrated or {}
    for fw, delta in integ.get("pulls_up", []):
        bullets.append(f"{fw} pulls the score up ({delta:+.1f} vs. raw baseline).")
    for fw, delta in integ.get("pulls_down", []):
        bullets.append(f"{fw} pulls the score down ({delta:+.1f} vs. raw baseline).")

    return ReportBlock(
        block_id="balance_analysis",
        title="Balance Analysis",
        visibility=BOTH,
        paragraphs=paragraphs,
        bullets=bullets,
        meta=bal,
    )


def _block_strategic_insights(case) -> ReportBlock:
    insights = build_strategic_insights(case)
    priority = build_priority_focus(case)
    return ReportBlock(
        block_id="strategic_insights",
        title="Strategic Insights",
        visibility=BOTH,
        paragraphs=[
            "Insights translate the framework readings into strategic meaning rather than "
            "repeating the scores. They answer: what does this reading actually imply for decisions?"
        ],
        bullets=insights or ["No material strategic insights surface from the current reading."],
        callouts=[f"Priority focus: {priority}"],
        meta={"insights": insights, "priority_focus": priority},
    )


def _block_risk_highlights(case) -> ReportBlock:
    highlights = build_risk_highlights(case)
    return ReportBlock(
        block_id="risk_highlights",
        title="Risk Highlights",
        visibility=INTERNAL_ONLY,
        paragraphs=[
            "Only critical risks are included here. Secondary issues live in the Sensitive "
            "Risk Exposures and Anti-Gaming sections."
        ],
        bullets=highlights or ["No critical risks surface at this time."],
        meta={"risks": highlights},
    )


def _block_timeline_projection(case) -> ReportBlock:
    tl = build_timeline_projection(case)
    table = ReportTable(
        title="Timeline Projection",
        columns=["Horizon", "Expected Trajectory"],
        rows=[
            ["0–3 months",  tl["0_3_months"]],
            ["3–6 months",  tl["3_6_months"]],
            ["6–12 months", tl["6_12_months"]],
        ],
    )
    return ReportBlock(
        block_id="timeline_projection",
        title="Timeline Projection",
        visibility=BOTH,
        paragraphs=[
            "A forward-looking view of how the institution is likely to evolve if current "
            "conditions hold and the actions implied by this diagnostic are followed."
        ],
        tables=[table],
        meta=tl,
    )


# ---------------------------------------------------------------------------
# Existing internal blocks (unchanged)
# ---------------------------------------------------------------------------
def _block_diagnostic_summary(case) -> ReportBlock:
    integ = case.integrated
    state = soften_label(integ.get("state") or "—", MODE_INTERNAL)
    score = integ.get("score")
    conf = case.confidence or {}
    paragraphs = [
        f"The institution reads as <b>{state}</b> on the integrated EduPulse score "
        f"({_fmt_score(score)} / 100). Confidence in this reading is "
        f"<b>{conf.get('label', '—')}</b> (composite {_fmt_score(conf.get('composite_score'))}/100)."
    ]
    callouts = []
    for fw, delta in integ.get("pulls_down", []):
        callouts.append(f"{fw} pulls the score down (Δ{delta:+.1f}).")
    for fw, delta in integ.get("pulls_up", []):
        callouts.append(f"{fw} supports the score (Δ{delta:+.1f}).")
    if integ.get("override_reason"):
        callouts.append(f"Override applied: {integ['override_reason']}")
    return ReportBlock(
        block_id="diagnostic_summary",
        title="Institutional Diagnostic Summary",
        visibility=BOTH,
        headline=f"Integrated state: {state}",
        paragraphs=paragraphs,
        callouts=callouts,
        summary_text=(
            f"EduPulse integrated state: {state}. Score {_fmt_score(score)}/100. "
            f"Confidence: {conf.get('label', '—')}."
        ),
    )


def _block_pressure_map(case) -> ReportBlock:
    rows = []
    for fw, res in [("ICG", case.icg), ("DMM", case.dmm), ("GPIS", case.gpis)]:
        if res and res.get("available"):
            rows.append([
                fw, soften_label(res["state"], MODE_INTERNAL),
                _fmt_score(res.get("score")),
                f"{res.get('coverage_pct', 0):.0f}%",
            ])
        else:
            rows.append([fw, "—", "—", "—"])
    table = ReportTable(
        title="Framework Pressure Map",
        columns=["Framework", "State", "Score", "Coverage"],
        rows=rows,
    )
    return ReportBlock(
        block_id="framework_pressure_map",
        title="Framework Pressure Map",
        visibility=BOTH,
        tables=[table],
    )


def _block_causal_findings(case) -> ReportBlock:
    bullets = []
    icg = case.icg
    if icg and icg.get("available"):
        for d in icg.get("key_drivers", []):
            bullets.append(f"[ICG] {d}")
    dmm = case.dmm
    if dmm and dmm.get("available"):
        for name, val in dmm.get("weakest", [])[:3]:
            bullets.append(f"[DMM] Weakest vitality lever: {name} ({val:.0f}/100).")
        for name, val in dmm.get("strongest", [])[:1]:
            bullets.append(f"[DMM] Strongest vitality lever: {name} ({val:.0f}/100).")
    gpis = case.gpis
    if gpis and gpis.get("available"):
        for d in gpis.get("key_drivers", []):
            bullets.append(f"[GPIS] {d}")
    return ReportBlock(
        block_id="causal_findings",
        title="Causal Findings",
        visibility=INTERNAL_ONLY,
        paragraphs=[
            "Causal findings attribute the integrated state to specific drivers. "
            "Each bullet names the framework, the driver, and its direction."
        ],
        bullets=bullets,
    )


def _block_sensitive_risks(case) -> ReportBlock:
    bullets = []
    tables = []
    icg = case.icg
    if icg and icg.get("available"):
        flagged = icg.get("flagged_faculty")
        if flagged is not None and not flagged.empty:
            rows = flagged.head(8)[["Department", "Faculty Name", "Risk Level",
                                    "Combined Risk", "Sole Expert",
                                    "Backup Available"]].values.tolist()
            tables.append(ReportTable(
                title="Top flagged faculty (internal only)",
                columns=["Department", "Faculty Name", "Risk Level",
                         "Combined Risk", "Sole Expert", "Backup Available"],
                rows=[[str(c) for c in r] for r in rows],
            ))
        if icg.get("pct_sole_no_backup", 0) >= 10:
            bullets.append(
                f"{icg['pct_sole_no_backup']:.0f}% of faculty are sole experts without a declared backup."
            )
        if icg.get("pct_retire_soon", 0) >= 15:
            bullets.append(
                f"{icg['pct_retire_soon']:.0f}% of faculty are within a 3-year retirement horizon."
            )
        dept = icg.get("dept_concentration")
        if dept is not None and not dept.empty:
            hottest = dept.iloc[0]
            if hottest.get("High_Risk_%", 0) >= 25:
                bullets.append(
                    f"{hottest['Department']}: {hottest['High_Risk_%']:.0f}% of its faculty are high-risk."
                )
    dmm = case.dmm
    if dmm and dmm.get("available"):
        crit = dmm.get("critical_programmes")
        if crit is not None and not crit.empty:
            names = crit["Programme Name"].tolist()
            bullets.append(
                f"Programmes in Static or Catabolic state: {', '.join(names)}."
            )
    return ReportBlock(
        block_id="sensitive_risks",
        title="Sensitive Risk Exposures",
        visibility=INTERNAL_ONLY,
        paragraphs=[
            "These exposures include faculty-level identity and programme-level "
            "weaknesses. They are restricted to internal distribution."
        ],
        bullets=bullets,
        tables=tables,
    )


def _block_anti_gaming(case) -> ReportBlock:
    dmm = case.dmm
    flags = dmm.get("anti_gaming_flags", []) if dmm and dmm.get("available") else []
    rows = []
    for f in flags:
        rows.append([
            f.get("category", "—"),
            f.get("severity", "—"),
            f.get("affected_unit", "—"),
            f.get("reason", "—"),
            f.get("suggested_action", "—"),
        ])
    tables = []
    if rows:
        tables.append(ReportTable(
            title="Anti-gaming flags",
            columns=["Category", "Severity", "Affected Unit", "Reason", "Suggested Action"],
            rows=rows,
        ))
    paragraphs = [
        "The anti-gaming engine inspects combinations that are structurally "
        "plausible but semantically suspect — e.g. strong outcomes with no "
        "institutional contribution, or strong placement with no degree-job "
        "alignment. Each flag carries a category, severity, the unit it applies "
        "to, the reason, and a suggested validation action."
    ]
    if not flags:
        paragraphs.append("No anti-gaming flags raised in this case.")
    return ReportBlock(
        block_id="anti_gaming",
        title="Anti-Gaming Analysis",
        visibility=INTERNAL_ONLY,
        paragraphs=paragraphs,
        tables=tables,
        meta={"flag_count": len(flags)},
    )


def _block_action_matrix(case) -> ReportBlock:
    pri = _action_priority(case.icg, case.dmm, case.gpis)
    rows = []
    for label, items in [("Immediate", pri["immediate"]),
                          ("Near-Term", pri["near_term"]),
                          ("Monitor", pri["monitor"])]:
        for item in items:
            rows.append([label, item])
    table = ReportTable(
        title="Action Prioritization Matrix",
        columns=["Horizon", "Action"],
        rows=rows,
    )
    return ReportBlock(
        block_id="action_matrix",
        title="Action Prioritization Matrix",
        visibility=INTERNAL_ONLY,
        paragraphs=[
            "Actions are bucketed by horizon so that leadership can sequence them. "
            "Immediate = address inside the next cycle. Near-Term = within 6 months. "
            "Monitor = watch items with no immediate action required."
        ],
        tables=[table],
        meta=pri,
    )


def _block_30_60_90(case) -> ReportBlock:
    pri = _action_priority(case.icg, case.dmm, case.gpis)
    day_30 = pri["immediate"][:4]
    day_60 = (pri["immediate"][4:] + pri["near_term"])[:4]
    day_90 = pri["near_term"][4:] or pri["monitor"]
    return ReportBlock(
        block_id="plan_30_60_90",
        title="30-60-90 Day Action Plan",
        visibility=INTERNAL_ONLY,
        paragraphs=[
            "A phased plan to sequence the Action Prioritization Matrix. "
            "First 30 days: stabilise immediate exposures. 31–60: execute near-term. "
            "61–90: close out remaining items and monitor."
        ],
        labeled_bullets=(
            [("Day 0-30", a) for a in day_30]
            + [("Day 31-60", a) for a in day_60]
            + [("Day 61-90", a) for a in day_90]
        ),
    )


def _block_traceability(case) -> ReportBlock:
    bullets = [
        f"Case name: {case.name}",
        f"Original filename: {case.original_filename or '—'}",
        f"Uploaded at: {case.uploaded_at}",
        f"Logic version: {case.logic_version}",
        f"Template version: {case.template_version}",
        f"Workspace ID: {case.workspace_id}",
    ]
    integ = case.integrated or {}
    if integ.get("raw_score") is not None:
        bullets.append(f"Raw weighted score (before penalty/ceiling): {integ['raw_score']}")
    if integ.get("penalty_total"):
        bullets.append(f"Penalty total applied: {integ['penalty_total']}")
    if integ.get("override_reason"):
        bullets.append(f"Override note: {integ['override_reason']}")
    conf_rows = []
    for dim, obj in (case.confidence or {}).get("dimensions", {}).items():
        conf_rows.append([dim.replace("_", " ").title(), f"{obj['score']:.1f}", obj["note"]])
    tables = []
    if conf_rows:
        tables.append(ReportTable(
            title="Confidence dimensions",
            columns=["Dimension", "Score", "Note"],
            rows=conf_rows,
        ))
    if integ.get("penalties"):
        p_rows = []
        for p in integ["penalties"]:
            p_rows.append([p["framework"], f"{p['score']:.1f}", f"{p['threshold']:.0f}",
                           f"{p['penalty']:.2f}", p["reason"]])
        tables.append(ReportTable(
            title="Non-compensatory penalties",
            columns=["Framework", "Score", "Threshold", "Penalty", "Reason"],
            rows=p_rows,
        ))
    return ReportBlock(
        block_id="traceability",
        title="Traceability Appendix",
        visibility=INTERNAL_ONLY,
        paragraphs=[
            "This appendix captures the inputs that produced this report. "
            "It exists to make the diagnostic reproducible and auditable."
        ],
        bullets=bullets,
        tables=tables,
    )


# ---------------------------------------------------------------------------
# Existing external blocks (unchanged)
# ---------------------------------------------------------------------------
def _block_executive_summary(case) -> ReportBlock:
    integ = case.integrated
    state = soften_label(integ.get("state") or "—", MODE_EXTERNAL)
    score = integ.get("score")
    strengths = []
    watches = []
    if case.icg and case.icg.get("available"):
        if case.icg["state"] in ("Resilient", "Stable"):
            strengths.append("faculty continuity is holding up")
        else:
            watches.append("faculty continuity is under pressure")
    if case.dmm and case.dmm.get("available"):
        if case.dmm["state"] in ("Anabolic", "Transitional"):
            strengths.append("programme vitality is broadly positive")
        else:
            watches.append("programme vitality needs renewal")
    if case.gpis and case.gpis.get("available"):
        if case.gpis["state"] in ("Strong Alignment", "Approximate Alignment", "Undersupply"):
            strengths.append("supply is aligned with demand")
        else:
            watches.append("supply-demand alignment warrants review")

    st_text = ", ".join(strengths) if strengths else "several positive signals"
    wt_text = ", ".join(watches) if watches else "no material watch areas"
    headline = (
        f"The institution's overall position reads as <b>{state}</b>. Where "
        f"it stands today: {st_text}. Where it should watch: {wt_text}."
    )
    return ReportBlock(
        block_id="executive_summary",
        title="Executive Summary",
        visibility=EXTERNAL_ONLY,
        headline=headline,
        paragraphs=[
            "This summary provides a strategic view of institutional health. "
            "It is derived from the same underlying engine used for internal diagnostics, "
            "but presented at the level appropriate for external audiences."
        ],
    )


def _block_health_position(case) -> ReportBlock:
    rows = []
    for fw, res in [("Continuity", case.icg), ("Programme Vitality", case.dmm),
                    ("Market Alignment", case.gpis)]:
        state = _fw_state(res, MODE_EXTERNAL)
        rows.append([fw, state])
    table = ReportTable(
        title="Institutional Health Position",
        columns=["Dimension", "Position"],
        rows=rows,
    )
    return ReportBlock(
        block_id="health_position",
        title="Institutional Health Position",
        visibility=EXTERNAL_ONLY,
        paragraphs=[
            "The position across three dimensions — continuity, programme vitality, "
            "and market alignment — describes where the institution sits today."
        ],
        tables=[table],
    )


def _block_strategic_strengths(case) -> ReportBlock:
    bullets = []
    if case.icg and case.icg.get("available"):
        if case.icg.get("pct_high_risk", 0) < 10:
            bullets.append("Faculty system shows low structural risk concentration.")
        if case.icg.get("pct_sole_no_backup", 0) < 10:
            bullets.append("Sole-expert exposure is well managed.")
    for s in _top_strengths_from_dmm(case.dmm)[:2]:
        bullets.append(f"Programme vitality is led by: {s}.")
    if case.gpis and case.gpis.get("available"):
        dist = case.gpis["state_distribution"].set_index("State")["Seat %"].to_dict()
        good = dist.get("Strong Alignment", 0) + dist.get("Approximate Alignment", 0)
        if good >= 50:
            bullets.append(f"{good:.0f}% of seats sit in well-aligned domain-geography pairs.")
        if dist.get("Undersupply", 0) > 0:
            bullets.append(f"Strong-demand areas at or above capacity — clear growth headroom.")
    if not bullets:
        bullets.append("Institution maintains baseline operational strength across the three dimensions.")
    return ReportBlock(
        block_id="strategic_strengths",
        title="Strategic Strengths",
        visibility=EXTERNAL_ONLY,
        paragraphs=["Strengths are positive signals that can be built upon."],
        bullets=bullets,
    )


def _block_watch_areas(case) -> ReportBlock:
    bullets = []
    if case.icg and case.icg.get("available") and case.icg["state"] in ("Vulnerable", "Priority Action"):
        if case.icg.get("pct_sole_no_backup", 0) >= 10:
            bullets.append("Faculty continuity is exposed to sole-expert dependency.")
        if case.icg.get("pct_retire_soon", 0) >= 15:
            bullets.append("A retirement wave is forming in the next 3 years.")
    for s in _top_weaknesses_from_dmm(case.dmm)[:2]:
        bullets.append(f"Programme vitality lags on: {s.split(' (')[0]}.")
    if case.gpis and case.gpis.get("available"):
        dist = case.gpis["state_distribution"].set_index("State")["Seat %"].to_dict()
        if dist.get("Mismatch", 0) >= 10:
            bullets.append(f"{dist['Mismatch']:.0f}% of seats sit in low- or no-demand areas.")
        if dist.get("Oversupply", 0) >= 15:
            bullets.append("Capacity exceeds visible demand in parts of the portfolio.")
    if not bullets:
        bullets.append("No material watch areas surface at this level of review.")
    return ReportBlock(
        block_id="watch_areas",
        title="Watch Areas",
        visibility=EXTERNAL_ONLY,
        paragraphs=[
            "Watch areas are themes that warrant proactive attention. "
            "They are presented at a strategic level; operational specifics stay internal."
        ],
        bullets=bullets,
    )


def _block_improvement_priorities(case) -> ReportBlock:
    pri = _action_priority(case.icg, case.dmm, case.gpis)
    items = pri["immediate"][:3] + pri["near_term"][:3]
    if not items:
        items = ["Maintain current practices; refresh the diagnostic each cycle."]
    cleaned = []
    for it in items:
        for prefix in ("ICG:", "DMM:", "GPIS:"):
            if it.startswith(prefix):
                it = it[len(prefix):].strip()
                break
        cleaned.append(it)
    return ReportBlock(
        block_id="improvement_priorities",
        title="Improvement Priorities",
        visibility=EXTERNAL_ONLY,
        paragraphs=[
            "Improvement priorities are the strategic moves suggested by the diagnostic. "
            "They are expressed at a strategic level and are not tied to any individual."
        ],
        bullets=cleaned,
    )


def _block_forward_outlook(case) -> ReportBlock:
    integ = case.integrated
    state = soften_label(integ.get("state") or "—", MODE_EXTERNAL)
    if state in ("Thriving", "Healthy"):
        outlook = ("The forward outlook is positive. If current practices are maintained, "
                   "the institution should continue to consolidate its position.")
    elif state in ("Stretched", "At Risk", "Fragile"):
        outlook = ("The forward outlook is mixed. Acting on the priorities above "
                   "is expected to shift the position upward within the next diagnostic cycle.")
    else:
        outlook = ("The forward outlook requires deliberate action. The priorities above "
                   "define the route back to a healthier position.")
    return ReportBlock(
        block_id="forward_outlook",
        title="Forward Outlook",
        visibility=EXTERNAL_ONLY,
        paragraphs=[outlook],
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def compose_internal_blocks(case) -> List[ReportBlock]:
    return [
        _block_system_snapshot(case),
        _block_diagnostic_summary(case),
        _block_balance_analysis(case),
        _block_pressure_map(case),
        _block_strategic_insights(case),
        _block_causal_findings(case),
        _block_risk_highlights(case),
        _block_sensitive_risks(case),
        _block_anti_gaming(case),
        _block_action_matrix(case),
        _block_timeline_projection(case),
        _block_30_60_90(case),
        _block_traceability(case),
    ]


def compose_external_blocks(case) -> List[ReportBlock]:
    return [
        _block_system_snapshot(case),
        _block_executive_summary(case),
        _block_health_position(case),
        _block_balance_analysis(case),
        _block_strategic_strengths(case),
        _block_strategic_insights(case),
        _block_watch_areas(case),
        _block_improvement_priorities(case),
        _block_timeline_projection(case),
        _block_forward_outlook(case),
    ]


def diff_modes(internal_blocks, external_blocks) -> dict:
    i_ids = {b.block_id for b in internal_blocks}
    e_ids = {b.block_id for b in external_blocks}
    internal_only = i_ids - e_ids
    external_only = e_ids - i_ids
    shared = i_ids & e_ids

    def describe(blocks, ids):
        return [next(b.title for b in blocks if b.block_id == bid) for bid in ids]

    return {
        "internal_only_blocks": describe(internal_blocks, internal_only),
        "external_only_blocks": describe(external_blocks, external_only),
        "shared_block_ids": list(shared),
    }
