from __future__ import annotations

from io import BytesIO
from typing import Tuple, Dict, Any

from backend.analysis_engine import classifier
from backend import cpvault
from backend.pdf_engine import pdf_builder


def analyse_bytes(csv_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Convenience wrapper: CSV bytes → full analysis JSON.
    """
    buffer = BytesIO(csv_bytes)
    return classifier.run_full_analysis(buffer, original_filename=filename)


def analyse_and_archive(csv_bytes: bytes, filename: str) -> Tuple[Dict[str, Any], str, str]:
    """
    CSV bytes → analysis → PDF → archive.

    Returns:
        (analysis, archive_timestamp, pdf_endpoint)
    """
    analysis = analyse_bytes(csv_bytes, filename)
    cpv = cpvault.load_cpvault()
    pdf_bytes = pdf_builder.build_pdf(analysis, cpv, charts=None)
    timestamp, pdf_path = cpvault.archive_run(
        analysis=analysis,
        csv_bytes=csv_bytes,
        source_filename=filename,
        pdf_bytes=pdf_bytes,
    )
    pdf_endpoint = f"/api/archive/{timestamp}/report.pdf"
    return analysis, timestamp, pdf_endpoint
