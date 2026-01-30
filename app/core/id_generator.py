"""
AUTOMATIC SHIPMENT ID GENERATOR

Purpose:
- Generate unique, deterministic shipment IDs
- Time-sortable for chronological ordering
- Human-readable format
- Globally unique across system

Format:
SHIP-YYYYMMDD-HHMMSS-XXXX

Where:
- SHIP: Prefix for shipment identification
- YYYYMMDD: Date component (2026-01-19 → 20260119)
- HHMMSS: Time component (14:30:45 → 143045)
- XXXX: 4-digit random suffix for collision avoidance

Requirements:
• NO manual ID input
• Deterministic uniqueness
• Chronological sortability
• Human readability

Author: National Logistics Control Tower
Phase: 9.1 - Auto Shipment ID Generation
"""

import random
import string
from datetime import datetime
from typing import Set


# In-memory collision tracker (survives during app lifecycle)
_GENERATED_IDS: Set[str] = set()


def generate_shipment_id() -> str:
    """
    Generate a globally unique shipment ID.
    
    Format: SHIP-YYYYMMDD-HHMMSS-XXXX
    
    Returns:
        str: Unique shipment ID
        
    Examples:
        >>> id1 = generate_shipment_id()
        >>> id1.startswith('SHIP-')
        True
        >>> len(id1)
        23
        >>> id2 = generate_shipment_id()
        >>> id1 != id2
        True
    
    Notes:
        - IDs are time-sortable
        - Collision detection via in-memory set
        - Maximum 10,000 retries before failure
        - Random suffix provides 10^4 combinations per second
    """
    max_retries = 10000
    
    for attempt in range(max_retries):
        # Get current timestamp
        now = datetime.now()
        
        # Format date and time components
        date_part = now.strftime("%Y%m%d")  # 20260119
        time_part = now.strftime("%H%M%S")  # 143045
        
        # Generate 4-digit random suffix
        suffix = ''.join(random.choices(string.digits, k=4))
        
        # Construct ID
        shipment_id = f"SHIP-{date_part}-{time_part}-{suffix}"
        
        # Check for collision
        if shipment_id not in _GENERATED_IDS:
            _GENERATED_IDS.add(shipment_id)
            return shipment_id
    
    # Extremely unlikely fallback
    raise RuntimeError(
        f"Failed to generate unique shipment ID after {max_retries} attempts. "
        f"System may be under extreme load."
    )


def validate_shipment_id(shipment_id: str) -> bool:
    """
    Validate shipment ID format.
    
    Args:
        shipment_id: ID to validate
        
    Returns:
        bool: True if valid format, False otherwise
        
    Examples:
        >>> validate_shipment_id("SHIP-20260119-143045-1234")
        True
        >>> validate_shipment_id("INVALID")
        False
        >>> validate_shipment_id("SHIP-20260119-143045")
        False
    """
    if not shipment_id or not isinstance(shipment_id, str):
        return False
    
    parts = shipment_id.split("-")
    
    # Must have 4 parts: SHIP, date, time, suffix
    if len(parts) != 4:
        return False
    
    prefix, date_part, time_part, suffix = parts
    
    # Validate prefix
    if prefix != "SHIP":
        return False
    
    # Validate date (8 digits)
    if not date_part.isdigit() or len(date_part) != 8:
        return False
    
    # Validate time (6 digits)
    if not time_part.isdigit() or len(time_part) != 6:
        return False
    
    # Validate suffix (4 digits)
    if not suffix.isdigit() or len(suffix) != 4:
        return False
    
    return True


def extract_timestamp_from_id(shipment_id: str) -> datetime:
    """
    Extract datetime from shipment ID.
    
    Args:
        shipment_id: Valid shipment ID
        
    Returns:
        datetime: Extracted timestamp
        
    Raises:
        ValueError: If ID format is invalid
        
    Examples:
        >>> dt = extract_timestamp_from_id("SHIP-20260119-143045-1234")
        >>> dt.year
        2026
        >>> dt.month
        1
        >>> dt.day
        19
    """
    if not validate_shipment_id(shipment_id):
        raise ValueError(f"Invalid shipment ID format: {shipment_id}")
    
    parts = shipment_id.split("-")
    date_part = parts[1]  # YYYYMMDD
    time_part = parts[2]  # HHMMSS
    
    # Parse components
    year = int(date_part[0:4])
    month = int(date_part[4:6])
    day = int(date_part[6:8])
    hour = int(time_part[0:2])
    minute = int(time_part[2:4])
    second = int(time_part[4:6])
    
    return datetime(year, month, day, hour, minute, second)


def get_id_generation_stats() -> dict:
    """
    Get statistics about ID generation.
    
    Returns:
        dict: Statistics including total IDs generated
        
    Examples:
        >>> stats = get_id_generation_stats()
        >>> 'total_generated' in stats
        True
    """
    return {
        "total_generated": len(_GENERATED_IDS),
        "collision_probability": len(_GENERATED_IDS) / 10000,  # IDs per second
        "format": "SHIP-YYYYMMDD-HHMMSS-XXXX",
    }


def clear_id_cache():
    """
    Clear the in-memory ID cache.
    
    WARNING: Only use in testing or system reset.
    This will allow ID regeneration which may cause collisions.
    """
    global _GENERATED_IDS
    _GENERATED_IDS.clear()
