"""
PHASE 7.1 — GEO POLICY ENGINE

Purpose:
Determine whether a shipment is within a role's geographic scope.

Inputs:
- role_scope: str
- source_state: Optional[str]
- destination_state: Optional[str]
- corridor: Optional[str]
- allowed_regions: Optional[List[str]]

Rules:
- No external calls
- No state mutation
- Deterministic boolean output
- Corridor format: "StateA -> StateB"

Return:
- True if access allowed
- False otherwise
"""

from typing import Optional, List


def is_within_geo_scope(
    role_scope: str,
    source_state: Optional[str] = None,
    destination_state: Optional[str] = None,
    corridor: Optional[str] = None,
    allowed_regions: Optional[List[str]] = None,
) -> bool:
    """
    Determine if a shipment is within a role's geographic scope.
    
    Args:
        role_scope: The access scope (SOURCE_STATE, DESTINATION_STATE, CORRIDOR, GLOBAL)
        source_state: The origin state of the shipment
        destination_state: The destination state of the shipment
        corridor: The corridor in format "StateA -> StateB"
        allowed_regions: List of allowed states or corridors for the role
    
    Returns:
        True if access is allowed, False otherwise
    """
    # GLOBAL scope has access to everything
    if role_scope == "GLOBAL":
        return True
    
    # If no allowed_regions or empty list, deny access
    if allowed_regions is None or len(allowed_regions) == 0:
        return False
    
    # SOURCE_STATE scope: check if source_state is in allowed_regions
    if role_scope == "SOURCE_STATE":
        if source_state is None or not isinstance(source_state, str) or source_state.strip() == "":
            return False
        return source_state in allowed_regions
    
    # DESTINATION_STATE scope: check if destination_state is in allowed_regions
    if role_scope == "DESTINATION_STATE":
        if destination_state is None or not isinstance(destination_state, str) or destination_state.strip() == "":
            return False
        return destination_state in allowed_regions
    
    # CORRIDOR scope: check if corridor is in allowed_regions
    if role_scope == "CORRIDOR":
        if corridor is None or not isinstance(corridor, str) or corridor.strip() == "":
            return False
        return corridor in allowed_regions
    
    # Unknown scope, deny access
    return False
