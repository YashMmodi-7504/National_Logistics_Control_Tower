# app/core/read_model.py

from typing import Dict, List, Optional
from functools import lru_cache

from app.storage.event_store import load_all_events


def build_state_from_events(events: List[Dict]) -> Dict[str, Dict]:
    """
    Replay all domain events and build the current shipment read model.

    SINGLE SOURCE OF TRUTH (SSOT) for:
    - Shipment lifecycle state
    - Geo projections (source / destination / states)
    - Corridor identity (state → state)
    - Downstream SLA / risk / corridor analytics

    ⚠️ STRICT RULES:
    - No business logic
    - No mutations outside this function
    - Deterministic replay only
    """

    shipments: Dict[str, Dict] = {}

    for event in events:
        shipment_id: str = event["shipment_id"]
        event_type: str = event["event_type"]
        metadata: Dict = event.get("metadata", {}) or {}

        # --------------------------------------------------
        # Initialize snapshot (first sight of shipment)
        # --------------------------------------------------
        if shipment_id not in shipments:
            # Get initial state from event if available
            initial_state = event.get("new_state", "UNKNOWN")
            shipments[shipment_id] = {
                "shipment_id": shipment_id,
                "current_state": initial_state,
                "history": [],

                # ---------------- GEO ----------------
                "source": None,
                "destination": None,
                "source_state": None,
                "destination_state": None,

                # ---------------- CORRIDOR ----------------
                "corridor": None,
            }
        else:
            # Only update lifecycle state if event has new_state
            if "new_state" in event:
                shipments[shipment_id]["current_state"] = event["new_state"]

        # --------------------------------------------------
        # Geo projection (ONLY from creation event)
        # --------------------------------------------------
        if event_type == "SHIPMENT_CREATED":
            shipments[shipment_id]["source"] = metadata.get("source")
            shipments[shipment_id]["destination"] = metadata.get("destination")

            source_geo = metadata.get("source_geo") or {}
            destination_geo = metadata.get("destination_geo") or {}

            src_state = source_geo.get("state")
            dst_state = destination_geo.get("state")

            shipments[shipment_id]["source_state"] = src_state
            shipments[shipment_id]["destination_state"] = dst_state

            # Corridor is immutable once known
            if src_state and dst_state:
                shipments[shipment_id]["corridor"] = f"{src_state} -> {dst_state}"
        
        # --------------------------------------------------
        # Handle metadata updates (no state transition)
        # --------------------------------------------------
        if event_type == "METADATA_UPDATED":
            updated_metadata = metadata.get("updated", {})
            if updated_metadata:
                # Update geo information if changed
                if "source" in updated_metadata:
                    shipments[shipment_id]["source"] = updated_metadata["source"]
                if "destination" in updated_metadata:
                    shipments[shipment_id]["destination"] = updated_metadata["destination"]

        # --------------------------------------------------
        # Append immutable event history
        # --------------------------------------------------
        shipments[shipment_id]["history"].append(event)

    return shipments


# ==================================================
# READ MODEL ACCESSORS (CACHED)
# ==================================================

@lru_cache(maxsize=1)
def get_all_shipments_state() -> Dict[str, Dict]:
    """
    Return current read snapshot of ALL shipments.

    ⚡ Cached for performance.
    Safe because event store is append-only.
    """
    events = load_all_events()
    return build_state_from_events(events)


def get_shipment_current_state(shipment_id: str) -> Optional[Dict]:
    """
    Return current read snapshot of a SINGLE shipment.
    """
    shipments = get_all_shipments_state()
    return shipments.get(shipment_id)
