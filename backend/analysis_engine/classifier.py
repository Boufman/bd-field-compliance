"""
Full ColdProof v3.6 classification pipeline.

- Uses parser for excursions + base stats.
- Adds:
    * GEYER classification
    * Fridge signature
    * AM/PM logging block
    * Timezone tagging for downstream PDF + UI
"""

from __future__ import annotations

from typing import Union, IO, Dict, Any

from . import parser
from . import fridge_signature
from . import reporting
from ..config import AM_PM_LOGGING_BLOCK

SourceType = Union[str, IO[bytes]]


def _extract_temps_for_signature(source: SourceType):
    """
    Reuses parser's loader to get temps for fridge signature.
    """
    df = parser._load_temperature_data(source)  # type: ignore[attr-defined]
    _, temps = parser._extract_time_and_temp(df)  # type: ignore[attr-defined]
    return temps


def run_full_analysis(
    source: SourceType,
    original_filename: str | None = None,
    timezone: str = "UTC",
) -> Dict[str, Any]:
    """
    High-level API for the backend:

    Returns:
        {
          ...parser_result,
          "geyer": {...},
          "fridge_signature": {...},
          "summary": {...},
          "am_pm_logging": {...},
          "timezone": "Australia/Perth",
        }
    """
    # Base parser result (now timezone-aware metadata)
    base = parser.classify_breach(
        source,
        original_filename=original_filename,
        timezone=timezone,
    )

    # Reload temps for fridge signature (parser functions rewind file-like sources)
    temps = _extract_temps_for_signature(source)
    fridge_sig = fridge_signature.compute_fridge_signature(temps)

    excursions = base.get("excursions", [])
    geyer = reporting.classify_geyer(excursions)

    # Base stats for summary
    stats = {
        "min_temp": base.get("min_temp"),
        "max_temp": base.get("max_temp"),
        "total_excursions": base.get("total_excursions"),
        "reportable_count": base.get("reportable_count"),
    }

    summary = reporting.build_summary(
        classification=base.get("classification", ""),
        geyer=geyer,
        fridge_signature=fridge_sig,
        base_stats=stats,
    )

    # AM/PM logging block as required
    am_pm_logging = {
        "required": AM_PM_LOGGING_BLOCK["required"],
        "note": AM_PM_LOGGING_BLOCK["note"],
    }

    base.update(
        {
            "geyer": geyer,
            "fridge_signature": fridge_sig,
            "summary": summary,
            "am_pm_logging": am_pm_logging,
            "timezone": timezone,   # <── what PDF & cpvault will read
        }
    )

    return base