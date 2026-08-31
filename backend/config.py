from pathlib import Path

# Project root (parent of backend/)
BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_DIR = BASE_DIR / "static"
LOGO_DIR = BASE_DIR / "assets"
FRONTEND_DIST_DIR = BASE_DIR / "frontend" / "dist"

PDF_DEFAULT_NAME = "BD_WA_Health_Fortnightly_Compliance_Report.pdf"

CUSTOMER_NAME = "Western Australia Health"
PROVIDER_NAME = "BD"
SITE_NAME = "Fiona Stanley Hospital"
