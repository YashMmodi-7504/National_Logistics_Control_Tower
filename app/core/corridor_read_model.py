# app/core/corridor_read_model.py

from typing import Dict, List
from collections import defaultdict

from app.core.read_model import get_all_shipments_state
from app.intelligence.corridor_engine import compute_corridor_risk


# ==================================================
# READ MODEL: CORRIDOR → SHIPMENTS
# ==================================================

def get_corridor_shipments() -> Dict[str, List[Dict]]:
    """
    Group shipments by corridor (state -> state).

    Returns:
    {
        "Gujarat -> Maharashtra": [
            {
                "shipment_id": "...",
                "current_state": "...",
                "risk": 72,
                "source_state": "...",
                "destination_state": "..."
            },
            ...
        ]
    }
    """

    shipments = get_all_shipments_state()
    corridor_map: Dict[str, List[Dict]] = defaultdict(list)

    for shipment in shipments.values():
        corridor = shipment.get("corridor")
        if not corridor:
            continue

        corridor_map[corridor].append({
            "shipment_id": shipment["shipment_id"],
            "current_state": shipment["current_state"],
            "source_state": shipment.get("source_state"),
            "destination_state": shipment.get("destination_state"),
        })

    return dict(corridor_map)


# ==================================================
# READ MODEL: CORRIDOR SUMMARY (RISK)
# ==================================================

def get_corridor_summary() -> Dict[str, Dict]:
    """
    Corridor-level aggregated risk metrics.
    Thin wrapper over intelligence layer.
    """
    return compute_corridor_risk()
