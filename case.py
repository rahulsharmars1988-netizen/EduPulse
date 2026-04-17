"""
Case Workspace.

A single upload → multiple runs. The scoring engine runs once and is
shared. Internal and external reports are generated independently on
demand; generating one does not invalidate or regenerate the other.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
import uuid
import re
from pathlib import Path

from .config import LOGIC_VERSION, TEMPLATE_VERSION
from .validation import validate_workbook, ValidationReport
from .scoring import score_icg, score_dmm, score_gpis, integrate_edupulse
from .confidence import compute_confidence
from .report_compose import compose_internal_blocks, compose_external_blocks
from .report_policy import new_report, Report, MODE_INTERNAL, MODE_EXTERNAL
from .config import (
    SHEET_ICG, SHEET_DMM, SHEET_GPIS_SUPPLY, SHEET_GPIS_DEMAND,
)


def derive_case_name(filename: Optional[str]) -> str:
    """Turn an uploaded filename into a readable case name."""
    if not filename:
        return "Untitled Case"
    stem = Path(filename).stem
    cleaned = re.sub(r"[_\-]+", " ", stem)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    for prefix in ("EduPulse ", "Edupulse ", "edupulse "):
        if cleaned.lower().startswith(prefix.lower()):
            cleaned = cleaned[len(prefix):]
    return cleaned or "Untitled Case"


@dataclass
class CaseWorkspace:
    # identity
    workspace_id: str
    name: str
    original_filename: Optional[str]
    uploaded_at: str
    logic_version: str
    template_version: str

    # raw + validation
    uploaded_bytes: bytes
    validation: ValidationReport

    # scoring (mode-agnostic, computed once)
    icg: Dict[str, Any]
    dmm: Dict[str, Any]
    gpis: Dict[str, Any]
    integrated: Dict[str, Any]
    confidence: Dict[str, Any]

    # reports (per mode, run independently)
    internal_report: Optional[Report] = None
    external_report: Optional[Report] = None
    internal_pdf_bytes: Optional[bytes] = None
    external_pdf_bytes: Optional[bytes] = None

    # legacy compatibility
    mode: str = "internal"
    @property
    def case_id(self): return self.workspace_id
    @property
    def timestamp(self): return self.uploaded_at

    # ---- status helpers ----
    def is_scored(self) -> bool:
        return self.integrated is not None and self.integrated.get("available", False)

    def has_internal(self) -> bool:
        return self.internal_report is not None

    def has_external(self) -> bool:
        return self.external_report is not None

    # ---- actions ----
    def run_internal(self) -> Report:
        blocks = compose_internal_blocks(self)
        report = new_report(
            mode=MODE_INTERNAL, blocks=blocks,
            case_name=self.name, original_filename=self.original_filename,
            logic_version=self.logic_version,
        )
        self.internal_report = report
        self.internal_pdf_bytes = None
        return report

    def run_external(self) -> Report:
        blocks = compose_external_blocks(self)
        report = new_report(
            mode=MODE_EXTERNAL, blocks=blocks,
            case_name=self.name, original_filename=self.original_filename,
            logic_version=self.logic_version,
        )
        self.external_report = report
        self.external_pdf_bytes = None
        return report

    def run_both(self) -> tuple:
        return self.run_internal(), self.run_external()

    # ---- summary for list views ----
    def summary_row(self) -> Dict[str, Any]:
        integ = self.integrated or {}
        return {
            "Case": self.name,
            "Source File": self.original_filename or "—",
            "Uploaded": self.uploaded_at,
            "ICG State": (self.icg or {}).get("state"),
            "ICG Score": (self.icg or {}).get("score"),
            "DMM State": (self.dmm or {}).get("state"),
            "DMM Score": (self.dmm or {}).get("score"),
            "GPIS State": (self.gpis or {}).get("state"),
            "GPIS Score": (self.gpis or {}).get("score"),
            "EduPulse State": integ.get("state"),
            "EduPulse Score": integ.get("score"),
            "Confidence": (self.confidence or {}).get("label"),
            "Internal": "✓" if self.has_internal() else "—",
            "External": "✓" if self.has_external() else "—",
        }


def build_workspace(xls_bytes: bytes, case_name: str,
                    original_filename: Optional[str]) -> CaseWorkspace:
    dfs, report = validate_workbook(xls_bytes)

    if report.ok:
        icg = score_icg(dfs.get(SHEET_ICG))
        dmm = score_dmm(dfs.get(SHEET_DMM))
        gpis = score_gpis(dfs.get(SHEET_GPIS_SUPPLY), dfs.get(SHEET_GPIS_DEMAND))
        integrated = integrate_edupulse(icg, dmm, gpis)
    else:
        unavail = {"available": False, "reason": "Validation failed."}
        icg = dmm = gpis = integrated = unavail

    conf = compute_confidence(icg, dmm, gpis) if report.ok else {
        "composite_score": 0.0, "label": "Very Low", "dimensions": {}, "weights": {},
    }

    return CaseWorkspace(
        workspace_id=str(uuid.uuid4())[:8],
        name=case_name or derive_case_name(original_filename),
        original_filename=original_filename,
        uploaded_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        logic_version=LOGIC_VERSION,
        template_version=TEMPLATE_VERSION,
        uploaded_bytes=xls_bytes,
        validation=report,
        icg=icg, dmm=dmm, gpis=gpis, integrated=integrated,
        confidence=conf,
    )


# Backwards-compat alias — older code imports Case / run_case
Case = CaseWorkspace


def run_case(xls_bytes: bytes, case_name: str, mode: str = MODE_INTERNAL) -> CaseWorkspace:
    ws = build_workspace(xls_bytes, case_name, original_filename=None)
    if mode == MODE_INTERNAL:
        ws.run_internal()
    elif mode == MODE_EXTERNAL:
        ws.run_external()
    else:
        ws.run_both()
    ws.mode = mode
    return ws
