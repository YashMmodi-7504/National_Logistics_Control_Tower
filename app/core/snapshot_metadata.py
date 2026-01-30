"""
SNAPSHOT METADATA (IMMUTABLE)

Purpose:
- Store immutable metadata for snapshots
- Include hash, signature, chain info
- Enable verification without payload

Requirements:
- Immutable once written
- Include all verification data
- Separate from snapshot content
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import time


@dataclass(frozen=True)
class SnapshotMetadata:
    """
    Immutable metadata for a snapshot.
    
    Attributes:
        snapshot_name: Name of the snapshot
        content_hash: SHA-256 hash of content
        signature: HMAC signature of hash
        prev_hash: Previous snapshot hash (chain)
        sequence: Sequence number in chain
        timestamp: Creation timestamp
        size_bytes: Size of snapshot in bytes
    """
    snapshot_name: str
    content_hash: str
    signature: str
    prev_hash: str
    sequence: int
    timestamp: float
    size_bytes: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "snapshot_name": self.snapshot_name,
            "content_hash": self.content_hash,
            "signature": self.signature,
            "prev_hash": self.prev_hash,
            "sequence": self.sequence,
            "timestamp": self.timestamp,
            "size_bytes": self.size_bytes,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SnapshotMetadata':
        """Create from dictionary."""
        return cls(
            snapshot_name=data["snapshot_name"],
            content_hash=data["content_hash"],
            signature=data["signature"],
            prev_hash=data["prev_hash"],
            sequence=data["sequence"],
            timestamp=data["timestamp"],
            size_bytes=data["size_bytes"],
        )


def create_metadata(
    snapshot_name: str,
    content_hash: str,
    signature: str,
    prev_hash: str,
    sequence: int,
    size_bytes: int,
) -> SnapshotMetadata:
    """
    Create immutable snapshot metadata.
    
    Args:
        snapshot_name: Name of the snapshot
        content_hash: SHA-256 hash of content
        signature: HMAC signature
        prev_hash: Previous snapshot hash
        sequence: Sequence number
        size_bytes: Size in bytes
    
    Returns:
        Immutable SnapshotMetadata instance
    """
    return SnapshotMetadata(
        snapshot_name=snapshot_name,
        content_hash=content_hash,
        signature=signature,
        prev_hash=prev_hash,
        sequence=sequence,
        timestamp=time.time(),
        size_bytes=size_bytes,
    )


def verify_metadata_integrity(metadata: SnapshotMetadata) -> bool:
    """
    Verify metadata integrity (basic checks).
    
    Args:
        metadata: Metadata to verify
    
    Returns:
        True if basic integrity checks pass
    """
    if not metadata:
        return False
    
    # Check hash length
    if len(metadata.content_hash) != 64:
        return False
    
    # Check signature length
    if len(metadata.signature) != 64:
        return False
    
    # Check prev_hash length
    if len(metadata.prev_hash) != 64:
        return False
    
    # Check sequence is non-negative
    if metadata.sequence < 0:
        return False
    
    # Check timestamp is reasonable
    if metadata.timestamp <= 0:
        return False
    
    return True
