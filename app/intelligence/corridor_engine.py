# app/intelligence/corridor_engine.py

from typing import Dict, List
from collections import defaultdict

from app.intelligence.risk_engine import compute_risk_score
from app.core.read_model import get_all_shipments_state


# ==================================================
# PUBLIC API
# ==================================================

def compute_corridor_risk() -> Dict[str, Dict]:
    """
    Compute aggregated risk per corridor (state -> state).

    Returns:
    {
        "Gujarat -> Maharashtra": {
            "shipment_count": 42,
            "avg_risk": 63.4,
            "max_risk": 92,
            "high_risk_shipments": 9
        },
        ...
    }
    """

    shipments = get_all_shipments_state()

    corridor_bucket: Dict[str, List[int]] = defaultdict(list)

    # ---------------------------------------------
    # Bucket shipment risks per corridor
    # ---------------------------------------------
    for shipment in shipments.values():
        corridor = shipment.get("corridor")
        history = shipment.get("history", [])

        if not corridor or not history:
            continue

        risk = compute_risk_score(history)
        corridor_bucket[corridor].append(risk)

    # ---------------------------------------------
    # Aggregate corridor metrics
    # ---------------------------------------------
    corridor_risk: Dict[str, Dict] = {}

    for corridor, risks in corridor_bucket.items():
        corridor_risk[corridor] = {
            "shipment_count": len(risks),
            "avg_risk": round(sum(risks) / len(risks), 2),
            "max_risk": max(risks),
            "high_risk_shipments": sum(1 for r in risks if r >= 70),
        }

    return corridor_risk
