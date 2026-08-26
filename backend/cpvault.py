"""
CPVault – encrypted local vault + archive system (MVP with XOR encryption).

Stores:
{
  "staff": ["Name1", "Name2"],
  "active_staff": "Name1",
  "fridge_id": "Fridge 1",
  "pharmacy_details": {},
  "stock_at_risk": []
}
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple

import pytz   # <── REQUIRED
from zoneinfo import ZoneInfo

from .config import CPVAULT_DIR, CPVAULT_FILE, CPVAULT_KEY, ARCHIVE_DIR, PDF_DEFAULT_NAME
from .analysis_engine import hashing


DEFAULT_CPVAULT: Dict[str, Any] = {
    "staff": ["Pharmacist 1", "Pharmacist 2"],
    "active_staff": "Pharmacist 1",
    "fridge_id": "Fridge 1",
    "pharmacy_details": {},
    "stock_at_risk": [],
}


def _ensure_dirs() -> None:
    CPVAULT_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)


def _encrypt(data: bytes) -> bytes:
    return hashing.simple_xor(data, CPVAULT_KEY.encode("utf-8"))


def _decrypt(data: bytes) -> bytes:
    return hashing.simple_xor(data, CPVAULT_KEY.encode("utf-8"))


# ----------------------------------------------------------
# CPVAULT LOAD / SAVE
# ----------------------------------------------------------

def load_cpvault() -> Dict[str, Any]:
    """Load (and decrypt) CPVault JSON, creating a default if missing."""
    _ensure_dirs()
    if not CPVAULT_FILE.exists():
        save_cpvault(DEFAULT_CPVAULT)
        return DEFAULT_CPVAULT.copy()

    raw = CPVAULT_FILE.read_bytes()
    try:
        decoded = _decrypt(raw)
        return json.loads(decoded.decode("utf-8"))
    except Exception:
        # If anything fails, reset to default (MVP behaviour)
        save_cpvault(DEFAULT_CPVAULT)
        return DEFAULT_CPVAULT.copy()


def save_cpvault(data: Dict[str, Any]) -> None:
    """Encrypt and persist CPVault JSON."""
    _ensure_dirs()
    payload = json.dumps(data, indent=2).encode("utf-8")
    CPVAULT_FILE.write_bytes(_encrypt(payload))


def set_active_staff(name: str) -> Dict[str, Any]:
    cpv = load_cpvault()
    if name not in cpv.get("staff", []):
        cpv.setdefault("staff", []).append(name)
    cpv["active_staff"] = name
    save_cpvault(cpv)
    return cpv


def set_fridge_id(fridge_id: str) -> Dict[str, Any]:
    cpv = load_cpvault()
    cpv["fridge_id"] = fridge_id
    save_cpvault(cpv)
    return cpv


# ----------------------------------------------------------
# ARCHIVE SYSTEM (TIMEZONE AWARE)
# ----------------------------------------------------------

def _local_timestamp_from_analysis(analysis: Dict[str, Any]) -> str:
    """
    Generate a timestamp string using the analysis timezone.
    Falls back to UTC if invalid/missing.
    """
    tzname = analysis.get("timezone", "UTC")

    try:
        tz = pytz.timezone(tzname)
        now_local = datetime.now(tz)
    except Exception:
        now_local = datetime.utcnow()

    return now_local.strftime("%Y%m%d-%H%M%S")


def archive_run(
    analysis: Dict[str, Any],
    csv_bytes: bytes,
    source_filename: str,
    pdf_bytes: bytes,
) -> Tuple[str, Path]:
    """
    Create a timestamped archive folder and store:
        - report.pdf
        - source.csv
        - analysis.json

    Returns:
        (timestamp_str, pdf_path)
    """
    _ensure_dirs()

    # TIMESTAMP FIX (was UTC — now full local timezone)
    timestamp = _local_timestamp_from_analysis(analysis)

    run_dir = ARCHIVE_DIR / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    # Save original CSV
    (run_dir / "source.csv").write_bytes(csv_bytes)

    # Save analysis JSON (includes timezone)
    analysis_payload = json.dumps(analysis, indent=2, default=str).encode("utf-8")
    (run_dir / "analysis.json").write_bytes(analysis_payload)

    # Save PDF
    pdf_path = run_dir / PDF_DEFAULT_NAME
    pdf_path.write_bytes(pdf_bytes)

    return timestamp, pdf_path