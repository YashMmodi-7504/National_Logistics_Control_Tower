"""
AUDIT REASON ENGINE

Purpose:
- Determine structured reason for access denial
- NEVER expose shipment payload data
- Return enum-safe denial reasons
- One reason per denial

Rules:
- No side effects
- No logging
- Deterministic output
- Used for audit trails and debugging
"""

from typing import Dict, Any, Optional, List, Literal
from security.roles import ROLE_SCOPE_MAP, SYSTEM, COO, VIEWER
from security.access_guard import can_access_shipment

# ==================================================
# DENIAL REASON CONSTANTS (ENUM-SAFE)
# ==================================================

DENIAL_INVALID_ROLE: Literal["INVALID_ROLE"] = "INVALID_ROLE"
DENIAL_INVALID_SHIPMENT: Literal["INVALID_SHIPMENT"] = "INVALID_SHIPMENT"
DENIAL_MISSING_GEO_DATA: Literal["MISSING_GEO_DATA"] = "MISSING_GEO_DATA"
DENIAL_GEO_SCOPE_MISMATCH: Literal["GEO_SCOPE_MISMATCH"] = "GEO_SCOPE_MISMATCH"
DENIAL_NO_USER_REGIONS: Literal["NO_USER_REGIONS"] = "NO_USER_REGIONS"
DENIAL_UNKNOWN: Literal["UNKNOWN"] = "UNKNOWN"

# All possible denial reasons
ALL_DENIAL_REASONS: list[str] = [
    DENIAL_INVALID_ROLE,
    DENIAL_INVALID_SHIPMENT,
    DENIAL_MISSING_GEO_DATA,
    DENIAL_GEO_SCOPE_MISMATCH,
    DENIAL_NO_USER_REGIONS,
    DENIAL_UNKNOWN,
]


# ==================================================
# AUDIT REASON ENGINE
# ==================================================

def get_denial_reason(
    role: str,
    shipment: Dict[str, Any],
    user_regions: Optional[List[str]] = None,
) -> str:
    """
    Determine the structured reason for access denial.
    
    NEVER exposes shipment payload data - only returns enum-safe reason codes.
    
    Args:
        role: User's role
        shipment: Shipment dictionary (read-model snapshot)
        user_regions: Optional list of allowed regions for the user
    
    Returns:
        Enum-safe denial reason string (one of ALL_DENIAL_REASONS)
    """
    # Validate role input
    if role is None or not isinstance(role, str) or role.strip() == "":
        return DENIAL_INVALID_ROLE
    
    # Validate shipment input
    if shipment is None or not isinstance(shipment, dict):
        return DENIAL_INVALID_SHIPMENT
    
    # Check if role is known (including special roles)
    if role not in ROLE_SCOPE_MAP and role not in [SYSTEM, COO, VIEWER]:
        return DENIAL_INVALID_ROLE
    
    # If access is actually allowed, shouldn't be calling this function
    # But return UNKNOWN if it happens
    if can_access_shipment(role, shipment, user_regions):
        return DENIAL_UNKNOWN
    
    # Special roles (SYSTEM, COO, VIEWER) always have access
    # If we reach here with these roles, something is wrong
    if role in [SYSTEM, COO, VIEWER]:
        return DENIAL_UNKNOWN
    
    # Get role scope for normal roles
    role_scope = ROLE_SCOPE_MAP.get(role)
    
    if role_scope is None:
        return DENIAL_INVALID_ROLE
    
    # Check for missing geo data and scope mismatches based on role scope
    if role_scope == "SOURCE_STATE":
        source_state = shipment.get("source_state")
        
        # Check if source_state is missing or invalid
        if source_state is None or not isinstance(source_state, str) or source_state.strip() == "":
            return DENIAL_MISSING_GEO_DATA
        
        # Check if user_regions is missing or empty
        if user_regions is None or len(user_regions) == 0:
            return DENIAL_NO_USER_REGIONS
        
        # If we have valid data but still denied, it's a geo scope mismatch
        return DENIAL_GEO_SCOPE_MISMATCH
    
    elif role_scope == "DESTINATION_STATE":
        destination_state = shipment.get("destination_state")
        
        # Check if destination_state is missing or invalid
        if destination_state is None or not isinstance(destination_state, str) or destination_state.strip() == "":
            return DENIAL_MISSING_GEO_DATA
        
        # Check if user_regions is missing or empty
        if user_regions is None or len(user_regions) == 0:
            return DENIAL_NO_USER_REGIONS
        
        # If we have valid data but still denied, it's a geo scope mismatch
        return DENIAL_GEO_SCOPE_MISMATCH
    
    elif role_scope == "CORRIDOR":
        corridor = shipment.get("corridor")
        
        # Check if corridor is missing or invalid
        if corridor is None or not isinstance(corridor, str) or corridor.strip() == "":
            return DENIAL_MISSING_GEO_DATA
        
        # Check if user_regions is missing or empty
        if user_regions is None or len(user_regions) == 0:
            return DENIAL_NO_USER_REGIONS
        
        # If we have valid data but still denied, it's a geo scope mismatch
        return DENIAL_GEO_SCOPE_MISMATCH
    
    elif role_scope == "GLOBAL":
        # GLOBAL scope should never be denied
        return DENIAL_UNKNOWN
    
    # Unknown reason
    return DENIAL_UNKNOWN
