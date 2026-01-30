"""
HASH CHAIN (TEMPORAL INTEGRITY)

Purpose:
- Build tamper-evident chain of snapshots
- Link each snapshot to previous via hash
- Enable temporal integrity verification

Requirements:
- Each snapshot references previous hash
- First snapshot = GENESIS
- Chain must be verifiable end-to-end
- Immutable once written
"""

from typing import Dict, Any, List, Optional
import time


# Genesis hash for first entry
GENESIS_HASH = "0" * 64


class ChainEntry:
    """
    Represents a single entry in the hash chain.
    
    Attributes:
        snapshot_name: Name of the snapshot
        snapshot_hash: Hash of the snapshot content
        prev_hash: Hash of previous entry
        timestamp: Creation timestamp
        sequence: Sequence number in chain
    """
    
    def __init__(
        self,
        snapshot_name: str,
        snapshot_hash: str,
        prev_hash: str,
        timestamp: Optional[float] = None,
        sequence: Optional[int] = None,
    ):
        self.snapshot_name = snapshot_name
        self.snapshot_hash = snapshot_hash
        self.prev_hash = prev_hash
        self.timestamp = timestamp or time.time()
        self.sequence = sequence or 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "snapshot_name": self.snapshot_name,
            "snapshot_hash": self.snapshot_hash,
            "prev_hash": self.prev_hash,
            "timestamp": self.timestamp,
            "sequence": self.sequence,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChainEntry':
        """Create from dictionary."""
        return cls(
            snapshot_name=data["snapshot_name"],
            snapshot_hash=data["snapshot_hash"],
            prev_hash=data["prev_hash"],
            timestamp=data.get("timestamp"),
            sequence=data.get("sequence", 0),
        )


def build_chain_entry(
    snapshot_name: str,
    snapshot_hash: str,
    prev_hash: str,
    sequence: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Build a new chain entry.
    
    Args:
        snapshot_name: Name of the snapshot
        snapshot_hash: Hash of the snapshot content
        prev_hash: Hash of previous entry (or GENESIS_HASH for first)
        sequence: Optional sequence number
    
    Returns:
        Chain entry dictionary
    
    Rules:
        - First entry must use GENESIS_HASH as prev_hash
        - Each entry must reference previous
        - Timestamps are auto-generated
    """
    if not snapshot_name or not isinstance(snapshot_name, str):
        raise ValueError("Invalid snapshot_name")
    
    if not snapshot_hash or len(snapshot_hash) != 64:
        raise ValueError("Invalid snapshot_hash (must be 64 chars)")
    
    if not prev_hash or len(prev_hash) != 64:
        raise ValueError("Invalid prev_hash (must be 64 chars)")
    
    entry = ChainEntry(
        snapshot_name=snapshot_name,
        snapshot_hash=snapshot_hash,
        prev_hash=prev_hash,
        sequence=sequence,
    )
    
    return entry.to_dict()


def verify_chain(chain: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Verify the integrity of a hash chain.
    
    Args:
        chain: List of chain entries (ordered)
    
    Returns:
        Verification result dictionary:
        - valid: bool
        - length: int
        - broken_at: int or None (index where chain breaks)
        - error: str or None
    
    Rules:
        - First entry must reference GENESIS_HASH
        - Each entry must reference previous entry's hash
        - Sequence numbers must be consecutive
    """
    if not chain or not isinstance(chain, list):
        return {
            "valid": False,
            "length": 0,
            "broken_at": None,
            "error": "Chain is empty or invalid",
        }
    
    # Verify first entry
    first_entry = chain[0]
    if first_entry.get("prev_hash") != GENESIS_HASH:
        return {
            "valid": False,
            "length": len(chain),
            "broken_at": 0,
            "error": f"First entry must reference GENESIS_HASH, got {first_entry.get('prev_hash')}",
        }
    
    # Verify chain links
    for i in range(1, len(chain)):
        current = chain[i]
        previous = chain[i - 1]
        
        # Check if current entry references previous hash
        expected_prev_hash = previous.get("snapshot_hash")
        actual_prev_hash = current.get("prev_hash")
        
        if expected_prev_hash != actual_prev_hash:
            return {
                "valid": False,
                "length": len(chain),
                "broken_at": i,
                "error": f"Chain break at index {i}: expected prev_hash {expected_prev_hash}, got {actual_prev_hash}",
            }
        
        # Check sequence numbers if present
        if "sequence" in current and "sequence" in previous:
            if current["sequence"] != previous["sequence"] + 1:
                return {
                    "valid": False,
                    "length": len(chain),
                    "broken_at": i,
                    "error": f"Sequence break at index {i}",
                }
    
    return {
        "valid": True,
        "length": len(chain),
        "broken_at": None,
        "error": None,
    }


def get_chain_head(chain: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Get the most recent (head) entry in the chain.
    
    Args:
        chain: List of chain entries
    
    Returns:
        Head entry or None if chain is empty
    """
    if not chain:
        return None
    
    return chain[-1]


def get_genesis_entry() -> Dict[str, Any]:
    """
    Create a genesis chain entry (for initialization).
    
    Returns:
        Genesis entry dictionary
    """
    return build_chain_entry(
        snapshot_name="GENESIS",
        snapshot_hash=GENESIS_HASH,
        prev_hash=GENESIS_HASH,
        sequence=0,
    )


def append_to_chain(
    chain: List[Dict[str, Any]],
    snapshot_name: str,
    snapshot_hash: str,
) -> Dict[str, Any]:
    """
    Append a new entry to the chain.
    
    Args:
        chain: Existing chain
        snapshot_name: Name of new snapshot
        snapshot_hash: Hash of new snapshot
    
    Returns:
        New chain entry
    
    Raises:
        ValueError: If chain is invalid
    """
    # Get previous hash
    if not chain:
        prev_hash = GENESIS_HASH
        sequence = 0
    else:
        head = get_chain_head(chain)
        prev_hash = head["snapshot_hash"]
        sequence = head.get("sequence", 0) + 1
    
    # Build new entry
    new_entry = build_chain_entry(
        snapshot_name=snapshot_name,
        snapshot_hash=snapshot_hash,
        prev_hash=prev_hash,
        sequence=sequence,
    )
    
    return new_entry


def find_entry_by_hash(
    chain: List[Dict[str, Any]],
    snapshot_hash: str,
) -> Optional[Dict[str, Any]]:
    """
    Find a chain entry by snapshot hash.
    
    Args:
        chain: Chain to search
        snapshot_hash: Hash to find
    
    Returns:
        Entry or None if not found
    """
    for entry in chain:
        if entry.get("snapshot_hash") == snapshot_hash:
            return entry
    return None


def get_chain_proof(
    chain: List[Dict[str, Any]],
    snapshot_hash: str,
) -> Optional[List[Dict[str, Any]]]:
    """
    Get proof path from genesis to a specific snapshot.
    
    Args:
        chain: Full chain
        snapshot_hash: Target snapshot hash
    
    Returns:
        List of entries from genesis to target, or None if not found
    """
    target_index = None
    
    for i, entry in enumerate(chain):
        if entry.get("snapshot_hash") == snapshot_hash:
            target_index = i
            break
    
    if target_index is None:
        return None
    
    return chain[:target_index + 1]
