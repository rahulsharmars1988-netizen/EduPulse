"""
PDF renderer.

Consumes a `Report` (list of policy-filtered `ReportBlock` objects) plus
optional `BrandingSettings` and emits a professional PDF.

Internal reports render with full detail — tables, labeled bullets,
callout strips, traceability. External reports render with a cleaner,
higher-level aesthetic — fewer tables, more prose, and a strategic cover
band. The mode switch happens inside this renderer so that the policy
layer's filtering drives the page.
"""
from __future__ import annotations

from io import BytesIO
from typing import Optional, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    Image as RLImage, Flowable,
)

from .config import APP_NAME, APP_TAGLINE, LOGIC_VERSION
from .report_policy import Report, ReportBlock, MODE_INTERNAL, MODE_EXTERNAL
from .branding import BrandingSettings

# Palette
INK = colors.HexColor("#0F172A")
ACCENT = colors.HexColor("#1E3A8A")
ACCENT_DARK = colors.HexColor("#0B1F5C")
SOFT = colors.HexColor("#E0E7FF")
MUTED = colors.HexColor("#64748B")
LINE = colors.HexColor("#CBD5E1")
CALLOUT_BG = colors.HexColor("#F1F5F9")
CALLOUT_BAR = colors.HexColor("#1E3A8A")


# ---------------------------------------------------------------------------
# Flowables
# ---------------------------------------------------------------------------
class HRule(Flowable):
    def __init__(self, width, thickness=0.6, color=LINE):
        super().__init__()
        self.width, self.thickness, self.color = width, thickness, color

    def wrap(self, *_):
        return self.width, self.thickness

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 0, self.width, 0)


class ColoredBand(Flowable):
    """Solid coloured band used for cover headers in external reports."""
    def __init__(self, width, height=28 * mm, color=ACCENT, title="", subtitle=""):
        super().__init__()
        self.width, self.height, self.color = width, height, color
        self.title, self.subtitle = title, subtitle

    def wrap(self, *_):
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.setFillColor(self.color)
        c.rect(0, 0, self.width, self.height, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(10 * mm, self.height - 12 * mm, self.title)
        if self.subtitle:
            c.setFont("Helvetica", 10)
            c.drawString(10 * mm, self.height - 19 * mm, self.subtitle)


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
def _styles():
    ss = getSampleStyleSheet()
    return {
        "title":    ParagraphStyle("t", parent=ss["Title"], textColor=ACCENT, alignment=TA_LEFT,
                                   fontSize=22, leading=26, spaceAfter=4),
        "subtitle": ParagraphStyle("s", parent=ss["Normal"], textColor=MUTED, fontSize=10,
                                   leading=13, spaceAfter=12),
        "h2":       ParagraphStyle("h2", parent=ss["Heading2"], textColor=ACCENT, fontSize=14,
                                   leading=18, spaceBefore=12, spaceAfter=6),
        "h3":       ParagraphStyle("h3", parent=ss["Heading3"], textColor=INK, fontSize=11,
                                   leading=15, spaceBefore=6, spaceAfter=3),
        "body":     ParagraphStyle("b", parent=ss["Normal"], textColor=INK, fontSize=10,
                                   leading=14, spaceAfter=4),
        "lead":     ParagraphStyle("ld", parent=ss["Normal"], textColor=INK, fontSize=11,
                                   leading=15.5, spaceAfter=6),
        "bullet":   ParagraphStyle("bu", parent=ss["Normal"], textColor=INK, fontSize=10,
                                   leading=14, leftIndent=12, bulletIndent=2, spaceAfter=2),
        "labeled":  ParagraphStyle("lb", parent=ss["Normal"], textColor=INK, fontSize=10,
                                   leading=14, leftIndent=0, spaceAfter=2),
        "small":    ParagraphStyle("sm", parent=ss["Normal"], textColor=MUTED, fontSize=8.5,
                                   leading=11),
        "callout":  ParagraphStyle("co", parent=ss["Normal"], textColor=INK, fontSize=10,
                                   leading=14, leftIndent=8, spaceAfter=2),
        "sig_name": ParagraphStyle("sn", parent=ss["Normal"], textColor=INK, fontSize=11,
                                   leading=14, spaceAfter=0, fontName="Helvetica-Bold"),
        "sig_desig": ParagraphStyle("sd", parent=ss["Normal"], textColor=MUTED, fontSize=9,
                                    leading=12, spaceAfter=0),
    }


# ---------------------------------------------------------------------------
# Render helpers
# ---------------------------------------------------------------------------
def _header_row(content_width: float, pairs):
    """Banner row of (label, value) cells."""
    lstyle = ParagraphStyle("hl", textColor=colors.white, fontSize=8.5,
                             alignment=TA_CENTER, leading=10)
    vstyle = ParagraphStyle("hv", textColor=colors.white, fontSize=13,
                             alignment=TA_CENTER, leading=15, fontName="Helvetica-Bold")
    labels = [Paragraph(l, lstyle) for l, _ in pairs]
    values = [Paragraph(str(v), vstyle) for _, v in pairs]
    n = len(pairs)
    col_w = content_width / n
    t = Table([labels, values], colWidths=[col_w] * n, rowHeights=[14, 22])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), ACCENT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("LINEAFTER", (0, 0), (-2, -1), 0.8, colors.white),
    ]))
    return t


def _data_table(table, content_width, max_rows=14):
    cols = table.columns
    n = len(cols)
    # wide first column for tables whose first column is a name-like field
    if n > 1 and cols[0] in {"Programme Name", "Department", "Dimension",
                              "Horizon", "Category"}:
        first = content_width * 0.30
        rest = (content_width - first) / (n - 1)
        widths = [first] + [rest] * (n - 1)
    else:
        widths = [content_width / n] * n
    data = [cols] + table.rows[:max_rows]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.25, LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def _callout_strip(text: str, content_width: float, styles) -> Table:
    body = Paragraph(text, styles["callout"])
    t = Table([[body]], colWidths=[content_width])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CALLOUT_BG),
        ("LINEBEFORE", (0, 0), (0, -1), 3, CALLOUT_BAR),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def _render_block(block: ReportBlock, content_width: float, styles, mode: str) -> list:
    out = []
    out.append(Paragraph(block.title, styles["h2"]))
    if block.headline:
        out.append(Paragraph(block.headline, styles["lead"]))
    for p in block.paragraphs:
        out.append(Paragraph(p, styles["body"]))
    for c in block.callouts:
        out.append(_callout_strip(c, content_width, styles))
        out.append(Spacer(1, 3))
    for b in block.bullets:
        out.append(Paragraph(f"• {b}", styles["bullet"]))
    if block.labeled_bullets:
        # group by label for clarity
        current = None
        for label, text in block.labeled_bullets:
            if label != current:
                current = label
                out.append(Spacer(1, 2))
                out.append(Paragraph(f"<b>{label}</b>", styles["h3"]))
            out.append(Paragraph(f"• {text}", styles["bullet"]))
    for tbl in block.tables:
        out.append(Spacer(1, 4))
        out.append(Paragraph(f"<b>{tbl.title}</b>", styles["h3"]))
        out.append(_data_table(tbl, content_width))
    out.append(Spacer(1, 6))
    out.append(HRule(content_width))
    out.append(Spacer(1, 4))
    return out


# ---------------------------------------------------------------------------
# Signature block
# ---------------------------------------------------------------------------
def _signature_block(branding: BrandingSettings, content_width: float, styles) -> list:
    out = []
    if not branding:
        return out
    # build a right-aligned signature column
    name = branding.authorized_signature_name.strip() if branding else ""
    desig = branding.designation.strip() if branding else ""
    inst = branding.institution_name.strip() if branding else ""
    owner = branding.copyright_owner_name.strip() if branding else ""

    # If nothing to show, skip
    if not any([name, desig, inst, owner, branding.has_signature_image()]):
        return out

    # Image
    sig_image = None
    if branding.has_signature_image():
        try:
            sig_image = RLImage(BytesIO(branding.signature_image_bytes),
                                width=45 * mm, height=18 * mm, kind='proportional')
        except Exception:
            sig_image = None

    # Right column content
    right_stack = []
    if sig_image is not None:
        right_stack.append(sig_image)
    elif name:
        right_stack.append(Paragraph(f"<i>/ {name} /</i>", styles["sig_name"]))
    if name:
        right_stack.append(Paragraph(name, styles["sig_name"]))
    if desig:
        right_stack.append(Paragraph(desig, styles["sig_desig"]))
    if inst:
        right_stack.append(Paragraph(inst, styles["sig_desig"]))
    if owner:
        right_stack.append(Paragraph(f"© {owner}", styles["sig_desig"]))

    # two-column layout: footer note left, signature right
    left_cell = [Paragraph(branding.footer_note, styles["small"])] if branding.footer_note else [Paragraph(" ", styles["small"])]
    right_cell = right_stack or [Paragraph(" ", styles["small"])]
    t = Table([[left_cell, right_cell]],
              colWidths=[content_width * 0.55, content_width * 0.45])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("LINEABOVE", (0, 0), (-1, 0), 0.4, LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))
    out.append(Spacer(1, 10))
    out.append(t)
    return out


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def render_pdf(report: Report, branding: Optional[BrandingSettings] = None,
               scored_summary: Optional[dict] = None) -> bytes:
    """Render the given report to PDF bytes."""
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=18 * mm, bottomMargin=16 * mm,
        title=f"{APP_NAME} {report.mode.title()} Report — {report.case_name}",
    )
    styles = _styles()
    content_width = doc.width
    flow = []

    is_external = report.mode == MODE_EXTERNAL
    inst = branding.institution_name if branding and branding.institution_name else ""

    # Cover / header
    if is_external:
        flow.append(ColoredBand(
            content_width, height=32 * mm, color=ACCENT,
            title=f"{APP_NAME} External Report",
            subtitle=f"{report.case_name}" + (f" · {inst}" if inst else ""),
        ))
        flow.append(Spacer(1, 10))
        flow.append(Paragraph(
            f"Generated {report.generated_at} · Logic v{LOGIC_VERSION} · Report ID: {report.report_id}",
            styles["subtitle"],
        ))
    else:
        flow.append(Paragraph(f"{APP_NAME} — Internal Diagnostic Report", styles["title"]))
        subtitle_bits = [
            f"Case: <b>{report.case_name}</b>",
            f"Source file: {report.original_filename or '—'}",
            f"Generated {report.generated_at}",
            f"Logic v{LOGIC_VERSION}",
            f"Report ID: {report.report_id}",
        ]
        if inst:
            subtitle_bits.insert(1, f"Institution: {inst}")
        flow.append(Paragraph(" · ".join(subtitle_bits), styles["subtitle"]))
        flow.append(HRule(content_width))
        flow.append(Spacer(1, 6))

    # Score / confidence banner — both modes, but simpler for external
    if scored_summary:
        state = scored_summary.get("state", "—")
        score = scored_summary.get("score")
        conf = scored_summary.get("confidence", "—")
        cov = scored_summary.get("coverage_pct")
        if is_external:
            pairs = [
                ("Overall Position", str(state)),
                ("Score", f"{score:.0f}" if isinstance(score, (int, float)) else "—"),
            ]
        else:
            pairs = [
                ("EduPulse State", str(state)),
                ("Score", f"{score:.0f}" if isinstance(score, (int, float)) else "—"),
                ("Confidence", str(conf)),
                ("Coverage", f"{cov:.0f}%" if isinstance(cov, (int, float)) else "—"),
            ]
        flow.append(_header_row(content_width, pairs))
        flow.append(Spacer(1, 10))

    # Page break after cover for external mode, no break for internal
    # (internal puts content right after the banner to save space)

    # Blocks
    for block in report.blocks:
        flow.extend(_render_block(block, content_width, styles, report.mode))

    # Signature / footer
    flow.extend(_signature_block(branding, content_width, styles))

    # Minimal disclaimer
    flow.append(Spacer(1, 6))
    flow.append(Paragraph(
        "This report is produced by the EduPulse Institutional Health Diagnostics Engine — "
        "a self-assessment and improvement tool, not a ranking or compliance instrument.",
        styles["small"],
    ))

    doc.build(flow)
    return buf.getvalue()


def render_internal_pdf(case, branding: Optional[BrandingSettings] = None) -> bytes:
    """Convenience: use or lazily build the internal report."""
    if not case.has_internal():
        case.run_internal()
    if case.internal_pdf_bytes:
        return case.internal_pdf_bytes
    scored = {
        "state": (case.integrated or {}).get("state"),
        "score": (case.integrated or {}).get("score"),
        "confidence": (case.confidence or {}).get("label"),
        "coverage_pct": (case.integrated or {}).get("coverage_pct"),
    }
    pdf = render_pdf(case.internal_report, branding=branding, scored_summary=scored)
    case.internal_pdf_bytes = pdf
    return pdf


def render_external_pdf(case, branding: Optional[BrandingSettings] = None) -> bytes:
    if not case.has_external():
        case.run_external()
    if case.external_pdf_bytes:
        return case.external_pdf_bytes
    scored = {
        "state": (case.integrated or {}).get("state"),
        "score": (case.integrated or {}).get("score"),
        "confidence": (case.confidence or {}).get("label"),
        "coverage_pct": (case.integrated or {}).get("coverage_pct"),
    }
    pdf = render_pdf(case.external_report, branding=branding, scored_summary=scored)
    case.external_pdf_bytes = pdf
    return pdf


# ---------------------------------------------------------------------------
# Backwards compatibility — old code imports `build_pdf(case)`
# Defaults to internal mode and no branding.
# ---------------------------------------------------------------------------
def build_pdf(case, branding: Optional[BrandingSettings] = None) -> bytes:
    return render_internal_pdf(case, branding=branding)
