"""
FORENSIC REPLAY ENGINE

Purpose:
- Replay snapshot state at any point in time
- Snapshot-driven only (no live event store)
- Deterministic reconstruction

Requirements:
- Snapshot-driven only
- No live event store reads
- Deterministic reconstruction
- Temporal queries
"""

from typing import Dict, Any, Optional, List
from app.core.snapshot_store import read_snapshot
from app.security.tamper_detector import detect_snapshot_tampering, assert_snapshot_integrity
import os
import json


class ReplayError(Exception):
    """Raised when replay fails."""
    pass


def replay_snapshot_state(
    snapshot_name: str,
    at_timestamp: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Replay the state of a snapshot at a specific time.
    
    Args:
        snapshot_name: Name of the snapshot to replay
        at_timestamp: Optional timestamp to replay at (None = latest)
    
    Returns:
        Dictionary with:
        - snapshot_name: str
        - timestamp: float (actual timestamp of snapshot)
        - content: dict (snapshot content)
        - metadata: dict (verification info)
        - integrity_status: str
    
    Raises:
        ReplayError: If replay fails
    
    Rules:
        - Snapshot-driven only
        - Verify integrity before replay
        - Return deterministic state
    """
    # Verify integrity first
    try:
        integrity_result = detect_snapshot_tampering(snapshot_name)
        
        if integrity_result["status"] != "INTACT":
            raise ReplayError(
                f"Cannot replay tampered snapshot: {snapshot_name}"
            )
    except Exception as e:
        raise ReplayError(f"Integrity check failed: {str(e)}")
    
    # Read snapshot
    snapshot = read_snapshot(snapshot_name)
    
    if snapshot is None:
        raise ReplayError(f"Snapshot not found: {snapshot_name}")
    
    # Get snapshot timestamp
    snapshot_timestamp = snapshot.get("generated_at")
    
    # Check if requested timestamp is valid
    if at_timestamp is not None:
        if snapshot_timestamp is None:
            raise ReplayError("Snapshot has no timestamp")
        
        if at_timestamp < snapshot_timestamp:
            raise ReplayError(
                f"Requested timestamp {at_timestamp} is before snapshot "
                f"timestamp {snapshot_timestamp}"
            )
    
    # Read metadata
    metadata = _read_metadata(snapshot_name)
    
    return {
        "snapshot_name": snapshot_name,
        "timestamp": snapshot_timestamp,
        "content": snapshot,
        "metadata": metadata,
        "integrity_status": integrity_result["status"],
        "replay_timestamp": at_timestamp,
    }


def replay_snapshot_history(snapshot_name: str) -> List[Dict[str, Any]]:
    """
    Replay the full history of a snapshot (all versions).
    
    Args:
        snapshot_name: Name of the snapshot
    
    Returns:
        List of historical states (ordered oldest to newest)
    
    Note:
        In current implementation, only latest version is stored.
        This function is designed for future versioning support.
    """
    # For now, return just the latest state
    try:
        latest = replay_snapshot_state(snapshot_name)
        return [latest]
    except ReplayError:
        return []


def get_snapshot_at_time(
    snapshot_names: List[str],
    at_timestamp: float,
) -> Dict[str, Dict[str, Any]]:
    """
    Get all snapshots as they were at a specific time.
    
    Args:
        snapshot_names: List of snapshot names
        at_timestamp: Timestamp to query
    
    Returns:
        Dictionary mapping snapshot_name -> state
    """
    results = {}
    
    for snapshot_name in snapshot_names:
        try:
            state = replay_snapshot_state(snapshot_name, at_timestamp)
            results[snapshot_name] = state
        except ReplayError:
            # Snapshot didn't exist or was invalid at that time
            results[snapshot_name] = None
    
    return results


def verify_replay_integrity(replay_result: Dict[str, Any]) -> bool:
    """
    Verify the integrity of a replay result.
    
    Args:
        replay_result: Result from replay_snapshot_state
    
    Returns:
        True if integrity is verified, False otherwise
    """
    if not replay_result:
        return False
    
    integrity_status = replay_result.get("integrity_status")
    return integrity_status == "INTACT"


def get_replay_metadata(replay_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract metadata from replay result.
    
    Args:
        replay_result: Result from replay_snapshot_state
    
    Returns:
        Metadata dictionary
    """
    return {
        "snapshot_name": replay_result.get("snapshot_name"),
        "timestamp": replay_result.get("timestamp"),
        "integrity_status": replay_result.get("integrity_status"),
        "replay_timestamp": replay_result.get("replay_timestamp"),
        "has_metadata": replay_result.get("metadata") is not None,
    }


# ==================================================
# INTERNAL HELPERS
# ==================================================

def _read_metadata(snapshot_name: str) -> Optional[Dict[str, Any]]:
    """Read metadata for a snapshot."""
    metadata_dir = os.path.join("data", "snapshots", "metadata")
    metadata_path = os.path.join(metadata_dir, f"{snapshot_name}_meta.json")
    
    if not os.path.exists(metadata_path):
        return None
    
    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None
