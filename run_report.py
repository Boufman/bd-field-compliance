"""
BD Field Compliance – CLI
Usage:
  BD_Field_Compliance.exe "input.xlsx" "output.pdf"
"""
from __future__ import annotations

import sys
from pathlib import Path
from io import BytesIO

if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).resolve().parent
    BUNDLE_DIR = Path(getattr(sys, "_MEIPASS", APP_DIR))
else:
    APP_DIR = Path(__file__).resolve().parent
    BUNDLE_DIR = APP_DIR

# Import modules by folder, not as a package
sys.path.insert(0, str(BUNDLE_DIR))
sys.path.insert(0, str(BUNDLE_DIR / "backend"))
sys.path.insert(0, str(BUNDLE_DIR / "backend" / "analysis_engine"))
sys.path.insert(0, str(BUNDLE_DIR / "backend" / "pdf_engine"))

from parser import parse_excel
from reporting import build_report
from pdf_builder import build_pdf

def main() -> None:
    if len(sys.argv) >= 2:
        excel_path = Path(sys.argv[1])
    else:
        print('Usage: BD_Field_Compliance.exe "input.xlsx" "output.pdf"')
        sys.exit(1)

    if len(sys.argv) >= 3:
        out_path = Path(sys.argv[2])
    else:
        out_path = APP_DIR / "output.pdf"

    print(f"Input:  {excel_path}")
    print(f"Output: {out_path}")

    if not excel_path.exists():
        print(f"File not found: {excel_path}")
        sys.exit(1)

    data = excel_path.read_bytes()
    parsed = parse_excel(BytesIO(data), excel_path.name)
    analysis = build_report(parsed["records"])
    pdf_bytes = build_pdf(analysis)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(pdf_bytes)
    print(f"Done: {out_path}")

if __name__ == "__main__":
    main()
