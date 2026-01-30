from app.storage.event_store import load_all_events
from app.intelligence.risk_engine import compute_risk_score
from app.intelligence.geo_resolver import STATE_CENTROIDS


def get_sender_state_heatmap_data():
    events = load_all_events()

    shipments = {}
    for e in events:
        shipments.setdefault(e["shipment_id"], []).append(e)

    state_risk = {}

    for shipment_id, history in shipments.items():
        # find source state
        source_state = None
        for e in history:
            if e["event_type"] == "SHIPMENT_CREATED":
                source_state = (
                    e.get("metadata", {})
                    .get("source_geo", {})
                    .get("state")
                )
                break

        if not source_state:
            continue

        risk = compute_risk_score(history)

        state_risk.setdefault(source_state, []).append(risk)

    heatmap_data = []

    for state, risks in state_risk.items():
        centroid = STATE_CENTROIDS.get(state)
        if not centroid:
            continue

        avg_risk = sum(risks) / len(risks)

        heatmap_data.append({
            "state": state,
            "lat": centroid["lat"],
            "lon": centroid["lon"],
            "weight": avg_risk,              # 🔴 risk-weighted
            "shipment_count": len(risks),
            "risk": round(avg_risk, 1)
        })

    return heatmap_data
