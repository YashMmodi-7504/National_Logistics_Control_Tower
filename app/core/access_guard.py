"""
ACCESS GUARD WITH DENIAL REASON CODES

Purpose:
- Extend access_guard with structured denial reasons
- Preserve existing boolean behavior
- Never expose shipment data in reasons

Rules:
- No side effects
- No logging
- Deterministic output
"""

from typing import Dict, Any, Optional, List, Tuple
from security.access_guard import can_access_shipment
from app.intelligence.audit_reason_engine import get_denial_reason


def check_access_with_reason(
    role: str,
    shipment: Dict[str, Any],
    user_regions: Optional[List[str]] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Check access and return both the decision and denial reason (if denied).
    
    Args:
        role: User's role
        shipment: Shipment dictionary (read-model snapshot)
        user_regions: Optional list of allowed regions for the user
    
    Returns:
        Tuple of (access_allowed, denial_reason)
        - (True, None) if access is allowed
        - (False, reason_code) if access is denied
    """
    # Check access using the security module
    access_allowed = can_access_shipment(role, shipment, user_regions)
    
    # If access is allowed, no denial reason
    if access_allowed:
        return (True, None)
    
    # If access is denied, get the structured reason
    denial_reason = get_denial_reason(role, shipment, user_regions)
    
    return (False, denial_reason)


def can_access(
    role: str,
    shipment: Dict[str, Any],
    user_regions: Optional[List[str]] = None,
) -> bool:
    """
    Simple boolean access check (preserves existing behavior).
    
    Args:
        role: User's role
        shipment: Shipment dictionary (read-model snapshot)
        user_regions: Optional list of allowed regions for the user
    
    Returns:
        True if access is allowed, False otherwise
    """
    return can_access_shipment(role, shipment, user_regions)
