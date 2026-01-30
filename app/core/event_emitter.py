from typing import Dict

from app.core.lifecycle import validate_transition
from app.core.role_guard import validate_role_authority
from app.storage.event_store import append_event, load_all_events
from app.intelligence.geo_resolver import resolve_location


class EventEmissionError(Exception):
    """Raised when event emission fails."""
    pass


def emit_event(
    *,
    shipment_id: str,
    current_state: str,
    next_state: str,
    event_type: str,
    role: str,
    metadata: Dict | None = None
) -> Dict:
    """
    Emit a domain event safely.

    This function enforces:
    - Idempotent shipment creation
    - Role authority
    - Lifecycle validity
    - Geo enrichment (on shipment creation)
    - Immutable event storage

    This is the ONLY allowed way to change system state.
    """

    metadata = metadata or {}

    try:
        # --------------------------------------------------
        # 0. Prevent duplicate shipment creation
        # --------------------------------------------------
        if event_type == "SHIPMENT_CREATED":
            existing_events = load_all_events()
            for e in existing_events:
                if (
                    e["shipment_id"] == shipment_id
                    and e["event_type"] == "SHIPMENT_CREATED"
                ):
                    raise EventEmissionError(
                        f"Shipment '{shipment_id}' already exists"
                    )

        # --------------------------------------------------
        # 1. Enforce role authority
        # --------------------------------------------------
        validate_role_authority(
            role=role,
            current_state=current_state,
            event_type=event_type
        )

        # --------------------------------------------------
        # 2. Enforce lifecycle transition
        # --------------------------------------------------
        validate_transition(
            current_state=current_state,
            next_state=next_state
        )

        # --------------------------------------------------
        # 3. GEO ENRICHMENT (ONLY ON CREATION)
        # --------------------------------------------------
        if event_type == "SHIPMENT_CREATED":
            source_raw = metadata.get("source")
            destination_raw = metadata.get("destination")

            source_geo = resolve_location(source_raw) if source_raw else {}
            destination_geo = resolve_location(destination_raw) if destination_raw else {}

            metadata = {
                **metadata,

                # ---- Source ----
                "source_city": source_geo.get("city"),
                "source_state": source_geo.get("state"),
                "source_state_code": source_geo.get("state_code"),
                "source_geo_confidence": source_geo.get("confidence"),

                # ---- Destination ----
                "destination_city": destination_geo.get("city"),
                "destination_state": destination_geo.get("state"),
                "destination_state_code": destination_geo.get("state_code"),
                "destination_geo_confidence": destination_geo.get("confidence"),
            }

        # --------------------------------------------------
        # 4. Append immutable event
        # --------------------------------------------------
        event = append_event({
            "event_type": event_type,
            "shipment_id": shipment_id,
            "role": role,
            "previous_state": current_state,
            "new_state": next_state,
            "metadata": metadata
        })

        return event

    except Exception as e:
        raise EventEmissionError(str(e)) from e
