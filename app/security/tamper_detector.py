"""
TAMPER DETECTOR

Purpose:
- Detect snapshot tampering
- Verify hash, signature, and chain integrity
- Fail loudly on violations

Requirements:
- Detect hash mismatch
- Detect signature mismatch
- Detect chain breaks
- Fail loudly
- No silent recovery
"""

from typing import Dict, Any, Optional
from app.core.snapshot_store import read_snapshot
from app.security.snapshot_hasher import hash_snapshot, verify_snapshot_hash
from app.security.snapshot_signer import verify_signature
from app.core.snapshot_metadata import SnapshotMetadata
import json
import os


class TamperDetected(Exception):
    """Raised when tampering is detected."""
    pass


# Severity levels
SEVERITY_CRITICAL = "CRITICAL"
SEVERITY_HIGH = "HIGH"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_LOW = "LOW"


def detect_snapshot_tampering(snapshot_name: str) -> Dict[str, Any]:
    """
    Detect tampering in a snapshot.
    
    Args:
        snapshot_name: Name of the snapshot to check
    
    Returns:
        Detection result dictionary:
        - status: "INTACT", "TAMPERED", "MISSING", "ERROR"
        - violated_rules: list of violated rules
        - severity: CRITICAL, HIGH, MEDIUM, LOW
        - details: dict with specific findings
    
    Rules:
        - Hash mismatch = CRITICAL
        - Signature mismatch = CRITICAL
        - Chain break = CRITICAL
        - Missing metadata = HIGH
        - Missing snapshot = HIGH
    """
    result = {
        "status": "INTACT",
        "violated_rules": [],
        "severity": None,
        "details": {},
    }
    
    # Read snapshot
    snapshot = read_snapshot(snapshot_name)
    
    if snapshot is None:
        result["status"] = "MISSING"
        result["violated_rules"].append("snapshot_not_found")
        result["severity"] = SEVERITY_HIGH
        result["details"]["error"] = f"Snapshot {snapshot_name} not found"
        return result
    
    # Read metadata (if exists)
    metadata = _read_snapshot_metadata(snapshot_name)
    
    if metadata is None:
        result["status"] = "ERROR"
        result["violated_rules"].append("metadata_missing")
        result["severity"] = SEVERITY_HIGH
        result["details"]["error"] = "Snapshot metadata not found"
        return result
    
    # Parse metadata
    try:
        meta = SnapshotMetadata.from_dict(metadata)
    except Exception as e:
        result["status"] = "ERROR"
        result["violated_rules"].append("metadata_invalid")
        result["severity"] = SEVERITY_HIGH
        result["details"]["error"] = f"Invalid metadata: {str(e)}"
        return result
    
    # Check hash
    expected_hash = meta.content_hash
    actual_hash = hash_snapshot(snapshot)
    
    if expected_hash != actual_hash:
        result["status"] = "TAMPERED"
        result["violated_rules"].append("hash_mismatch")
        result["severity"] = SEVERITY_CRITICAL
        result["details"]["expected_hash"] = expected_hash
        result["details"]["actual_hash"] = actual_hash
        return result
    
    # Check signature
    signature_valid = verify_signature(expected_hash, meta.signature)
    
    if not signature_valid:
        result["status"] = "TAMPERED"
        result["violated_rules"].append("signature_invalid")
        result["severity"] = SEVERITY_CRITICAL
        result["details"]["signature"] = meta.signature
        return result
    
    # All checks passed
    result["status"] = "INTACT"
    result["severity"] = None
    result["details"]["hash"] = actual_hash
    result["details"]["signature_valid"] = True
    
    return result


def verify_snapshot_chain(snapshot_names: list) -> Dict[str, Any]:
    """
    Verify the hash chain across multiple snapshots.
    
    Args:
        snapshot_names: List of snapshot names in order
    
    Returns:
        Verification result:
        - chain_valid: bool
        - broken_at: str or None (snapshot name where chain breaks)
        - details: dict
    """
    if not snapshot_names:
        return {
            "chain_valid": False,
            "broken_at": None,
            "details": {"error": "No snapshots to verify"},
        }
    
    chain_entries = []
    
    # Load metadata for each snapshot
    for snapshot_name in snapshot_names:
        metadata = _read_snapshot_metadata(snapshot_name)
        
        if metadata is None:
            return {
                "chain_valid": False,
                "broken_at": snapshot_name,
                "details": {"error": f"Missing metadata for {snapshot_name}"},
            }
        
        chain_entries.append(metadata)
    
    # Verify chain links
    for i in range(1, len(chain_entries)):
        current = chain_entries[i]
        previous = chain_entries[i - 1]
        
        expected_prev_hash = previous["content_hash"]
        actual_prev_hash = current["prev_hash"]
        
        if expected_prev_hash != actual_prev_hash:
            return {
                "chain_valid": False,
                "broken_at": current["snapshot_name"],
                "details": {
                    "expected_prev_hash": expected_prev_hash,
                    "actual_prev_hash": actual_prev_hash,
                },
            }
    
    return {
        "chain_valid": True,
        "broken_at": None,
        "details": {"verified_count": len(chain_entries)},
    }


def assert_snapshot_integrity(snapshot_name: str) -> None:
    """
    Assert snapshot integrity, raising exception if tampered.
    
    Args:
        snapshot_name: Name of snapshot to verify
    
    Raises:
        TamperDetected: If tampering is detected
    """
    result = detect_snapshot_tampering(snapshot_name)
    
    if result["status"] == "TAMPERED":
        raise TamperDetected(
            f"Snapshot {snapshot_name} has been tampered with: "
            f"{', '.join(result['violated_rules'])}"
        )
    
    if result["status"] in ["MISSING", "ERROR"]:
        raise TamperDetected(
            f"Cannot verify snapshot {snapshot_name}: {result['status']}"
        )


def get_integrity_status(snapshot_names: list) -> Dict[str, Any]:
    """
    Get overall integrity status for multiple snapshots.
    
    Args:
        snapshot_names: List of snapshot names
    
    Returns:
        Status dictionary:
        - total: int
        - intact: int
        - tampered: int
        - missing: int
        - error: int
        - details: list of individual results
    """
    status = {
        "total": len(snapshot_names),
        "intact": 0,
        "tampered": 0,
        "missing": 0,
        "error": 0,
        "details": [],
    }
    
    for snapshot_name in snapshot_names:
        result = detect_snapshot_tampering(snapshot_name)
        status["details"].append(result)
        
        if result["status"] == "INTACT":
            status["intact"] += 1
        elif result["status"] == "TAMPERED":
            status["tampered"] += 1
        elif result["status"] == "MISSING":
            status["missing"] += 1
        else:
            status["error"] += 1
    
    return status


# ==================================================
# INTERNAL HELPERS
# ==================================================

def _read_snapshot_metadata(snapshot_name: str) -> Optional[Dict[str, Any]]:
    """
    Read metadata for a snapshot.
    
    Args:
        snapshot_name: Name of snapshot
    
    Returns:
        Metadata dict or None if not found
    """
    metadata_dir = os.path.join("data", "snapshots", "metadata")
    metadata_path = os.path.join(metadata_dir, f"{snapshot_name}_meta.json")
    
    if not os.path.exists(metadata_path):
        return None
    
    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None
