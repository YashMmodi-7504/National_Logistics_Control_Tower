from collections import defaultdict
from typing import Dict, List

from app.storage.event_store import load_all_events
from app.core.read_model import get_all_shipments_state


# ==================================================
# STATE-WISE AGGREGATION (SENDER VIEW)
# ==================================================
def get_state_wise_sender_summary() -> Dict[str, Dict]:
    """
    Returns aggregated shipment counts by SOURCE STATE.

    Example:
    {
        "Gujarat": {
            "total": 5,
            "CREATED": 2,
            "IN_TRANSIT": 1,
            "HIGH_RISK": 1
        }
    }
    """

    shipments = get_all_shipments_state()
    events = load_all_events()

    # shipment_id -> source_state
    source_state_by_shipment = {}

    for e in events:
        if e["event_type"] == "SHIPMENT_CREATED":
            state = e.get("metadata", {}).get("source_state")
            if state:
                source_state_by_shipment[e["shipment_id"]] = state

    summary = defaultdict(lambda: defaultdict(int))

    for shipment_id, shipment in shipments.items():
        state = source_state_by_shipment.get(shipment_id)
        if not state:
            continue

        current_state = shipment["current_state"]

        summary[state]["total"] += 1
        summary[state][current_state] += 1

        # Optional AI signal placeholder
        if shipment.get("risk", 0) >= 70:
            summary[state]["HIGH_RISK"] += 1

    return dict(summary)


# ==================================================
# STATE DRILL-DOWN (SHIPMENT LEVEL)
# ==================================================
def get_shipments_by_source_state(state_name: str) -> List[Dict]:
    """
    Returns all shipments whose SOURCE STATE matches the given state.

    Used for:
    - Manager drill-down
    - Heatmap click inspection
    """

    shipments = get_all_shipments_state()
    events = load_all_events()

    source_state_by_shipment = {}
    source_city_by_shipment = {}
    destination_by_shipment = {}

    for e in events:
        if e["event_type"] == "SHIPMENT_CREATED":
            meta = e.get("metadata", {})
            source_state_by_shipment[e["shipment_id"]] = meta.get("source_state")
            source_city_by_shipment[e["shipment_id"]] = meta.get("source_city")
            destination_by_shipment[e["shipment_id"]] = meta.get("destination")

    results = []

    for shipment_id, shipment in shipments.items():
        if source_state_by_shipment.get(shipment_id) != state_name:
            continue

        results.append({
            "shipment_id": shipment_id,
            "current_state": shipment["current_state"],
            "source": source_city_by_shipment.get(shipment_id),
            "destination": destination_by_shipment.get(shipment_id)
        })

    return results
