# app/async_engine/snapshot_worker.py

import time
from typing import Dict, Any, List

from app.storage.event_store import load_all_events
from app.core.snapshot_store import (
    write_snapshot,
    SLA_SNAPSHOT,
    CORRIDOR_SNAPSHOT,
    HEATMAP_SNAPSHOT,
    ALERTS_SNAPSHOT,
)
from app.core.audit_snapshot_store import write_audit_snapshot
from app.core.access_guard import check_access_with_reason

# Intelligence engines
from app.intelligence.sla_engine import predict_sla_breach
from app.intelligence.corridor_sla_engine import compute_corridor_sla_health
from app.intelligence.corridor_alert_engine import detect_corridor_alerts
from app.core.heatmap_read_model import get_sender_state_heatmap_data
from app.core.read_model import build_state_from_events


# ==================================================
# WORKER CONFIG
# ==================================================

POLL_INTERVAL_SECONDS = 5        # safe for local & prod
MAX_EVENTS_PER_CYCLE = 50_000    # backpressure guard (incremental)


# ==================================================
# INTERNAL STATE
# ==================================================

_last_processed_index = 0


# ==================================================
# SNAPSHOT COMPUTATION
# ==================================================

def compute_sla_snapshot(shipments: Dict[str, Dict]) -> Dict[str, Any]:
    """
    Compute SLA intelligence snapshot per shipment.
    """
    snapshot = {}

    for shipment_id, shipment in shipments.items():
        snapshot[shipment_id] = predict_sla_breach(
            history=shipment["history"]
        )

    return snapshot


def compute_heatmap_snapshot() -> Dict[str, Any]:
    """
    Compute geo heatmap snapshot.
    """
    return {
        "generated_at": time.time(),
        "points": get_sender_state_heatmap_data(),
    }


def compute_audit_snapshot(
    shipments: Dict[str, Dict],
    role: str,
    user_regions: List[str],
) -> List[Dict[str, str]]:
    """
    Compute audit snapshot with denial reasons only.
    
    Args:
        shipments: All shipments from read model
        role: Role to check access for
        user_regions: List of allowed regions for the role
    
    Returns:
        List of denials with shipment_id and reason_code only
        (NEVER exposes full shipment payload)
    """
    denials = []
    
    for shipment_id, shipment in shipments.items():
        access_allowed, denial_reason = check_access_with_reason(
            role=role,
            shipment=shipment,
            user_regions=user_regions,
        )
        
        # Record denial with reason code only
        if not access_allowed and denial_reason is not None:
            denials.append({
                "shipment_id": shipment_id,
                "reason_code": denial_reason,
            })
    
    return denials


# ==================================================
# MAIN WORKER LOOP
# ==================================================

def snapshot_worker_loop() -> None:
    """
    Long-running async snapshot worker.

    Responsibilities:
    - Detect new events
    - Recompute analytics snapshots
    - Persist atomically
    - NEVER block or crash
    """

    global _last_processed_index

    print("🟢 Snapshot worker started")

    while True:
        try:
            events = load_all_events()
            total_events = len(events)

            # --------------------------------------
            # No new events → sleep
            # --------------------------------------
            if total_events == _last_processed_index:
                time.sleep(POLL_INTERVAL_SECONDS)
                continue

            # --------------------------------------
            # Incremental window (backpressure safe)
            # --------------------------------------
            new_events = events[_last_processed_index:]

            if len(new_events) > MAX_EVENTS_PER_CYCLE:
                new_events = new_events[-MAX_EVENTS_PER_CYCLE:]

            print(
                f"🔄 Processing events "
                f"{_last_processed_index} → {total_events}"
            )

            # --------------------------------------
            # Build FULL read model (SSOT)
            # --------------------------------------
            shipments = build_state_from_events(events)

            # --------------------------------------
            # SLA Snapshot
            # --------------------------------------
            sla_snapshot = compute_sla_snapshot(shipments)
            write_snapshot(SLA_SNAPSHOT, {
                "generated_at": time.time(),
                "data": sla_snapshot,
            })

            # --------------------------------------
            # Corridor SLA Snapshot
            # --------------------------------------
            corridor_snapshot = compute_corridor_sla_health()
            write_snapshot(CORRIDOR_SNAPSHOT, {
                "generated_at": time.time(),
                "data": corridor_snapshot,
            })

            # --------------------------------------
            # Alerts Snapshot
            # --------------------------------------
            alerts = detect_corridor_alerts(corridor_snapshot)
            write_snapshot(ALERTS_SNAPSHOT, {
                "generated_at": time.time(),
                "alerts": alerts,
            })

            # --------------------------------------
            # Heatmap Snapshot
            # --------------------------------------
            heatmap_snapshot = compute_heatmap_snapshot()
            write_snapshot(HEATMAP_SNAPSHOT, heatmap_snapshot)

            # --------------------------------------
            # Audit Snapshots (for each role)
            # --------------------------------------
            # Example roles and their regions - in production, load from config
            audit_roles = [
                ("SENDER_MANAGER", ["Maharashtra"]),
                ("RECEIVER_MANAGER", ["Karnataka"]),
                ("VIEWER", []),
            ]
            
            for role, user_regions in audit_roles:
                denials = compute_audit_snapshot(shipments, role, user_regions)
                if denials:  # Only write if there are denials
                    write_audit_snapshot(
                        role=role,
                        denials=denials,
                        generated_at=int(time.time()),
                    )

            # --------------------------------------
            # Advance cursor
            # --------------------------------------
            _last_processed_index = total_events

            print("✅ Snapshots updated successfully")

        except Exception as e:
            # ❗ NEVER crash the worker
            print(f"❌ Snapshot worker error: {e}")

        time.sleep(POLL_INTERVAL_SECONDS)


# ==================================================
# CLI ENTRYPOINT
# ==================================================

if __name__ == "__main__":
    snapshot_worker_loop()
