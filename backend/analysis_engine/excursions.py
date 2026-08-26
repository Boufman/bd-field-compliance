"""
Thin wrapper around parser excursion data (placeholder for future advanced logic).
"""

from __future__ import annotations

from typing import Dict, Any, List


def normalise_excursions(analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract excursions list from parser/classifier result.

    Normalises keys/types if needed in future versions; for now,
    it simply returns analysis["excursions"].
    """
    return list(analysis.get("excursions", []))
