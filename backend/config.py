from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"

STATIC_DIR = BACKEND_DIR / "static"
LOGO_DIR = STATIC_DIR / "logos"
FRONTEND_DIST_DIR = FRONTEND_DIR / "dist"

PDF_DEFAULT_NAME = "BD_WA_Health_Fortnightly_Compliance_Report.pdf"

CUSTOMER_NAME = "Western Australia Health"
PROVIDER_NAME = "Becton Dickinson"
SITE_NAME = "Fiona Stanley Hospital"
REPORT_TITLE = "Fortnightly Field Compliance Report"
REPORT_SUBTITLE = "Service Call & Work Order Compliance – Automation Equipment"