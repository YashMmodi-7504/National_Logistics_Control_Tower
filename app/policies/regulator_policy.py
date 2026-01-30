"""
REGULATOR POLICY

Purpose:
- Declare WHAT a regulator may see
- Snapshot-based visibility only
- Explicit allow-list

Rules:
- Snapshot-based visibility only
- Explicit allow-list
- No deny-list logic
- No side effects
"""

from typing import List, Dict

# ==================================================
# ALLOWED SNAPSHOTS (EXPLICIT ALLOW-LIST)
# ==================================================

ALLOWED_SNAPSHOTS: List[str] = [
    "sla_snapshot",
    "corridor_snapshot",
    "alerts_snapshot",
    "heatmap_snapshot",
]

# ==================================================
# SNAPSHOT DESCRIPTIONS (HUMAN-READABLE)
# ==================================================

SNAPSHOT_DESCRIPTIONS: Dict[str, str] = {
    "sla_snapshot": "SLA breach predictions per shipment",
    "corridor_snapshot": "State-to-state corridor health metrics",
    "alerts_snapshot": "Active SLA breach alerts by corridor",
    "heatmap_snapshot": "Geographic risk distribution heatmap",
}

# ==================================================
# FORBIDDEN OPERATIONS (EXPLICIT)
# ==================================================

FORBIDDEN_OPERATIONS: List[str] = [
    "emit_event",
    "write_snapshot",
    "delete_event",
    "modify_state",
    "invoke_intelligence_engine",
    "access_live_read_model",
]

# ==================================================
# AUDIT EXPORTS (ALLOWED)
# ==================================================

ALLOWED_AUDIT_EXPORTS: List[str] = [
    "access_denials",
    "role_activity",
    "geo_violations",
    "full_trail",
]

# ==================================================
# COMPLIANCE EXPORTS (ALLOWED)
# ==================================================

ALLOWED_COMPLIANCE_EXPORTS: List[str] = [
    "access_control",
    "data_retention",
    "dispute_log",
    "sla_breach",
    "regulatory",
]


# ==================================================
# POLICY VALIDATION
# ==================================================

def is_snapshot_allowed(snapshot_name: str) -> bool:
    """
    Check if a snapshot is allowed for regulator access.
    
    Args:
        snapshot_name: Name of the snapshot
    
    Returns:
        True if allowed, False otherwise
    """
    return snapshot_name in ALLOWED_SNAPSHOTS


def is_operation_forbidden(operation_name: str) -> bool:
    """
    Check if an operation is forbidden for regulator.
    
    Args:
        operation_name: Name of the operation
    
    Returns:
        True if forbidden, False otherwise
    """
    return operation_name in FORBIDDEN_OPERATIONS


def get_snapshot_description(snapshot_name: str) -> str:
    """
    Get human-readable description for a snapshot.
    
    Args:
        snapshot_name: Name of the snapshot
    
    Returns:
        Description or "Unknown snapshot"
    """
    return SNAPSHOT_DESCRIPTIONS.get(snapshot_name, "Unknown snapshot")
