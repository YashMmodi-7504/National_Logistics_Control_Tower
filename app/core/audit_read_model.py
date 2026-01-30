"""
AUDIT READ MODEL

Purpose:
- Expose why data is hidden, scoped to current role
- NEVER expose shipment state, geo info, or corridor
- Only return: shipment_id, reason_code, timestamp

Responsibilities:
- Query audit snapshots by role
- Return minimal denial information
- Safe for UI consumption
"""

from typing import List, Dict, Optional
from app.core.audit_snapshot_store import read_audit_snapshot


def get_hidden_shipments_reasons(role: str) -> List[Dict[str, str]]:
    """
    Get list of shipments hidden from a role with denial reasons.
    
    Args:
        role: User's role (e.g., SENDER_MANAGER, RECEIVER_MANAGER)
    
    Returns:
        List of dictionaries with ONLY:
        - shipment_id: The shipment identifier
        - reason_code: Why access was denied
        - timestamp: When the audit was generated (optional)
    
    NEVER exposes:
        - Shipment state
        - Geo info
        - Corridor
        - Any other sensitive data
    """
    # Read the latest audit snapshot for this role
    audit_data = read_audit_snapshot(role)
    
    if audit_data is None:
        return []
    
    # Extract denials
    denials = audit_data.get("denials", [])
    generated_at = audit_data.get("generated_at")
    
    # Build UI-safe response
    result = []
    for denial in denials:
        shipment_id = denial.get("shipment_id")
        reason_code = denial.get("reason_code")
        
        # Skip malformed entries
        if shipment_id is None or reason_code is None:
            continue
        
        entry = {
            "shipment_id": shipment_id,
            "reason_code": reason_code,
        }
        
        # Add timestamp if available
        if generated_at is not None:
            entry["timestamp"] = str(generated_at)
        
        result.append(entry)
    
    return result


def get_denial_summary(role: str) -> Dict[str, int]:
    """
    Get summary statistics of denials by reason code.
    
    Args:
        role: User's role
    
    Returns:
        Dictionary mapping reason_code -> count
        Example: {"GEO_SCOPE_MISMATCH": 15, "MISSING_GEO_DATA": 3}
    """
    audit_data = read_audit_snapshot(role)
    
    if audit_data is None:
        return {}
    
    denials = audit_data.get("denials", [])
    
    # Count by reason code
    summary: Dict[str, int] = {}
    for denial in denials:
        reason = denial.get("reason_code", "UNKNOWN")
        summary[reason] = summary.get(reason, 0) + 1
    
    return summary


def get_hidden_count(role: str) -> int:
    """
    Get total count of hidden shipments for a role.
    
    Args:
        role: User's role
    
    Returns:
        Total number of shipments hidden from this role
    """
    audit_data = read_audit_snapshot(role)
    
    if audit_data is None:
        return 0
    
    denials = audit_data.get("denials", [])
    return len(denials)


def get_audit_metadata(role: str) -> Optional[Dict[str, any]]:
    """
    Get metadata about the audit snapshot (without sensitive data).
    
    Args:
        role: User's role
    
    Returns:
        Dictionary with metadata:
        - generated_at: Timestamp of audit generation
        - role: The role this audit is for
        - total_denials: Total count of denials
        
        Returns None if no audit exists
    """
    audit_data = read_audit_snapshot(role)
    
    if audit_data is None:
        return None
    
    denials = audit_data.get("denials", [])
    
    return {
        "generated_at": audit_data.get("generated_at"),
        "role": audit_data.get("role"),
        "total_denials": len(denials),
    }
