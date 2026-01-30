"""
AUDIT SNAPSHOT STORE

Purpose:
- Track access denials for audit and debugging
- Store denial reasons without exposing shipment data
- Write atomic audit snapshots

Rules:
- Never store full shipment payload
- Only store shipment_id and reason_code
- Thread-safe writes
- No side effects on reads

Audit Snapshot Format:
{
  "generated_at": 1712345678,
  "role": "SENDER_MANAGER",
  "denials": [
    {
      "shipment_id": "SHP-88921",
      "reason_code": "OUT_OF_REGION"
    }
  ]
}
"""

import json
import os
import threading
import time
from typing import Dict, Any, List, Optional

# ==================================================
# STORAGE CONFIG
# ==================================================

_AUDIT_DIR = os.path.join("data", "snapshots", "audit")
os.makedirs(_AUDIT_DIR, exist_ok=True)

_LOCK = threading.Lock()


# ==================================================
# INTERNAL HELPERS
# ==================================================

def _audit_path(role: str, timestamp: int) -> str:
    """Generate audit snapshot filename."""
    return os.path.join(_AUDIT_DIR, f"audit_{role}_{timestamp}.json")


def _latest_audit_path(role: str) -> str:
    """Generate path for latest audit snapshot."""
    return os.path.join(_AUDIT_DIR, f"audit_{role}_latest.json")


# ==================================================
# WRITE AUDIT SNAPSHOT
# ==================================================

def write_audit_snapshot(
    role: str,
    denials: List[Dict[str, str]],
    generated_at: Optional[int] = None,
) -> None:
    """
    Atomically write an audit snapshot to disk.
    
    Args:
        role: User's role
        denials: List of denial records [{"shipment_id": "...", "reason_code": "..."}]
        generated_at: Optional timestamp (defaults to current time)
    
    Rules:
        - Thread-safe
        - Crash-safe (temp file + replace)
        - Never stores full shipment data
    """
    if generated_at is None:
        generated_at = int(time.time())
    
    # Build audit snapshot structure
    audit_data = {
        "generated_at": generated_at,
        "role": role,
        "denials": denials,
    }
    
    # Write timestamped snapshot
    timestamped_path = _audit_path(role, generated_at)
    tmp_path = f"{timestamped_path}.tmp"
    
    with _LOCK:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(audit_data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, timestamped_path)
        
        # Also write latest snapshot for easy access
        latest_path = _latest_audit_path(role)
        tmp_latest = f"{latest_path}.tmp"
        
        with open(tmp_latest, "w", encoding="utf-8") as f:
            json.dump(audit_data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_latest, latest_path)


# ==================================================
# READ AUDIT SNAPSHOT
# ==================================================

def read_audit_snapshot(role: str, timestamp: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Read an audit snapshot safely.
    
    Args:
        role: User's role
        timestamp: Optional specific timestamp (if None, reads latest)
    
    Returns:
        - Parsed audit data
        - None if snapshot does not exist or is unreadable
    """
    if timestamp is None:
        path = _latest_audit_path(role)
    else:
        path = _audit_path(role, timestamp)
    
    if not os.path.exists(path):
        return None
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Never break on corruption
        return None


# ==================================================
# RECORD DENIAL
# ==================================================

def record_denial(
    role: str,
    shipment_id: str,
    reason_code: str,
) -> None:
    """
    Record a single access denial event.
    
    Args:
        role: User's role
        shipment_id: Shipment identifier (NOT full payload)
        reason_code: Denial reason code from audit_reason_engine
    
    Rules:
        - Appends to existing denials
        - Never stores full shipment data
        - Creates new snapshot if none exists
    """
    # Read existing audit snapshot
    existing = read_audit_snapshot(role)
    
    if existing is None:
        denials = []
    else:
        denials = existing.get("denials", [])
    
    # Append new denial
    denials.append({
        "shipment_id": shipment_id,
        "reason_code": reason_code,
    })
    
    # Write updated snapshot
    write_audit_snapshot(role, denials)


# ==================================================
# GET DENIAL STATS
# ==================================================

def get_denial_stats(role: str) -> Dict[str, int]:
    """
    Get statistics about denials for a role.
    
    Args:
        role: User's role
    
    Returns:
        Dictionary with denial counts by reason_code
    """
    audit_data = read_audit_snapshot(role)
    
    if audit_data is None:
        return {}
    
    denials = audit_data.get("denials", [])
    
    # Count denials by reason code
    stats: Dict[str, int] = {}
    for denial in denials:
        reason = denial.get("reason_code", "UNKNOWN")
        stats[reason] = stats.get(reason, 0) + 1
    
    return stats
