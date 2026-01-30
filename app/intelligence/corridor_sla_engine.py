from typing import Dict, List
from collections import defaultdict

from app.core.read_model import get_all_shipments_state
from app.intelligence.sla_engine import predict_sla_breach


# --------------------------------------------------
# RISK CLASSIFICATION
# --------------------------------------------------
def classify_corridor_risk(breach_probability: float) -> str:
    """
    Classify corridor SLA risk level.
    """
    if breach_probability >= 0.6:
        return "HIGH"
    elif breach_probability >= 0.3:
        return "MEDIUM"
    return "LOW"


# --------------------------------------------------
# MAIN ENGINE
# --------------------------------------------------
def compute_corridor_sla_health() -> Dict[str, Dict]:
    """
    Compute SLA health metrics for each corridor (source_state → destination_state).

    Hybrid logic:
      final = 70% average breach + 30% worst-case breach
    """

    shipments = get_all_shipments_state()
    corridor_bucket: Dict[str, List[Dict]] = defaultdict(list)

    # --------------------------------------------------
    # 1. GROUP SHIPMENTS BY CORRIDOR
    # --------------------------------------------------
    for shipment in shipments.values():
        src = shipment.get("source_state")
        dst = shipment.get("destination_state")

        if not src or not dst:
            continue

        corridor = f"{src} -> {dst}"
        corridor_bucket[corridor].append(shipment)

    # --------------------------------------------------
    # 2. COMPUTE SLA METRICS
    # --------------------------------------------------
    corridor_metrics: Dict[str, Dict] = {}

    for corridor, corridor_shipments in corridor_bucket.items():
        eta_values = []
        sla_utils = []
        breach_probs = []

        for shipment in corridor_shipments:
            sla = predict_sla_breach(history=shipment["history"])

            eta_values.append(sla["eta_hours"])
            sla_utils.append(sla["sla_utilization"])
            breach_probs.append(sla["breach_probability"])

        if not breach_probs:
            continue

        avg_eta = round(sum(eta_values) / len(eta_values), 2)
        avg_util = round(sum(sla_utils) / len(sla_utils), 2)
        avg_breach = round(sum(breach_probs) / len(breach_probs), 2)
        max_breach = round(max(breach_probs), 2)

        # --------------------------------------------------
        # HYBRID RISK FORMULA
        # --------------------------------------------------
        final_breach = round(
            (0.7 * avg_breach) + (0.3 * max_breach),
            2
        )

        corridor_metrics[corridor] = {
            "corridor": corridor,
            "shipments": len(corridor_shipments),
            "avg_eta_hours": avg_eta,
            "avg_sla_utilization": avg_util,
            "avg_breach_probability": avg_breach,
            "max_breach_probability": max_breach,
            "final_breach_probability": final_breach,
            "risk_level": classify_corridor_risk(final_breach),
        }

    return corridor_metrics
