# app/core/snapshot_store.py

import json
import os
import threading
from typing import Any, Optional, Dict, List
from security.access_guard import can_access_shipment

# ==================================================
# SNAPSHOT TYPES (PUBLIC CONSTANTS)
# ==================================================

SLA_SNAPSHOT = "sla_snapshot"
CORRIDOR_SNAPSHOT = "corridor_snapshot"
HEATMAP_SNAPSHOT = "heatmap_snapshot"
ALERTS_SNAPSHOT = "alerts_snapshot"

# ==================================================
# STORAGE CONFIG
# ==================================================

_SNAPSHOT_DIR = os.path.join("data", "snapshots")
os.makedirs(_SNAPSHOT_DIR, exist_ok=True)

_LOCK = threading.Lock()


# ==================================================
# INTERNAL HELPERS
# ==================================================

def _snapshot_path(name: str) -> str:
    return os.path.join(_SNAPSHOT_DIR, f"{name}.json")


# ==================================================
# WRITE SNAPSHOT (ATOMIC)
# ==================================================

def write_snapshot(name: str, data: Any) -> None:
    """
    Atomically write a snapshot to disk.

    - Thread-safe
    - Crash-safe (temp file + replace)
    """
    path = _snapshot_path(name)
    tmp_path = f"{path}.tmp"

    with _LOCK:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        os.replace(tmp_path, path)


# ==================================================
# READ SNAPSHOT (SAFE)
# ==================================================

def read_snapshot(name: str) -> Optional[Any]:
    """
    Read a snapshot safely.

    Returns:
    - Parsed JSON data
    - None if snapshot does not exist or is unreadable
    """
    path = _snapshot_path(name)

    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Never break UI due to snapshot corruption
        return None


# ==================================================
# GEO-RBAC AWARE WRAPPERS
# ==================================================

def read_snapshot_with_access_control(
    name: str,
    role: str,
    user_regions: Optional[List[str]] = None,
) -> Optional[Any]:
    """
    Read a snapshot with Geo-RBAC access control enforcement.
    
    Args:
        name: Snapshot name (e.g., SLA_SNAPSHOT, CORRIDOR_SNAPSHOT)
        role: User's role (e.g., SENDER_MANAGER, COO, VIEWER)
        user_regions: Optional list of allowed regions for the user
    
    Returns:
        - Filtered snapshot data if access is allowed
        - None if access is denied or snapshot doesn't exist
    """
    # Read the raw snapshot
    snapshot = read_snapshot(name)
    
    # If snapshot doesn't exist, return None
    if snapshot is None:
        return None
    
    # If snapshot is not a dict or list, return as-is (no filtering needed)
    if not isinstance(snapshot, (dict, list)):
        return snapshot
    
    # Filter based on access control
    if isinstance(snapshot, dict):
        # Single shipment or aggregate data
        if not can_access_shipment(role, snapshot, user_regions):
            return None
        return snapshot
    
    # List of shipments - filter each
    filtered_list = []
    for item in snapshot:
        if isinstance(item, dict) and can_access_shipment(role, item, user_regions):
            filtered_list.append(item)
    
    return filtered_list


def filter_shipments_by_role(
    shipments: List[Dict[str, Any]],
    role: str,
    user_regions: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Filter a list of shipments based on Geo-RBAC access control.
    
    Args:
        shipments: List of shipment dictionaries
        role: User's role
        user_regions: Optional list of allowed regions for the user
    
    Returns:
        Filtered list containing only shipments the user can access
    """
    if not isinstance(shipments, list):
        return []
    
    filtered = []
    for shipment in shipments:
        if isinstance(shipment, dict) and can_access_shipment(role, shipment, user_regions):
            filtered.append(shipment)
    
    return filtered


def can_access_snapshot(
    shipment: Dict[str, Any],
    role: str,
    user_regions: Optional[List[str]] = None,
) -> bool:
    """
    Check if a user can access a specific shipment snapshot.
    
    Args:
        shipment: Shipment dictionary (read-model snapshot)
        role: User's role
        user_regions: Optional list of allowed regions for the user
    
    Returns:
        True if access is allowed, False otherwise
    """
    if not isinstance(shipment, dict):
        return False
    
    return can_access_shipment(role, shipment, user_regions)
