"""
Field Compliance – aggregation & KPI engine.
Produces the exact data structure required by the rebuilt PDF builder.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple


def _in_range(d: Optional[date], start: date, end: date) -> bool:
    if d is None:
        return False
    return start <= d <= end


def _month_start(d: date) -> date:
    return d.replace(day=1)


def _prev_n_months(ref: date, n: int) -> Tuple[date, date]:
    first_this = ref.replace(day=1)
    end = first_this - timedelta(days=1)
    y, m = end.year, end.month
    m -= (n - 1)
    while m <= 0:
        m += 12
        y -= 1
    start = date(y, m, 1)
    return start, end


def build_report(records: List[Dict[str, Any]], report_period_end: Optional[date] = None) -> Dict[str, Any]:
    if not records:
        return {"error": "No records", "sections": {}}

    dates = [r["date_submitted"] for r in records if r["date_submitted"]]
    if not dates:
        return {"error": "No dated records", "sections": {}}

    latest = max(dates)
    earliest = min(dates)
    period_end = report_period_end or latest
    period_start = period_end - timedelta(days=13)

    mtd_start = _month_start(period_end)
    ytd_start = date(period_end.year, 1, 1)

    week_records = [r for r in records if _in_range(r["date_submitted"], period_start, period_end)]
    mtd_records = [r for r in records if _in_range(r["date_submitted"], mtd_start, period_end)]
    ytd_records = [r for r in records if _in_range(r["date_submitted"], ytd_start, period_end)]

    def _wo_row(r: Dict) -> Dict:
        # Correct rule: only "Not Achieved" when Breach? column is Yes
        breach_val = str(r.get("breach") or "").strip().upper()
        kpi = "Not Achieved" if breach_val in ("YES", "TRUE", "Y") else "Achieved"

        return {
            "work_order": r["work_order"],
            "time_of_attendance": f"{r.get('date_start') or r.get('date_submitted')} {r.get('time_start') or ''}".strip(),
            "time_of_completion": f"{r.get('date_completed') or ''} {r.get('time_completed') or ''}".strip(),
            "completion_notes": (r.get("completion_comments") or "")[:220],
            "urgency": r.get("severity") or "Non-Urgent",
            "hw_sw": r.get("completion_code") or "Other",
            "equipment_type": r.get("product_classification") or "",
            "product_type": r.get("product_classification") or "",
            "asset_number": r.get("asset_number") or "",
            "kpi_3_4": kpi,
            "completion_comments": r.get("completion_comments") or "",
            "department": r.get("department") or "",
            "completed_by": r.get("completed_by") or "",
            "cubie": r.get("cubie_replaced", False),
            "weekend": r.get("weekend", False) or bool(r.get("saturday_or_sunday")),
            "outside_hours": not r.get("between_8_and_8", True),
            "date_submitted": r.get("date_submitted"),
        }

    log_week = [_wo_row(r) for r in week_records]
    log_mtd = [_wo_row(r) for r in mtd_records]
    log_ytd = [_wo_row(r) for r in ytd_records]

    # Preceding 3 months
    prev3_start, prev3_end = _prev_n_months(period_end, 3)
    prev3_records = [r for r in records if _in_range(r["date_submitted"], prev3_start, prev3_end)]
    monthly_counts: Dict[str, int] = defaultdict(int)
    for r in prev3_records:
        key = r["date_submitted"].strftime("%Y-%m")
        monthly_counts[key] += 1
    avg_3m = round(sum(monthly_counts.values()) / max(len(monthly_counts), 1), 1)

    # CUBIEs
    cubies_week = sum(1 for r in week_records if r.get("cubie_replaced"))
    cubies_mtd = sum(1 for r in mtd_records if r.get("cubie_replaced"))
    cubies_ytd = sum(1 for r in ytd_records if r.get("cubie_replaced"))

    # Weekend / OOH
    weekend_mtd = sum(1 for r in mtd_records if r.get("weekend") or r.get("saturday_or_sunday"))
    outside_hours_mtd = sum(1 for r in mtd_records if not r.get("between_8_and_8", True))
    ooh_or_weekend = sum(
        1 for r in mtd_records
        if (r.get("weekend") or r.get("saturday_or_sunday") or not r.get("between_8_and_8", True))
    )

    # Classification
    code_counts = Counter(
        (r.get("completion_code") or "Other").strip().title()
        for r in mtd_records
    )
    hw_sw_user = {
        "Hardware": code_counts.get("Hardware", 0),
        "Software": code_counts.get("Software", 0),
        "User Error": code_counts.get("User Error", 0) + code_counts.get("Usererror", 0),
        "Other": sum(v for k, v in code_counts.items()
                     if k not in ("Hardware", "Software", "User Error", "Usererror")),
    }

    # Service area
    dept_ytd = Counter((r.get("department") or "Unknown").strip() for r in ytd_records)
    total_ytd = sum(dept_ytd.values()) or 1
    dept_pct = {
        k: {"count": v, "pct": round(100.0 * v / total_ytd, 1)}
        for k, v in dept_ytd.most_common()
    }

    top_depts = [k for k, _ in dept_ytd.most_common(8)]
    monthly_dept: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for r in ytd_records:
        if not r["date_submitted"]:
            continue
        mkey = r["date_submitted"].strftime("%Y-%m")
        d = (r.get("department") or "Unknown").strip()
        if d in top_depts:
            monthly_dept[mkey][d] += 1

    # Remedial / Corrective
    remedial = []
    keywords = ("replaced", "repair", "remedial", "faulty", "failed", "broken",
                "ups", "psu", "drawer engine", "cubie")
    for r in mtd_records:
        comments = (r.get("completion_comments") or "").lower()
        parts = (r.get("part_used") or "").lower()
        if any(k in comments or k in parts for k in keywords) or r.get("cubie_replaced"):
            remedial.append({
                "work_order": r["work_order"],
                "asset": r.get("asset_number"),
                "department": r.get("department"),
                "status": "Completed",
                "commentary": (r.get("completion_comments") or "")[:250],
                "parts": r.get("part_used") or "",
                "date": str(r.get("date_completed") or r.get("date_submitted") or ""),
            })

    # Staff note
    staff_note = (
        "Staff scheduling and credentialing confirmation is maintained outside this intake log. "
        "Confirm current credential status for nominated on-site technicians via the BD credentialing system "
        "prior to submission of this report."
    )

    # System events (reboots / access)
    reboot_keywords = ("reboot", "hard reboot", "restart", "power cycle", "ups", "access")
    system_events = []
    for r in mtd_records:
        c = (r.get("completion_comments") or "").lower()
        if any(k in c for k in reboot_keywords):
            system_events.append({
                "work_order": r["work_order"],
                "asset": r.get("asset_number"),
                "department": r.get("department"),
                "event": (r.get("completion_comments") or "")[:200],
                "date": str(r.get("date_completed") or r.get("date_submitted") or ""),
            })

    # KPI compliance % (based on Breach? column)
    total_kpi = len(week_records) or 1
    achieved = sum(1 for r in week_records
                   if str(r.get("breach") or "").strip().upper() not in ("YES", "TRUE", "Y"))
    kpi_pct = round(100.0 * achieved / total_kpi)

    summary = {
        "period_start": str(period_start),
        "period_end": str(period_end),
        "mtd_start": str(mtd_start),
        "ytd_start": str(ytd_start),
        "total_wo_week": len(week_records),
        "total_wo_mtd": len(mtd_records),
        "total_wo_ytd": len(ytd_records),
        "total_wo_prev3m": len(prev3_records),
        "avg_wo_prev3m": avg_3m,
        "cubies_week": cubies_week,
        "cubies_mtd": cubies_mtd,
        "cubies_ytd": cubies_ytd,
        "weekend_callouts_mtd": weekend_mtd,
        "outside_hours_mtd": outside_hours_mtd,
        "ooh_or_weekend_mtd": ooh_or_weekend,
        "hw_sw_user": hw_sw_user,
        "top_departments": list(dept_pct.items())[:10],
        "remedial_count": len(remedial),
        "system_events_count": len(system_events),
        "data_earliest": str(earliest),
        "data_latest": str(latest),
        "record_count_all": len(records),
        "kpi_compliance_pct": kpi_pct,
    }

    return {
        "summary": summary,
        "log_week": log_week,
        "log_mtd": log_mtd,
        "log_ytd_sample": log_ytd[:100],
        "prev3_monthly": dict(sorted(monthly_counts.items())),
        "dept_pct_ytd": dept_pct,
        "monthly_dept_trend": {k: dict(v) for k, v in sorted(monthly_dept.items())},
        "remedial": remedial,
        "system_events": system_events,
        "staff_note": staff_note,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }