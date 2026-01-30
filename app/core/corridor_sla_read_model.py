from collections import defaultdict
from app.core.read_model import get_all_shipments_state
from app.intelligence.sla_engine import predict_sla_breach

def get_corridor_sla_matrix():
    """
    Returns:
    {
      ("Gujarat", "Maharashtra"): {
          "count": 42,
          "avg_breach_prob": 0.63,
          "risk_level": "HIGH"
      }
    }
    """
    shipments = get_all_shipments_state()
    corridors = defaultdict(list)

    for s in shipments.values():
        src = s.get("source_state")
        dst = s.get("destination_state")

        if not src or not dst:
            continue

        sla = predict_sla_breach(shipment_history=s["history"])
        corridors[(src, dst)].append(sla["breach_probability"])

    result = {}
    for corridor, probs in corridors.items():
        avg = sum(probs) / len(probs)
        result[corridor] = {
            "count": len(probs),
            "avg_breach_prob": round(avg, 2),
            "risk_level": (
                "HIGH" if avg > 0.7 else
                "MEDIUM" if avg > 0.4 else
                "LOW"
            )
        }

    return result
