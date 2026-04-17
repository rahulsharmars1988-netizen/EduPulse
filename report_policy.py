"""
Report Policy Layer.

A report is a list of BLOCKS. Each block declares its visibility rule:

  INTERNAL_ONLY        — never appears in external reports
  EXTERNAL_ONLY        — never appears in internal reports
  BOTH                 — present in both, rendered identically
  SUMMARIZE_FOR_EXTERNAL — present in internal fully; summarised in external
  REDACT_SENSITIVE     — present in both, sensitive rows stripped for external

The structural difference between internal and external reports is
enforced here, not by string substitution.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Optional
import uuid


# Visibility tokens
INTERNAL_ONLY = "internal_only"
EXTERNAL_ONLY = "external_only"
BOTH = "both"
SUMMARIZE_FOR_EXTERNAL = "summarize_for_external"
REDACT_SENSITIVE = "redact_sensitive"

# Modes
MODE_INTERNAL = "internal"
MODE_EXTERNAL = "external"


@dataclass
class ReportTable:
    title: str
    columns: List[str]
    rows: List[List[Any]]


@dataclass
class ReportBlock:
    block_id: str
    title: str
    visibility: str = BOTH
    headline: Optional[str] = None
    paragraphs: List[str] = field(default_factory=list)
    callouts: List[str] = field(default_factory=list)          # boxed highlights
    bullets: List[str] = field(default_factory=list)            # plain bullets
    labeled_bullets: List[tuple] = field(default_factory=list)  # (label, text)
    tables: List[ReportTable] = field(default_factory=list)
    meta: dict = field(default_factory=dict)                    # structured extras
    summary_text: Optional[str] = None                          # used when summarize_for_external


@dataclass
class Report:
    mode: str
    generated_at: str
    report_id: str
    case_name: str
    original_filename: Optional[str]
    logic_version: str
    blocks: List[ReportBlock]

    def block(self, block_id: str) -> Optional[ReportBlock]:
        for b in self.blocks:
            if b.block_id == block_id:
                return b
        return None


def _now_stamp() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")


def _rid() -> str:
    return str(uuid.uuid4())[:8]


def apply_policy(blocks: List[ReportBlock], mode: str) -> List[ReportBlock]:
    """Filter and transform blocks according to visibility rules for `mode`."""
    out: List[ReportBlock] = []
    for b in blocks:
        vis = b.visibility
        if vis == INTERNAL_ONLY and mode != MODE_INTERNAL:
            continue
        if vis == EXTERNAL_ONLY and mode != MODE_EXTERNAL:
            continue
        if vis == SUMMARIZE_FOR_EXTERNAL and mode == MODE_EXTERNAL:
            # collapse into a single summary paragraph, drop detail + tables
            summary = b.summary_text or (
                b.headline or (b.paragraphs[0] if b.paragraphs else b.title)
            )
            out.append(ReportBlock(
                block_id=b.block_id, title=b.title, visibility=BOTH,
                headline=None, paragraphs=[summary], tables=[], bullets=[],
                callouts=[], labeled_bullets=[], meta={},
            ))
            continue
        if vis == REDACT_SENSITIVE and mode == MODE_EXTERNAL:
            # rebuild without the 'sensitive_*' fields
            out.append(ReportBlock(
                block_id=b.block_id, title=b.title, visibility=BOTH,
                headline=b.headline,
                paragraphs=list(b.paragraphs),
                callouts=list(b.callouts),
                bullets=[x for x in b.bullets if not str(x).startswith("[sensitive]")],
                labeled_bullets=[(l, t) for (l, t) in b.labeled_bullets if l != "sensitive"],
                tables=[t for t in b.tables if not t.title.lower().startswith("sensitive")],
                meta={k: v for k, v in b.meta.items() if not k.startswith("sensitive_")},
                summary_text=b.summary_text,
            ))
            continue
        out.append(b)
    return out


def new_report(mode: str, blocks: List[ReportBlock], case_name: str,
               original_filename: Optional[str], logic_version: str) -> Report:
    filtered = apply_policy(blocks, mode)
    return Report(
        mode=mode,
        generated_at=_now_stamp(),
        report_id=_rid(),
        case_name=case_name,
        original_filename=original_filename,
        logic_version=logic_version,
        blocks=filtered,
    )
