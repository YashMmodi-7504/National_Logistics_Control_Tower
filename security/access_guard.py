"""
PHASE 7.1 — ACCESS GUARD (FINAL AUTH DECISION)

This is the SINGLE ENTRYPOINT for Geo-RBAC decisions.

Inputs:
- role: str
- shipment: Dict (read-model snapshot)
- user_regions: Optional[List[str]]

Rules:
- SYSTEM and COO always allowed
- Viewer is read-only but unrestricted
- Others must match geo_policy
- No mutation of shipment
- No logging
- No side effects

Return:
- bool
"""

from typing import Dict, Any, Optional, List
from security.roles import ROLE_SCOPE_MAP, COO, SYSTEM, VIEWER
from security.geo_policy import is_within_geo_scope


def can_access_shipment(
    role: str,
    shipment: Dict[str, Any],
    user_regions: Optional[List[str]] = None,
) -> bool:
    """
    Single entrypoint for Geo-RBAC authorization decisions.
    
    Args:
        role: The user's role (e.g., SENDER_MANAGER, RECEIVER_MANAGER, COO, etc.)
        shipment: Read-model snapshot containing shipment data
        user_regions: Optional list of allowed regions for the user
    
    Returns:
        True if access is allowed, False otherwise
    """
    # Validate role input: must be non-None, non-empty string
    if role is None or not isinstance(role, str) or role.strip() == "":
        return False
    
    # Validate shipment input: must be non-None dict
    if shipment is None or not isinstance(shipment, dict):
        return False
    
    # SYSTEM and COO always have access (GLOBAL scope)
    if role == SYSTEM or role == COO:
        return True
    
    # VIEWER is read-only but unrestricted
    if role == VIEWER:
        return True
    
    # Unknown role, deny access
    if role not in ROLE_SCOPE_MAP:
        return False
    
    # Get the scope for this role
    role_scope = ROLE_SCOPE_MAP[role]
    
    # GLOBAL scope always allows (redundant safety check)
    if role_scope == "GLOBAL":
        return True
    
    # Unknown scope, deny access
    if role_scope not in ["SOURCE_STATE", "DESTINATION_STATE", "CORRIDOR"]:
        return False
    
    # Extract geographic information from shipment
    source_state = shipment.get("source_state")
    destination_state = shipment.get("destination_state")
    corridor = shipment.get("corridor")
    
    # Check geo policy
    return is_within_geo_scope(
        role_scope=role_scope,
        source_state=source_state,
        destination_state=destination_state,
        corridor=corridor,
        allowed_regions=user_regions,
    )
