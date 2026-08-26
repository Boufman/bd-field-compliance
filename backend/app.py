from __future__ import annotations
from pathlib import Path
from io import BytesIO
from datetime import date
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
import traceback

from .config import (
    STATIC_DIR, LOGO_DIR, FRONTEND_DIST_DIR, PDF_DEFAULT_NAME,
    CUSTOMER_NAME, PROVIDER_NAME, SITE_NAME,
)
from .analysis_engine import parser, reporting
from .pdf_engine.pdf_builder import build_pdf

app = FastAPI(
    title="Field Compliance Report – BD / WA Health",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
    expose_headers=["Content-Disposition"], allow_credentials=True,
)

@app.get("/")
def root():
    index_path = FRONTEND_DIST_DIR / "index.html"
    if not index_path.exists():
        return JSONResponse(status_code=503, content={"detail": "Frontend not built yet."})
    return FileResponse(str(index_path))

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "Field Compliance Report", "customer": CUSTOMER_NAME}

@app.post("/api/preview")
async def preview_intake(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        return parser.classify_with_preview(BytesIO(contents), file.filename or "intake.xlsx")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/analyse")
async def analyse_intake(file: UploadFile = File(...), period_end: str = Form(None)):
    try:
        contents = await file.read()
        parsed = parser.parse_excel(BytesIO(contents), file.filename or "intake.xlsx")
        pe = date.fromisoformat(period_end) if period_end else None
        analysis = reporting.build_report(parsed["records"], report_period_end=pe)
        meta = {"customer": CUSTOMER_NAME, "provider": PROVIDER_NAME, "site": SITE_NAME}
        pdf_bytes = build_pdf(analysis)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{PDF_DEFAULT_NAME}"'},
        )
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Analysis / PDF generation failed")

@app.post("/api/analyse-json")
async def analyse_json(file: UploadFile = File(...), period_end: str = Form(None)):
    try:
        contents = await file.read()
        parsed = parser.parse_excel(BytesIO(contents), file.filename or "intake.xlsx")
        pe = date.fromisoformat(period_end) if period_end else None
        analysis = reporting.build_report(parsed["records"], report_period_end=pe)
        analysis["source_filename"] = parsed["filename"]
        analysis["source_record_count"] = parsed["record_count"]
        return analysis
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
