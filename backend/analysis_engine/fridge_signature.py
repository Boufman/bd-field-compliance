"""
Fridge signature engine.

Classifies logger behaviour:
- Purpose-Built Vaccine Refrigerator (PBVR)
- Domestic/Bar Fridge (Non-Compliant)
- Uncertain
"""

from __future__ import annotations

from typing import Sequence, Dict, Any

import numpy as np

from .config import (
    RANGE_PBVR_MAX,
    STD_PBVR_MAX,
    RANGE_DOMESTIC_MIN,
    STD_DOMESTIC_MIN,
)


def compute_fridge_signature(temps: Sequence[float]) -> Dict[str, Any]:
    temps_arr = np.asarray(list(temps), dtype=float)
    if temps_arr.size == 0:
        return {
            "fridge_type": "Unknown",
            "range": None,
            "std": None,
            "notes": ["No valid temperature points detected."],
        }

    temp_range = float(np.max(temps_arr) - np.min(temps_arr))
    std = float(np.std(temps_arr))

    if temp_range < RANGE_PBVR_MAX and std < STD_PBVR_MAX:
        fridge_type = "Purpose-Built Vaccine Refrigerator (PBVR)"
        notes = ["Narrow range and low variability consistent with PBVR."]
    elif temp_range > RANGE_DOMESTIC_MIN or std > STD_DOMESTIC_MIN:
        fridge_type = "Domestic/Bar Fridge (Non-Compliant)"
        notes = ["Wide range and/or high variability suggests domestic/non-compliant fridge."]
    else:
        fridge_type = "Uncertain"
        notes = ["Signature between PBVR and domestic thresholds; consider service/inspection."]

    return {
        "fridge_type": fridge_type,
        "range": round(temp_range, 2),
        "std": round(std, 2),
        "notes": notes,
    }
