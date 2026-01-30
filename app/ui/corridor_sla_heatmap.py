from collections import defaultdict
from app.core.read_model import get_all_shipments_state
from app.intelligence.sla_engine import predict_sla_breach


def get_corridor_sla_matrix():
    """
    Returns lane-level SLA health:
    (source_state, destination_state) → metrics
    """

    shipments = get_all_shipments_state()
    corridors = defaultdict(list)

    for s in shipments.values():
        src = s.get("source_state")
        dst = s.get("destination_state")
        if not src or not dst:
            continue
        corridors[(src, dst)].append(s)

    matrix = []

    for (src, dst), items in corridors.items():
        sla_scores = []
        for s in items:
            sla = predict_sla_breach(history=s["history"])
            sla_scores.append(sla["breach_probability"])

        matrix.append({
            "source": src,
            "destination": dst,
            "avg_breach_prob": round(sum(sla_scores) / len(sla_scores), 2),
            "shipment_count": len(items),
        })

    return matrix
