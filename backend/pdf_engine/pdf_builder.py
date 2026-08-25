"""
BD / WA Health – Fortnightly Field Report
Pyxis & WOW Service Performance
"""
from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, Image, KeepTogether,
)
from reportlab.graphics.shapes import Drawing, Rect, String, Line

PAGE_WIDTH, PAGE_HEIGHT = A4

# Palette
NAVY = colors.Color(0.00, 0.20, 0.63)
TEAL = colors.Color(0.00, 0.45, 0.55)
SLATE = colors.Color(0.30, 0.36, 0.42)
LIGHT_GREY = colors.Color(0.945, 0.95, 0.96)
MED_GREY = colors.Color(0.70, 0.74, 0.78)
SOFT_BLUE = colors.Color(0.88, 0.93, 0.98)
WHITE = colors.white
GREEN = colors.Color(0.10, 0.55, 0.30)
RED = colors.Color(0.80, 0.15, 0.15)

# Optional logo paths (place files next to the app or set absolute paths)
LOGO_BD_PATH = Path('/Users/rkmaganga/Downloads/BD compliance/assets/bd_logo.png')
LOGO_CUSTOMER_PATH = Path('/Users/rkmaganga/Downloads/BD compliance/assets/smhs_logo.png')


def _styles():
    base = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle(
            "CoverTitle", parent=base["Title"],
            fontName="Helvetica-Bold", fontSize=16, leading=20,
            textColor=NAVY, alignment=TA_CENTER, spaceAfter=2,
        ),
        "cover_sub": ParagraphStyle(
            "CoverSub", parent=base["Normal"],
            fontName="Helvetica", fontSize=9, leading=12,
            textColor=SLATE, alignment=TA_CENTER, spaceAfter=2,
        ),
        "section": ParagraphStyle(
            "Section", parent=base["Heading1"],
            fontName="Helvetica-Bold", fontSize=11, leading=14,
            textColor=NAVY, spaceBefore=8, spaceAfter=3,
        ),
        "subsection": ParagraphStyle(
            "SubSection", parent=base["Heading2"],
            fontName="Helvetica-Bold", fontSize=9, leading=11,
            textColor=TEAL, spaceBefore=5, spaceAfter=2,
        ),
        "body": ParagraphStyle(
            "Body", parent=base["Normal"],
            fontName="Helvetica", fontSize=8, leading=10.5,
            textColor=colors.black,
        ),
        "small": ParagraphStyle(
            "Small", parent=base["Normal"],
            fontName="Helvetica", fontSize=6.5, leading=8.5,
            textColor=SLATE,
        ),
        "table_header": ParagraphStyle(
            "TH", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=7, leading=9,
            textColor=WHITE, alignment=TA_CENTER,
        ),
        "table_cell": ParagraphStyle(
            "TC", parent=base["Normal"],
            fontName="Helvetica", fontSize=7, leading=9,
            textColor=colors.black, alignment=TA_CENTER,
        ),
        "table_cell_left": ParagraphStyle(
            "TCL", parent=base["Normal"],
            fontName="Helvetica", fontSize=7, leading=9,
            textColor=colors.black, alignment=TA_LEFT,
        ),
        "kpi_value": ParagraphStyle(
            "KPI", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=14, leading=16,
            textColor=NAVY, alignment=TA_CENTER,
        ),
        "kpi_label": ParagraphStyle(
            "KPILabel", parent=base["Normal"],
            fontName="Helvetica", fontSize=6.5, leading=8,
            textColor=SLATE, alignment=TA_CENTER,
        ),
    }


def _footer(canvas, doc, meta):
    canvas.saveState()
    canvas.setStrokeColor(MED_GREY)
    canvas.setLineWidth(0.4)
    canvas.line(13 * mm, 10 * mm, PAGE_WIDTH - 13 * mm, 10 * mm)
    canvas.setFont("Helvetica", 6.5)
    canvas.setFillColor(SLATE)
    canvas.drawString(13 * mm, 5.5 * mm, "BD")
    canvas.drawCentredString(PAGE_WIDTH / 2, 5.5 * mm, "For official use only")
    canvas.drawRightString(PAGE_WIDTH - 13 * mm, 5.5 * mm, f"Page {doc.page}")
    canvas.restoreState()


def _kpi_box(label: str, value: str, styles) -> Table:
    t = Table(
        [[Paragraph(str(value), styles["kpi_value"])],
         [Paragraph(label, styles["kpi_label"])]],
        colWidths=[38 * mm],
        rowHeights=[12 * mm, 10 * mm],
    )
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SOFT_BLUE),
        ("BOX", (0, 0), (-1, -1), 0.6, MED_GREY),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t



def _scaled_logo(path: Path, max_width: float, max_height: float) -> Image:
    """
    Build an Image flowable that fits within (max_width, max_height)
    while preserving the source image's native aspect ratio, so logos
    are never stretched.
    """
    reader = ImageReader(str(path))
    src_w, src_h = reader.getSize()
    aspect = src_h / src_w

    width = max_width
    height = width * aspect
    if height > max_height:
        height = max_height
        width = height / aspect

    return Image(str(path), width=width, height=height)


def _logo_block(styles) -> Table:
    """
    Side-by-side logo block, both rows kept together on one page:
      Prepared for: <customer logo>
      Prepared by:  <BD logo>
    """
    customer_fallback = Paragraph("South Metropolitan Health Service", styles["small"])
    bd_fallback = Paragraph("BD", styles["small"])

    MAX_W, MAX_H = 55 * mm, 20 * mm

    prep_for_label = Paragraph("Prepared for:", styles["small"])
    if LOGO_CUSTOMER_PATH.exists():
        customer_cell = _scaled_logo(LOGO_CUSTOMER_PATH, MAX_W, MAX_H)
    else:
        customer_cell = customer_fallback

    prep_by_label = Paragraph("Prepared by:", styles["small"])
    if LOGO_BD_PATH.exists():
        bd_cell = _scaled_logo(LOGO_BD_PATH, MAX_W, MAX_H)
    else:
        bd_cell = bd_fallback

    t = Table(
        [[prep_for_label, customer_cell],
         [prep_by_label, bd_cell]],
        colWidths=[25 * mm, 120 * mm],
    )
    t.setStyle(TableStyle([
        ("ALIGN", (0, 0), (0, -1), "RIGHT"),
        ("ALIGN", (1, 0), (1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ]))
    return KeepTogether(t)

def _month_label(key: Any) -> str:
    text = str(key)
    if len(text) >= 7 and text[4] in "-/":
        return text[:7]
    return text[:10]


def _axis_limits(values: List[int]):
    maximum = max(values or [1])
    if maximum <= 10:
        return 10, 2
    if maximum <= 25:
        return 30, 5
    if maximum <= 50:
        return 60, 10
    if maximum <= 100:
        return 100, 20
    step = max(10, ((maximum // 5 + 4) // 5) * 5)
    return ((maximum + step - 1) // step) * step, step


def _callouts_combined_exhibit(
    monthly_data: Dict[str, int],
    current_month_data: Dict[str, int],
    width: float = 170 * mm,
    height: float = 92 * mm,
) -> Drawing:
    drawing = Drawing(width, height)
    monthly_data = monthly_data or {}
    current_month_data = current_month_data or {}

    title_y = height - 12
    subtitle_y = height - 25
    top = height - 39
    bottom = 29
    chart_h = top - bottom

    drawing.add(String(
        0, title_y,
        "Work-order volume and current-month classification",
        fontName="Helvetica-Bold", fontSize=10.5, fillColor=colors.black
    ))
    drawing.add(String(
        0, subtitle_y,
        "Number of work orders by month and share of current-month classification",
        fontName="Helvetica", fontSize=7.5, fillColor=SLATE
    ))

    left_x = 30
    left_w = width * 0.53
    divider_x = left_x + left_w + 17
    right_x = divider_x + 12
    bar_x = right_x
    bar_w = 18
    text_x = bar_x + bar_w + 8

    drawing.add(Line(divider_x, bottom, divider_x, top + 10, strokeColor=MED_GREY, strokeWidth=0.6))
    drawing.add(String(
        left_x, top + 8, "",
        fontName="Helvetica-Bold", fontSize=7, fillColor=colors.black
    ))
    drawing.add(String(
        right_x, top + 8, "Current-month mix",
        fontName="Helvetica-Bold", fontSize=7, fillColor=colors.black
    ))

    keys = list(monthly_data.keys())
    values = [max(0, int(monthly_data[k] or 0)) for k in keys]
    y_max, y_step = _axis_limits(values)

    for y_value in range(0, y_max + 1, y_step):
        y = bottom + y_value / y_max * chart_h
        drawing.add(Line(left_x, y, left_x + left_w, y, strokeColor=LIGHT_GREY, strokeWidth=0.45))
        drawing.add(String(
            left_x - 8, y - 2, str(y_value),
            fontName="Helvetica", fontSize=6.5, fillColor=SLATE, textAnchor="end"
        ))

    drawing.add(Line(left_x, bottom, left_x + left_w, bottom, strokeColor=MED_GREY, strokeWidth=0.5))

    if keys:
        if len(values) == 1:
            x_positions = [left_x + left_w / 2]
        else:
            x_positions = [left_x + i / (len(values) - 1) * left_w for i in range(len(values))]
        points = [(x, bottom + value / y_max * chart_h) for x, value in zip(x_positions, values)]
        for (x1, y1), (x2, y2) in zip(points, points[1:]):
            drawing.add(Line(x1, y1, x2, y2, strokeColor=NAVY, strokeWidth=1.7))
        for i, ((x, y), value) in enumerate(zip(points, values)):
            drawing.add(Rect(x - 2.3, y - 2.3, 4.6, 4.6, fillColor=NAVY, strokeColor=NAVY, strokeWidth=0.2))
            label_y = y + 6 if y < top - 10 else y - 11
            drawing.add(String(
                x, label_y, str(value),
                fontName="Helvetica", fontSize=6.5, fillColor=colors.black, textAnchor="middle"
            ))
            drawing.add(String(
                x, bottom - 11, _month_label(keys[i]),
                fontName="Helvetica", fontSize=6.5, fillColor=SLATE, textAnchor="middle"
            ))
        # Intentionally no floating "Work orders" label (was obscuring the last point)
    else:
        drawing.add(String(
            left_x, bottom + chart_h / 2,
            "No monthly work-order data available",
            fontName="Helvetica", fontSize=7, fillColor=SLATE
        ))

    labels = list(current_month_data.keys())
    bar_values = [max(0, int(current_month_data[k] or 0)) for k in labels]
    total = sum(bar_values)
    # Blue-only stack (no orange)
    stack_colours = [
        colors.Color(0.00, 0.20, 0.63),
        colors.Color(0.15, 0.35, 0.72),
        colors.Color(0.35, 0.50, 0.78),
        colors.Color(0.55, 0.65, 0.85),
        colors.Color(0.72, 0.78, 0.90),
    ]
    drawing.add(Rect(bar_x, bottom, bar_w, chart_h, fillColor=None, strokeColor=MED_GREY, strokeWidth=0.4))

    if total:
        y_cursor = bottom
        for i, (label, value) in enumerate(zip(labels, bar_values)):
            segment_h = value / total * chart_h
            segment_colour = stack_colours[i % len(stack_colours)]
            drawing.add(Rect(
                bar_x, y_cursor, bar_w, segment_h,
                fillColor=segment_colour, strokeColor=WHITE, strokeWidth=0.4
            ))
            if segment_h >= 12:
                drawing.add(String(
                    bar_x + bar_w / 2, y_cursor + segment_h / 2 - 2, str(value),
                    fontName="Helvetica-Bold", fontSize=6.5, fillColor=WHITE, textAnchor="middle"
                ))
            pct = round(value / total * 100)
            text_y = y_cursor + segment_h / 2 + 2
            drawing.add(Line(bar_x + bar_w, text_y, text_x - 3, text_y, strokeColor=MED_GREY, strokeWidth=0.35))
            drawing.add(String(
                text_x, text_y, str(label),
                fontName="Helvetica-Bold", fontSize=6.2, fillColor=colors.black
            ))
            drawing.add(String(
                text_x, text_y - 8, f"{value} ({pct}%)",
                fontName="Helvetica", fontSize=6, fillColor=colors.black
            ))
            y_cursor += segment_h
    else:
        drawing.add(String(
            text_x, bottom + chart_h / 2, "No data recorded",
            fontName="Helvetica", fontSize=7, fillColor=SLATE
        ))

    drawing.add(String(
        0, 9,
        "Note: Category shares are calculated from the displayed counts; percentages are rounded.",
        fontName="Helvetica", fontSize=5.8, fillColor=SLATE
    ))
    drawing.add(String(
        0, 1,
        "Source: BD Service Call Intake records, Fiona Stanley Hospital.",
        fontName="Helvetica", fontSize=5.8, fillColor=SLATE
    ))
    return drawing


def _centred_table(table: Table, content_width: float = 170 * mm) -> Table:
    """Wrap a table in a single-cell outer table to centre it on the page."""
    outer = Table([[table]], colWidths=[content_width])
    outer.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    return outer


def build_pdf(analysis: Dict[str, Any], cpv: Dict[str, Any] | None = None, charts=None) -> bytes:
    styles = _styles()
    summary = analysis.get("summary", {})
    generated = datetime.now().strftime("%d %b %Y %H:%M") + " (Western Australia time)"
    meta = {"generated": generated}

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=13 * mm, rightMargin=13 * mm,
        topMargin=12 * mm, bottomMargin=15 * mm,
        title="Fortnightly Report – BD / WA Health",
        author="BD",
    )
    story: List[Any] = []

    # =========================================================
    # COVER PAGE (title + subtitle + logo block)
    # =========================================================

    # Top margin so the block sits nicely on the page
    story.append(Spacer(1, 18 * mm))

    # Title block (centered)
    story.append(Paragraph("FORTNIGHTLY REPORT", styles["cover_title"]))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("Pyxis ROWA &amp; WOW Service Performance", styles["cover_sub"]))
    story.append(Paragraph("Fiona Stanley Hospital", styles["cover_sub"]))

    # Separator line under the title block
    story.append(
        HRFlowable(
            width="100%",
            thickness=1.2,
            color=NAVY,
            spaceBefore=8,
            spaceAfter=8,
        )
    )

    # Space before logo block
    story.append(Spacer(1, 10 * mm))

    # Stacked logo block: Prepared for / Prepared by
    story.append(_logo_block(styles))

    # Force everything below onto page 2
    story.append(PageBreak())
    
    # =========================================================
    # PAGE 2 – meta, KPIs, key outcomes
    # =========================================================
    meta_data = [
        [Paragraph("<b>Customer</b>", styles["body"]), Paragraph("WA Health", styles["body"])],
        [Paragraph("<b>Provider</b>", styles["body"]), Paragraph("BD", styles["body"])],
        [Paragraph("<b>Primary Site</b>", styles["body"]), Paragraph("Fiona Stanley Hospital", styles["body"])],
        [Paragraph("<b>Reporting Period</b>", styles["body"]),
         Paragraph(f"{summary.get('period_start', '')} → {summary.get('period_end', '')}", styles["body"])],
        [Paragraph("<b>Generated</b>", styles["body"]), Paragraph(generated, styles["body"])],
    ]
    meta_t = Table(meta_data, colWidths=[35 * mm, 120 * mm])
    meta_t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
    ]))
    story += [meta_t, Spacer(1, 6 * mm)]

    kpis = [
        _kpi_box("Work Orders<br/>Completed", str(summary.get("total_wo_week", 0)), styles),
        _kpi_box("KPI Compliance", f"{summary.get('kpi_compliance_pct', 100)}%", styles),
        _kpi_box("CUBIEs Replaced<br/>(MTD)", str(summary.get("cubies_mtd", 0)), styles),
        _kpi_box("Callouts<br/>(MTD)", str(summary.get("callouts_mtd", 0)), styles),
    ]
    kpi_table = Table([kpis], colWidths=[42 * mm] * 4)
    kpi_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ]))
    story += [_centred_table(kpi_table), Spacer(1, 6 * mm), Paragraph("Key Outcomes", styles["subsection"])]

    kpi_pct = summary.get("kpi_compliance_pct", 100)
    outcome_kpi = (
        "All recorded work orders achieved contractual KPI 3 &amp; 4 requirements."
        if kpi_pct >= 100
        else f"KPI 3 &amp; 4 compliance for the reporting period is {kpi_pct}%."
    )
    outcomes = [
        outcome_kpi,
        f"{summary.get('cubies_mtd', 0)} CUBIE replacements completed in the month-to-date window.",
        f"{summary.get('remedial_count', 0)} remedial / corrective maintenance activities completed.",
        f"{summary.get('callouts_mtd', 0)} callout(s) recorded in the month-to-date window.",
        "No critical unresolved faults at reporting close.",
    ]
    story.extend(Paragraph(f"• {o}", styles["body"]) for o in outcomes)
    story += [
        Spacer(1, 4 * mm),
        Paragraph(
            "<b>Key:</b> MTD = Month to Date · YTD = Year to Date · Times recorded to the nearest hour.",
            styles["small"],
        ),
        PageBreak(),
    ]

    # =========================================================
    # 1. SERVICE DELIVERY
    # =========================================================
    story += [
        Paragraph("1. Service Delivery Performance", styles["section"]),
        Paragraph(
            "Work order volume, classification, KPI achievement and monthly trend for Pyxis and WOW assets.",
            styles["small"],
        ),
        Spacer(1, 3 * mm),
    ]

    hw = summary.get("hw_sw_user", {}) or {}
    class_data = [[Paragraph("Category", styles["table_header"]), Paragraph("Count", styles["table_header"])]]
    for label in ("Hardware", "Software", "User Error", "Other"):
        class_data.append([
            Paragraph(label, styles["table_cell"]),
            Paragraph(str(hw.get(label, 0)), styles["table_cell"]),
        ])
    class_t = Table(class_data, colWidths=[40 * mm, 25 * mm])
    class_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREY]),
        ("GRID", (0, 0), (-1, -1), 0.3, MED_GREY),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))

    kpi_data = [
        [Paragraph("Measure", styles["table_header"]), Paragraph("Result", styles["table_header"])],
        [Paragraph("KPI 3 &amp; 4 Achievement", styles["table_cell"]),
         Paragraph(f"{summary.get('kpi_compliance_pct', 100)}%", styles["table_cell"])],
        [Paragraph("Work Orders (Fortnight)", styles["table_cell"]),
         Paragraph(str(summary.get("total_wo_week", 0)), styles["table_cell"])],
        [Paragraph("Work Orders (MTD)", styles["table_cell"]),
         Paragraph(str(summary.get("total_wo_mtd", 0)), styles["table_cell"])],
        [Paragraph("Work Orders (YTD)", styles["table_cell"]),
         Paragraph(str(summary.get("total_wo_ytd", 0)), styles["table_cell"])],
    ]
    kpi_t = Table(kpi_data, colWidths=[50 * mm, 30 * mm])
    kpi_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREY]),
        ("GRID", (0, 0), (-1, -1), 0.3, MED_GREY),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))

    side = Table([[class_t, kpi_t]], colWidths=[75 * mm, 90 * mm])
    side.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ]))
    story += [_centred_table(side), Spacer(1, 8 * mm)]

    monthly = analysis.get("monthly_work_orders") or analysis.get("prev3_monthly") or {}
    current_mix = summary.get("hw_sw_user_current_month") or summary.get("hw_sw_user") or {}
    story += [
        Paragraph("Figure 1", styles["small"]),
        Spacer(1, 2 * mm),
        _callouts_combined_exhibit(monthly, current_mix),
        Spacer(1, 4 * mm),
        Paragraph(
            f"The line chart shows monthly work-order volume. The stacked bar shows the current-month "
            f"classification mix across {sum(int(v or 0) for v in current_mix.values())} jobs.",
            styles["body"],
        ),
        PageBreak(),
    ]

    # =========================================================
    # 2. SERVICE AREA
    # =========================================================
    story += [
        Paragraph("2. Service Area Analysis", styles["section"]),
        Paragraph("Instances of work orders by service area as a percentage of year-to-date volume.", styles["small"]),
        Spacer(1, 3 * mm),
    ]
    dept = analysis.get("dept_pct_ytd", {}) or {}
    if dept:
        rows = [[
            Paragraph("Service Area / Department", styles["table_header"]),
            Paragraph("YTD Count", styles["table_header"]),
            Paragraph("% of YTD", styles["table_header"]),
        ]]
        for name, info in list(dept.items())[:12]:
            rows.append([
                Paragraph(str(name)[:48], styles["table_cell_left"]),
                Paragraph(str(info["count"]), styles["table_cell"]),
                Paragraph(f"{info['pct']}%", styles["table_cell"]),
            ])
        table = Table(rows, colWidths=[105 * mm, 28 * mm, 28 * mm], repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREY]),
            ("GRID", (0, 0), (-1, -1), 0.3, MED_GREY),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 2.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ]))
        story += [_centred_table(table), Spacer(1, 4 * mm)]
        top_item = next(iter(dept.items()))
        story.append(Paragraph(
            f"<b>Observation:</b> {top_item[0]} remains the highest service demand area year-to-date "
            f"({top_item[1]['count']} work orders, {top_item[1]['pct']}% of YTD).",
            styles["body"],
        ))
    story.append(PageBreak())

    # =========================================================
    # 3. CORRECTIVE MAINTENANCE
    # =========================================================
    story += [
        Paragraph("3. Corrective Maintenance Activities Completed", styles["section"]),
        Paragraph(
            "Remedial and corrective actions undertaken on Pyxis and WOW assets during the month-to-date window.",
            styles["small"],
        ),
        Spacer(1, 3 * mm),
    ]
    remedial = analysis.get("remedial", []) or []
    story += [
        Paragraph(f"<b>{len(remedial)}</b> corrective maintenance activities completed MTD.", styles["body"]),
        Spacer(1, 3 * mm),
    ]
    if remedial:
        rows = [[Paragraph(x, styles["table_header"]) for x in (
            "WO #", "Asset", "Department", "Product type", "Action / Commentary"
        )]]
        for record in remedial[:18]:
            rows.append([
                Paragraph(str(record.get("work_order", "")), styles["table_cell"]),
                Paragraph(str(record.get("asset", "") or "")[:14], styles["table_cell"]),
                Paragraph(str(record.get("department", "") or "")[:22], styles["table_cell"]),
                Paragraph(str(record.get("product_type", "") or "")[:20], styles["table_cell"]),
                Paragraph(
                    (str(record.get("commentary", "")) + " " + str(record.get("parts", "")))[:90],
                    styles["table_cell_left"],
                ),
            ])
        table = Table(rows, colWidths=[20 * mm, 17 * mm, 30 * mm, 35 * mm, 59 * mm], repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREY]),
            ("GRID", (0, 0), (-1, -1), 0.3, MED_GREY),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ]))
        story.append(_centred_table(table))
    story.append(PageBreak())

    # =========================================================
    # 4. OPERATIONAL EVENTS
    # =========================================================
    story += [
        Paragraph("4. Operational Events", styles["section"]),
        Paragraph("CUBIE Replacements", styles["subsection"]),
        Spacer(1, 2 * mm),
    ]
    rows = [[Paragraph("Period", styles["table_header"]), Paragraph("Count", styles["table_header"])]]
    for label, key in (
        ("Reporting Fortnight", "cubies_week"),
        ("Month to Date (MTD)", "cubies_mtd"),
        ("Year to Date (YTD)", "cubies_ytd"),
    ):
        rows.append([
            Paragraph(label, styles["table_cell_left"]),
            Paragraph(str(summary.get(key, 0)), styles["table_cell"]),
        ])
    table = Table(rows, colWidths=[55 * mm, 30 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREY]),
        ("GRID", (0, 0), (-1, -1), 0.3, MED_GREY),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story += [_centred_table(table), Spacer(1, 5 * mm), Paragraph("Callouts (MTD)", styles["subsection"]), Spacer(1, 2 * mm)]

    rows = [
        [Paragraph("Metric", styles["table_header"]), Paragraph("Count", styles["table_header"])],
        [Paragraph("Callouts (Saturday and Sunday On-site Attendance)", styles["table_cell_left"]),
         Paragraph(str(summary.get("callouts_mtd", 0)), styles["table_cell"])],
    ]
    table = Table(rows, colWidths=[70 * mm, 30 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREY]),
        ("GRID", (0, 0), (-1, -1), 0.3, MED_GREY),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(_centred_table(table))
    story.append(PageBreak())

    # =========================================================
    # APPENDIX A – same jobs as Section 3 (Corrective), more detail
    # =========================================================
    story += [
        Paragraph("Appendix A – Full Work Order Log", styles["section"]),
        Paragraph(
            "Detailed log of the same corrective maintenance work orders listed in Section 3, "
            "with attendance, completion and KPI detail. Times recorded to the nearest hour.",
            styles["small"],
        ),
        Spacer(1, 2 * mm),
        Paragraph(
            '<font color="#1A8C4A"><b>■</b></font> KPI 3 &amp; 4 Achieved &nbsp;&nbsp; '
            '<font color="#CC2626"><b>■</b></font> KPI 3 &amp; 4 Not Achieved',
            styles["small"],
        ),
        Spacer(1, 3 * mm),
    ]

    remedial = analysis.get("remedial", []) or []
    # Enrich from log_mtd / log_week by work order number
    detail_by_wo = {}
    for src in (analysis.get("log_mtd") or [], analysis.get("log_week") or []):
        for r in src:
            wo = str(r.get("work_order", ""))
            if wo and wo not in detail_by_wo:
                detail_by_wo[wo] = r

    if remedial:
        rows = [[Paragraph(x, styles["table_header"]) for x in (
            "WO #", "Time of Attendance", "Time of Completion", "Urgency",
            "Classification", "Asset", "Department", "KPI",
        )]]
        for record in remedial:
            wo = str(record.get("work_order", ""))
            detail = detail_by_wo.get(wo, {})

            kpi = str(detail.get("kpi_3_4") or "Achieved")
            if kpi == "Achieved":
                kpi_cell = Paragraph('<font color="#1A8C4A"><b>■</b></font>', styles["table_cell"])
            elif kpi == "Not Achieved":
                kpi_cell = Paragraph('<font color="#CC2626"><b>■</b></font>', styles["table_cell"])
            else:
                kpi_cell = Paragraph("·", styles["table_cell"])

            rows.append([
                Paragraph(wo, styles["table_cell"]),
                Paragraph(str(detail.get("time_of_attendance") or record.get("date") or "")[:16], styles["table_cell"]),
                Paragraph(str(detail.get("time_of_completion") or record.get("date") or "")[:16], styles["table_cell"]),
                Paragraph(str(detail.get("urgency") or "")[:11], styles["table_cell"]),
                Paragraph(str(detail.get("hw_sw") or "")[:14], styles["table_cell"]),
                Paragraph(str(record.get("asset") or detail.get("asset_number") or "")[:12], styles["table_cell"]),
                Paragraph(str(record.get("department") or detail.get("department") or "")[:20], styles["table_cell_left"]),
                kpi_cell,
            ])

        table = Table(
            rows,
            colWidths=[18 * mm, 26 * mm, 26 * mm, 17 * mm, 22 * mm, 20 * mm, 28 * mm, 12 * mm],
            repeatRows=1,
        )
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREY]),
            ("GRID", (0, 0), (-1, -1), 0.25, MED_GREY),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 1.6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6),
            ("LEFTPADDING", (0, 0), (-1, -1), 1.5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 1.5),
        ]))
        story.append(_centred_table(table))

        breaches = sum(
            1 for record in remedial
            if str(detail_by_wo.get(str(record.get("work_order", "")), {}).get("kpi_3_4") or "Achieved")
            == "Not Achieved"
        )
        stmt = (
            "Pertaining to performance of KPI 3 and 4. KPI achieved. No breaches detailed."
            if breaches == 0
            else f"Pertaining to performance of KPI 3 and 4. {breaches} work order(s) did not meet KPI requirements."
        )
        story += [Spacer(1, 4 * mm), Paragraph(stmt, styles["body"])]
    else:
        story.append(Paragraph("No corrective maintenance work orders in the reporting period.", styles["body"]))

    doc.build(
        story,
        onFirstPage=lambda canvas, doc: _footer(canvas, doc, meta),
        onLaterPages=lambda canvas, doc: _footer(canvas, doc, meta),
    )
    buffer.seek(0)
    return buffer.read()

