"""
SNAPSHOT HASHER

Purpose:
- Generate cryptographic hashes of snapshots
- Ensure tamper-evidence
- Deterministic, reproducible hashing

Requirements:
- Canonical JSON serialization
- Stable ordering
- SHA-256 hashing
- No timestamps inside payload
- Deterministic output
"""

import json
import hashlib
from typing import Any, Dict


def hash_snapshot(snapshot: Dict[str, Any]) -> str:
    """
    Generate a deterministic SHA-256 hash of a snapshot.
    
    Args:
        snapshot: Snapshot dictionary to hash
    
    Returns:
        Hexadecimal hash string (64 characters)
    
    Rules:
        - Canonical JSON serialization (sorted keys)
        - Stable ordering
        - Deterministic output
        - No timestamps in payload (handled externally)
    
    Raises:
        ValueError: If snapshot is None or not serializable
    """
    if snapshot is None:
        raise ValueError("Cannot hash None snapshot")
    
    if not isinstance(snapshot, dict):
        raise ValueError("Snapshot must be a dictionary")
    
    try:
        # Canonical JSON: sorted keys, no whitespace, ASCII
        canonical_json = json.dumps(
            snapshot,
            sort_keys=True,
            ensure_ascii=True,
            separators=(',', ':')
        )
        
        # UTF-8 encode
        encoded = canonical_json.encode('utf-8')
        
        # SHA-256 hash
        hash_object = hashlib.sha256(encoded)
        
        # Return hex digest
        return hash_object.hexdigest()
    
    except (TypeError, ValueError) as e:
        raise ValueError(f"Failed to hash snapshot: {str(e)}")


def verify_snapshot_hash(snapshot: Dict[str, Any], expected_hash: str) -> bool:
    """
    Verify that a snapshot matches its expected hash.
    
    Args:
        snapshot: Snapshot dictionary
        expected_hash: Expected hash value
    
    Returns:
        True if hash matches, False otherwise
    """
    if not expected_hash or not isinstance(expected_hash, str):
        return False
    
    try:
        actual_hash = hash_snapshot(snapshot)
        return actual_hash == expected_hash
    except ValueError:
        return False


def hash_string(data: str) -> str:
    """
    Generate SHA-256 hash of a string.
    
    Args:
        data: String to hash
    
    Returns:
        Hexadecimal hash string
    """
    if not isinstance(data, str):
        raise ValueError("Data must be a string")
    
    encoded = data.encode('utf-8')
    hash_object = hashlib.sha256(encoded)
    return hash_object.hexdigest()


def hash_bytes(data: bytes) -> str:
    """
    Generate SHA-256 hash of bytes.
    
    Args:
        data: Bytes to hash
    
    Returns:
        Hexadecimal hash string
    """
    if not isinstance(data, bytes):
        raise ValueError("Data must be bytes")
    
    hash_object = hashlib.sha256(data)
    return hash_object.hexdigest()
