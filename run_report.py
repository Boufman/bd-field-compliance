"""
BD Field Compliance – CLI
Usage:
  BD_Field_Compliance.exe
  BD_Field_Compliance.exe "input.xlsx"
  BD_Field_Compliance.exe "input.xlsx" "output.pdf"
"""
from __future__ import annotations

import sys
from pathlib import Path
from io import BytesIO

if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).resolve().parent
else:
    APP_DIR = Path(__file__).resolve().parent

sys.path.insert(0, str(APP_DIR))

from backend.analysis_engine.parser import parse_excel
from backend.analysis_engine.reporting import build_report
from backend.pdf_engine.pdf_builder import build_pdf

def main() -> None:
    if len(sys.argv) >= 2:
        excel_path = Path(sys.argv[1])
    else:
        candidates = list(APP_DIR.glob("*.xlsx")) + list((APP_DIR / "input").glob("*.xlsx"))
        if not candidates:
            print("No Excel found. Put a .xlsx here or pass a path.")
            print('Example: BD_Field_Compliance.exe "input.xlsx" "output.pdf"')
            sys.exit(1)
        excel_path = candidates[0]

    if not excel_path.exists():
        print(f"File not found: {excel_path}")
        sys.exit(1)

    if len(sys.argv) >= 3:
        out_path = Path(sys.argv[2])
    else:
        out_dir = APP_DIR / "output"
        out_dir.mkdir(exist_ok=True)
        out_path = out_dir / "BD_WA_Health_Fortnightly_Compliance_Report.pdf"

    print(f"Input:  {excel_path}")
    print(f"Output: {out_path}")

    try:
        data = excel_path.read_bytes()
        parsed = parse_excel(BytesIO(data), excel_path.name)
        analysis = build_report(parsed["records"])
        pdf_bytes = build_pdf(analysis)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(pdf_bytes)
        print(f"Done: {out_path}")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
