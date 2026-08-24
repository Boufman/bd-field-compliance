from __future__ import annotations

from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.graphics.shapes import Drawing, Rect, String, Line

PAGE_WIDTH, PAGE_HEIGHT = A4

NAVY = colors.Color(0.05, 0.13, 0.28)
TEAL = colors.Color(0.00, 0.45, 0.55)
SLATE = colors.Color(0.30, 0.36, 0.42)
LIGHT_GREY = colors.Color(0.945, 0.95, 0.96)
MED_GREY = colors.Color(0.70, 0.74, 0.78)
SOFT_TEAL = colors.Color(0.88, 0.95, 0.97)
WHITE = colors.white


def _styles():
    base = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle("CoverTitle", parent=base["Title"], fontName="Helvetica-Bold", fontSize=16, leading=20, textColor=NAVY, alignment=TA_LEFT, spaceAfter=2),
        "cover_sub": ParagraphStyle("CoverSub", parent=base["Normal"], fontName="Helvetica", fontSize=9, leading=12, textColor=SLATE, alignment=TA_LEFT, spaceAfter=2),
        "section": ParagraphStyle("Section", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=NAVY, spaceBefore=8, spaceAfter=3),
        "subsection": ParagraphStyle("SubSection", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=9, leading=11, textColor=TEAL, spaceBefore=5, spaceAfter=2),
        "body": ParagraphStyle("Body", parent=base["Normal"], fontName="Helvetica", fontSize=8, leading=10.5, textColor=colors.black),
        "small": ParagraphStyle("Small", parent=base["Normal"], fontName="Helvetica", fontSize=6.5, leading=8.5, textColor=SLATE),
        "table_header": ParagraphStyle("TH", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=7, leading=9, textColor=WHITE, alignment=TA_CENTER),
        "table_cell": ParagraphStyle("TC", parent=base["Normal"], fontName="Helvetica", fontSize=7, leading=9, textColor=colors.black),
        "kpi_value": ParagraphStyle("KPI", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=14, leading=16, textColor=NAVY, alignment=TA_CENTER),
        "kpi_label": ParagraphStyle("KPILabel", parent=base["Normal"], fontName="Helvetica", fontSize=6.5, leading=8, textColor=SLATE, alignment=TA_CENTER),
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
    t = Table([[Paragraph(str(value), styles["kpi_value"])], [Paragraph(label, styles["kpi_label"])]], colWidths=[38 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SOFT_TEAL),
        ("BOX", (0, 0), (-1, -1), 0.6, MED_GREY),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


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


def _callouts_combined_exhibit(monthly_data: Dict[str, int], current_month_data: Dict[str, int], width: float = 170 * mm, height: float = 92 * mm) -> Drawing:
    """Combined McKinsey-inspired line chart and vertical 100% stacked bar."""
    drawing = Drawing(width, height)
    monthly_data = monthly_data or {}
    current_month_data = current_month_data or {}

    title_y = height - 12
    subtitle_y = height - 25
    top = height - 39
    bottom = 29
    chart_h = top - bottom

    drawing.add(String(0, title_y, "Work-order volume and current-month classification", fontName="Helvetica-Bold", fontSize=10.5, fillColor=colors.black))
    drawing.add(String(0, subtitle_y, "Number of work orders by month and share of current-month call-outs", fontName="Helvetica-Bold", fontSize=7.5, fillColor=colors.black))

    left_x = 30
    left_w = width * 0.53
    divider_x = left_x + left_w + 17
    right_x = divider_x + 12
    bar_x = right_x
    bar_w = 18
    text_x = bar_x + bar_w + 8

    drawing.add(Line(divider_x, bottom, divider_x, top + 10, strokeColor=MED_GREY, strokeWidth=0.6))
    drawing.add(String(left_x, top + 8, "Work orders by month", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.black))
    drawing.add(String(right_x, top + 8, "Current-month call-outs", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.black))

    keys = list(monthly_data.keys())
    values = [max(0, int(monthly_data[k] or 0)) for k in keys]
    y_max, y_step = _axis_limits(values)

    for y_value in range(0, y_max + 1, y_step):
        y = bottom + y_value / y_max * chart_h
        drawing.add(Line(left_x, y, left_x + left_w, y, strokeColor=LIGHT_GREY, strokeWidth=0.45))
        drawing.add(String(left_x - 8, y - 2, str(y_value), fontName="Helvetica", fontSize=6.5, fillColor=SLATE, textAnchor="end"))
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
            drawing.add(String(x, label_y, str(value), fontName="Helvetica", fontSize=6.5, fillColor=colors.black, textAnchor="middle"))
            drawing.add(String(x, bottom - 11, _month_label(keys[i]), fontName="Helvetica", fontSize=6.5, fillColor=SLATE, textAnchor="middle"))
        last_x, last_y = points[-1]
        drawing.add(String(min(last_x + 7, left_x + left_w - 2), last_y + 7, "Work orders", fontName="Helvetica-Bold", fontSize=6.5, fillColor=colors.black))
    else:
        drawing.add(String(left_x, bottom + chart_h / 2, "No monthly work-order data available", fontName="Helvetica", fontSize=7, fillColor=SLATE))

    labels = list(current_month_data.keys())
    bar_values = [max(0, int(current_month_data[k] or 0)) for k in labels]
    total = sum(bar_values)
    stack_colours = [colors.Color(0.06, 0.18, 0.42), colors.Color(0.28, 0.39, 0.64), colors.Color(0.46, 0.55, 0.74), colors.Color(0.61, 0.67, 0.80), colors.Color(0.76, 0.80, 0.88)]

    drawing.add(Rect(bar_x, bottom, bar_w, chart_h, fillColor=None, strokeColor=MED_GREY, strokeWidth=0.4))
    if total:
        y_cursor = bottom
        for i, (label, value) in enumerate(zip(labels, bar_values)):
            segment_h = value / total * chart_h
            segment_colour = stack_colours[(len(labels) - 1 - i) % len(stack_colours)]
            drawing.add(Rect(bar_x, y_cursor, bar_w, segment_h, fillColor=segment_colour, strokeColor=WHITE, strokeWidth=0.4))
            if segment_h >= 12:
                drawing.add(String(bar_x + bar_w / 2, y_cursor + segment_h / 2 - 2, str(value), fontName="Helvetica-Bold", fontSize=6.5, fillColor=WHITE, textAnchor="middle"))
            pct = round(value / total * 100)
            text_y = y_cursor + segment_h / 2 + 2
            drawing.add(Line(bar_x + bar_w, text_y, text_x - 3, text_y, strokeColor=MED_GREY, strokeWidth=0.35))
            drawing.add(String(text_x, text_y, str(label), fontName="Helvetica-Bold", fontSize=6.2, fillColor=colors.black))
            drawing.add(String(text_x, text_y - 8, f"{value} call-outs ({pct}%)", fontName="Helvetica", fontSize=6, fillColor=colors.black))
            y_cursor += segment_h
    else:
        drawing.add(String(text_x, bottom + chart_h / 2, "No call-outs recorded", fontName="Helvetica", fontSize=7, fillColor=SLATE))

    drawing.add(String(0, 9, "Note: Current-month category shares are calculated from the displayed call-out counts; percentages are rounded.", fontName="Helvetica", fontSize=5.8, fillColor=SLATE))
    drawing.add(String(0, 1, "Source: BD Service Call Intake records, Fiona Stanley Hospital.", fontName="Helvetica", fontSize=5.8, fillColor=SLATE))
    return drawing


def build_pdf(analysis: Dict[str, Any], cpv: Dict[str, Any] | None = None, charts=None) -> bytes:
    styles = _styles()
    summary = analysis.get("summary", {})
    generated = datetime.now().strftime("%d %b %Y %H:%M") + " (Western Australia time)"
    meta = {"generated": generated}
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=13 * mm, rightMargin=13 * mm, topMargin=12 * mm, bottomMargin=15 * mm, title="Fortnightly Field Compliance Report – BD / WA Health", author="BD")
    story: List[Any] = []

    story += [Spacer(1, 4 * mm), Paragraph("FORTNIGHTLY FIELD COMPLIANCE REPORT", styles["cover_title"]), Paragraph("Pyxis &amp; WOW Service Performance", styles["cover_sub"]), Paragraph("Fiona Stanley Hospital", styles["cover_sub"]), HRFlowable(width="100%", thickness=1.2, color=NAVY, spaceBefore=2, spaceAfter=6)]

    meta_data = [
        [Paragraph("<b>Customer</b>", styles["body"]), Paragraph("Western Australia Health", styles["body"])],
        [Paragraph("<b>Provider</b>", styles["body"]), Paragraph("BD", styles["body"])],
        [Paragraph("<b>Primary Site</b>", styles["body"]), Paragraph("Fiona Stanley Hospital", styles["body"])],
        [Paragraph("<b>Reporting Period</b>", styles["body"]), Paragraph(f"{summary.get('period_start', '')}  →  {summary.get('period_end', '')}", styles["body"])],
        [Paragraph("<b>Generated</b>", styles["body"]), Paragraph(generated, styles["body"])],
    ]
    meta_t = Table(meta_data, colWidths=[35 * mm, 120 * mm])
    meta_t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 1.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5)]))
    story += [meta_t, Spacer(1, 5 * mm)]

    kpis = [
        _kpi_box("Work Orders<br/>Completed", str(summary.get("total_wo_week", 0)), styles),
        _kpi_box("KPI Compliance", f"{summary.get('kpi_compliance_pct', 100)}%", styles),
        _kpi_box("CUBIEs Replaced<br/>(MTD)", str(summary.get("cubies_mtd", 0)), styles),
        _kpi_box("Weekend / OOH<br/>Call-Outs", str(summary.get("ooh_or_weekend_mtd", 0)), styles),
    ]
    kpi_table = Table([kpis], colWidths=[42 * mm] * 4)
    kpi_table.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 1.5), ("RIGHTPADDING", (0, 0), (-1, -1), 1.5)]))
    story += [kpi_table, Spacer(1, 5 * mm), Paragraph("Key Outcomes", styles["subsection"])]
    outcomes = [
        "All recorded work orders achieved contractual KPI requirements (Breach? = No).",
        f"{summary.get('cubies_mtd', 0)} CUBIE replacements completed in the month-to-date window.",
        f"{summary.get('remedial_count', 0)} remedial / corrective maintenance activities completed.",
        "No critical unresolved faults at reporting close.",
    ]
    story.extend(Paragraph(f"•  {outcome}", styles["body"]) for outcome in outcomes)
    story += [Spacer(1, 3 * mm), Paragraph("<b>Key:</b> MTD = Month to Date · OOH = Out of Hours · YTD = Year to Date · Times recorded to the nearest hour.", styles["small"]), PageBreak()]

    story += [Paragraph("1. Service Delivery Performance", styles["section"]), Paragraph("Work order volume, classification, KPI achievement and monthly trend for Pyxis and WOW assets.", styles["small"])]
    hw = summary.get("hw_sw_user", {}) or {}

    class_data = [[Paragraph("Category", styles["table_header"]), Paragraph("Count", styles["table_header"])]]
    for label in ("Hardware", "Software", "User Error", "Other"):
        class_data.append([Paragraph(label, styles["table_cell"]), Paragraph(str(hw.get(label, 0)), styles["table_cell"])])
    class_t = Table(class_data, colWidths=[40 * mm, 25 * mm])
    class_t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREY]), ("GRID", (0, 0), (-1, -1), 0.3, MED_GREY), ("ALIGN", (1, 0), (1, -1), "CENTER"), ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))

    kpi_data = [
        [Paragraph("Measure", styles["table_header"]), Paragraph("Result", styles["table_header"])],
        [Paragraph("KPI 3 &amp; 4 Achievement", styles["table_cell"]), Paragraph(f"{summary.get('kpi_compliance_pct', 100)}%", styles["table_cell"])],
        [Paragraph("Work Orders (Fortnight)", styles["table_cell"]), Paragraph(str(summary.get("total_wo_week", 0)), styles["table_cell"])],
        [Paragraph("Work Orders (MTD)", styles["table_cell"]), Paragraph(str(summary.get("total_wo_mtd", 0)), styles["table_cell"])],
        [Paragraph("Work Orders (YTD)", styles["table_cell"]), Paragraph(str(summary.get("total_wo_ytd", 0)), styles["table_cell"])],
    ]
    kpi_t = Table(kpi_data, colWidths=[50 * mm, 30 * mm])
    kpi_t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREY]), ("GRID", (0, 0), (-1, -1), 0.3, MED_GREY), ("ALIGN", (1, 0), (1, -1), "CENTER"), ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))

    side = Table([[class_t, kpi_t]], colWidths=[75 * mm, 90 * mm])
    side.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]))
    story += [side, Spacer(1, 8 * mm)]

    monthly = analysis.get("monthly_work_orders") or analysis.get("prev3_monthly") or {}
    current_mix = summary.get("hw_sw_user_current_month") or summary.get("hw_sw_user") or {}
    story += [Paragraph("Exhibit 1", styles["small"]), Spacer(1, 1 * mm), _callouts_combined_exhibit(monthly, current_mix), Spacer(1, 3 * mm), Paragraph(f"The line chart shows monthly work-order volume. The stacked bar shows the current-month classification mix across {sum(int(v or 0) for v in current_mix.values())} call-outs.", styles["body"]), PageBreak()]

    story += [Paragraph("2. Service Area Analysis", styles["section"]), Paragraph("Instances of work orders by service area as a percentage of year-to-date volume.", styles["small"])]
    dept = analysis.get("dept_pct_ytd", {}) or {}
    if dept:
        rows = [[Paragraph("Service Area / Department", styles["table_header"]), Paragraph("YTD Count", styles["table_header"]), Paragraph("% of YTD", styles["table_header"])]]
        for name, info in list(dept.items())[:12]:
            rows.append([Paragraph(str(name)[:48], styles["table_cell"]), Paragraph(str(info["count"]), styles["table_cell"]), Paragraph(f"{info['pct']}%", styles["table_cell"])])
        table = Table(rows, colWidths=[105 * mm, 28 * mm, 28 * mm], repeatRows=1)
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREY]), ("GRID", (0, 0), (-1, -1), 0.3, MED_GREY), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (1, 0), (-1, -1), "CENTER"), ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]))
        story += [table, Spacer(1, 3 * mm)]
        top_item = next(iter(dept.items()))
        story.append(Paragraph(f"<b>Observation:</b> {top_item[0]} remains the highest service demand area year-to-date ({top_item[1]['count']} work orders, {top_item[1]['pct']}% of YTD).", styles["body"]))
    story.append(PageBreak())

    story += [Paragraph("3. Corrective Maintenance Activities Completed", styles["section"]), Paragraph("Remedial and corrective actions undertaken on Pyxis and WOW assets during the month-to-date window.", styles["small"])]
    remedial = analysis.get("remedial", []) or []
    story += [Paragraph(f"<b>{len(remedial)}</b> corrective maintenance activities completed MTD.", styles["body"]), Spacer(1, 2 * mm)]
    if remedial:
        rows = [[Paragraph(x, styles["table_header"]) for x in ("WO #", "Asset", "Department", "Status", "Action / Commentary")]]
        for record in remedial[:18]:
            rows.append([Paragraph(str(record.get("work_order", "")), styles["table_cell"]), Paragraph(str(record.get("asset", "") or "")[:14], styles["table_cell"]), Paragraph(str(record.get("department", "") or "")[:18], styles["table_cell"]), Paragraph("Completed", styles["table_cell"]), Paragraph((str(record.get("commentary", "")) + " " + str(record.get("parts", "")))[:90], styles["table_cell"])])
        table = Table(rows, colWidths=[20 * mm, 24 * mm, 32 * mm, 20 * mm, 66 * mm], repeatRows=1)
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREY]), ("GRID", (0, 0), (-1, -1), 0.3, MED_GREY), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2), ("LEFTPADDING", (0, 0), (-1, -1), 2)]))
        story.append(table)
    story.append(PageBreak())

    story += [Paragraph("4. Operational Events", styles["section"]), Paragraph("CUBIE Replacements", styles["subsection"])]
    rows = [[Paragraph("Period", styles["table_header"]), Paragraph("Count", styles["table_header"])] ]
    for label, key in (("Reporting Fortnight", "cubies_week"), ("Month to Date (MTD)", "cubies_mtd"), ("Year to Date (YTD)", "cubies_ytd")):
        rows.append([Paragraph(label, styles["table_cell"]), Paragraph(str(summary.get(key, 0)), styles["table_cell"])])
    table = Table(rows, colWidths=[55 * mm, 30 * mm])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREY]), ("GRID", (0, 0), (-1, -1), 0.3, MED_GREY), ("ALIGN", (1, 0), (1, -1), "CENTER"), ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    story += [table, Spacer(1, 3 * mm), Paragraph("Weekend &amp; Out-of-Hours Support (MTD)", styles["subsection"])]
    rows = [[Paragraph("Metric", styles["table_header"]), Paragraph("Count", styles["table_header"])]]
    for label, key in (("Weekend (Sat/Sun) Call-Outs", "weekend_callouts_mtd"), ("Outside Service Hours (OOH)", "outside_hours_mtd"), ("Combined Unique Events", "ooh_or_weekend_mtd")):
        rows.append([Paragraph(label, styles["table_cell"]), Paragraph(str(summary.get(key, 0)), styles["table_cell"])])
    table = Table(rows, colWidths=[70 * mm, 30 * mm])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREY]), ("GRID", (0, 0), (-1, -1), 0.3, MED_GREY), ("ALIGN", (1, 0), (1, -1), "CENTER"), ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    story += [table, Spacer(1, 3 * mm), Paragraph("System Access &amp; Reboot Events", styles["subsection"])]
    events = analysis.get("system_events", []) or []
    story.append(Paragraph(f"{len(events)} recorded events involving reboot, hard reboot, power cycle or equipment access (MTD).", styles["body"]))
    if events:
        rows = [[Paragraph(x, styles["table_header"]) for x in ("WO #", "Asset", "Department", "Event Summary", "Date")]]
        for record in events[:12]:
            rows.append([Paragraph(str(record.get("work_order", "")), styles["table_cell"]), Paragraph(str(record.get("asset", "") or "")[:13], styles["table_cell"]), Paragraph(str(record.get("department", "") or "")[:16], styles["table_cell"]), Paragraph(str(record.get("event", ""))[:70], styles["table_cell"]), Paragraph(str(record.get("date", ""))[:11], styles["table_cell"])])
        table = Table(rows, colWidths=[20 * mm, 23 * mm, 30 * mm, 70 * mm, 20 * mm], repeatRows=1)
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREY]), ("GRID", (0, 0), (-1, -1), 0.3, MED_GREY), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
        story.append(table)
    story.append(PageBreak())

    story += [Paragraph("5. Compliance &amp; Credentialing", styles["section"]), Paragraph("Personnel &amp; Credential Compliance", styles["subsection"]), Paragraph("All BD personnel nominated for scheduled onsite support maintain current credentialing requirements in accordance with Western Australia Health access requirements. Confirmation of currency is held in the BD credentialing system and can be provided on request.", styles["body"]), Spacer(1, 2 * mm), Paragraph("Scheduled Resourcing – Coming Month", styles["subsection"]), Paragraph(analysis.get("staff_note", ""), styles["body"]), Paragraph("Action: BD Site Lead to attach the current credentialing matrix and roster as Annex B before submission.", styles["small"]), Spacer(1, 3 * mm), Paragraph("Customer Requested Information", styles["subsection"]), Paragraph("No additional information has been formally requested under clause 10 of the reporting requirements during this reporting period.", styles["body"]), Spacer(1, 6 * mm), HRFlowable(width="100%", thickness=0.8, color=NAVY, spaceBefore=2, spaceAfter=4), Paragraph("Attestation", styles["subsection"]), Paragraph("This report has been prepared from the Service Call Intake records maintained by BD field service personnel for the Fiona Stanley Hospital site. Figures are accurate to the best of our knowledge at the time of generation. Source data is retained and available for audit.", styles["body"]), Spacer(1, 6 * mm), Paragraph("_______________________________          _______________________________", styles["body"]), Paragraph("BD Site Lead / Service Manager                    Date", styles["small"]), Spacer(1, 4 * mm), Paragraph("_______________________________          _______________________________", styles["body"]), Paragraph("WA Health Representative (acknowledgment)          Date", styles["small"]), PageBreak()]

    story += [Paragraph("Appendix A – Full Work Order Log", styles["section"]), Paragraph("Complete detailed log containing all fields required under points 1.1 – 1.11 of the Fortnightly Report briefing. Attendance and completion times are recorded to the nearest hour. KPI 3 &amp; 4 status is derived solely from the Breach? column (Yes = Not Achieved).", styles["small"]), Spacer(1, 2.5 * mm)]
    log_week = analysis.get("log_week", []) or []
    if log_week:
        rows = [[Paragraph(x, styles["table_header"]) for x in ("WO #", "Attendance", "Completion", "Urgency", "Classification", "Asset", "KPI 3&amp;4", "Department")]]
        for record in log_week:
            rows.append([Paragraph(str(record.get("work_order", "")), styles["table_cell"]), Paragraph(str(record.get("time_of_attendance", ""))[:16], styles["table_cell"]), Paragraph(str(record.get("time_of_completion", ""))[:16], styles["table_cell"]), Paragraph(str(record.get("urgency", ""))[:11], styles["table_cell"]), Paragraph(str(record.get("hw_sw", "")), styles["table_cell"]), Paragraph(str(record.get("asset_number", ""))[:12], styles["table_cell"]), Paragraph(str(record.get("kpi_3_4", "")), styles["table_cell"]), Paragraph(str(record.get("department", ""))[:20], styles["table_cell"])])
        table = Table(rows, colWidths=[18 * mm, 26 * mm, 26 * mm, 17 * mm, 22 * mm, 20 * mm, 16 * mm, 30 * mm], repeatRows=1)
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREY]), ("GRID", (0, 0), (-1, -1), 0.25, MED_GREY), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 1.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6), ("LEFTPADDING", (0, 0), (-1, -1), 1.5), ("RIGHTPADDING", (0, 0), (-1, -1), 1.5)]))
        story.append(table)
    else:
        story.append(Paragraph("No work orders in the reporting period.", styles["body"]))

    doc.build(story, onFirstPage=lambda canvas, doc: _footer(canvas, doc, meta), onLaterPages=lambda canvas, doc: _footer(canvas, doc, meta))
    buffer.seek(0)
    return buffer.read()
