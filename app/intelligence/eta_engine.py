"""
ETA + ROUTING INTELLIGENCE ENGINE

Purpose:
- Compute ETA using OpenRouteService directions API
- Calculate distance and estimated travel time
- Provide route confidence metric
- Graceful fallback if API unavailable
- Short-term caching to avoid rate limits

Requirements:
• Never hardcode API keys (use os.getenv)
• Timeout protection (10s max)
• Rate limit handling
• Cache responses (1 hour)
• Fallback ETA calculation

Author: National Logistics Control Tower
Phase: 10 - External Service Integration
"""

import os
import requests
import logging
import time
import math
from typing import Dict, Any, Optional, Tuple, List

# Configure logging
logger = logging.getLogger(__name__)

# OpenRouteService configuration
ORS_API_KEY = os.getenv("ORS_API_KEY")
ORS_BASE_URL = "https://api.openrouteservice.org/v2"
API_TIMEOUT = 10  # seconds
CACHE_DURATION = 3600  # 1 hour

# In-memory cache
_eta_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}

# Fallback average speeds (km/h)
FALLBACK_SPEEDS = {
    "highway": 80,
    "national": 60,
    "state": 50,
    "urban": 30,
}


def _get_cache_key(source_lat: float, source_lon: float, dest_lat: float, dest_lon: float) -> str:
    """Generate cache key from coordinates."""
    return f"{round(source_lat, 2)}_{round(source_lon, 2)}_{round(dest_lat, 2)}_{round(dest_lon, 2)}"


def _is_cache_valid(cache_key: str) -> bool:
    """Check if cached data is still valid."""
    if cache_key not in _eta_cache:
        return False
    
    timestamp, _ = _eta_cache[cache_key]
    age = time.time() - timestamp
    
    return age < CACHE_DURATION


def _get_from_cache(cache_key: str) -> Optional[Dict[str, Any]]:
    """Retrieve data from cache if valid."""
    if _is_cache_valid(cache_key):
        _, data = _eta_cache[cache_key]
        logger.info(f"ETA cache hit for {cache_key}")
        return data
    return None


def _save_to_cache(cache_key: str, data: Dict[str, Any]):
    """Save data to cache."""
    _eta_cache[cache_key] = (time.time(), data)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate great-circle distance between two points.
    
    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates
        
    Returns:
        float: Distance in kilometers
    """
    # Earth radius in km
    R = 6371.0
    
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    
    return distance


def fetch_route_from_ors(source_lat: float, source_lon: float, dest_lat: float, dest_lon: float) -> Optional[Dict[str, Any]]:
    """
    Fetch route from OpenRouteService.
    
    Args:
        source_lat, source_lon: Source coordinates
        dest_lat, dest_lon: Destination coordinates
        
    Returns:
        dict: Route data or None if failed
        
    API Response includes:
    - features[0].properties.summary.distance: Distance in meters
    - features[0].properties.summary.duration: Duration in seconds
    - features[0].geometry.coordinates: Route polyline
    """
    if not ORS_API_KEY:
        logger.warning("ORS_API_KEY not configured")
        return None
    
    # Check cache first
    cache_key = _get_cache_key(source_lat, source_lon, dest_lat, dest_lon)
    cached = _get_from_cache(cache_key)
    if cached:
        return cached
    
    try:
        url = f"{ORS_BASE_URL}/directions/driving-car"
        
        headers = {
            "Authorization": ORS_API_KEY,
            "Content-Type": "application/json",
        }
        
        body = {
            "coordinates": [
                [source_lon, source_lat],  # ORS uses [lon, lat] order
                [dest_lon, dest_lat]
            ]
        }
        
        logger.info(f"Fetching route from ({source_lat}, {source_lon}) to ({dest_lat}, {dest_lon})")
        response = requests.post(url, json=body, headers=headers, timeout=API_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        
        # Cache the result
        _save_to_cache(cache_key, data)
        
        return data
    
    except requests.exceptions.Timeout:
        logger.error(f"ORS API timeout")
        return None
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            logger.error("ORS API rate limit exceeded")
        else:
            logger.error(f"ORS API HTTP error: {e.response.status_code}")
        return None
    
    except requests.exceptions.RequestException as e:
        logger.error(f"ORS API error: {str(e)}")
        return None
    
    except Exception as e:
        logger.error(f"Unexpected error fetching route: {str(e)}")
        return None


def calculate_fallback_eta(distance_km: float, avg_speed_kmh: float = 50) -> float:
    """
    Calculate fallback ETA using simple formula.
    
    Args:
        distance_km: Distance in kilometers
        avg_speed_kmh: Average speed in km/h
        
    Returns:
        float: ETA in hours
    """
    return distance_km / avg_speed_kmh


def compute_route_confidence(route_data: Optional[Dict[str, Any]], used_fallback: bool) -> float:
    """
    Compute confidence in route calculation.
    
    Args:
        route_data: ORS route data
        used_fallback: Whether fallback was used
        
    Returns:
        float: Confidence (0.0 - 1.0)
    """
    if used_fallback:
        return 0.5  # Medium confidence for fallback
    
    if route_data is None:
        return 0.3  # Low confidence
    
    # High confidence if we got actual route data
    return 0.9


def compute_eta(source_geo: Dict[str, Any], destination_geo: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute ETA and route information.
    
    Args:
        source_geo: Source location {lat, lon} or {city, state}
        destination_geo: Destination location {lat, lon} or {city, state}
        
    Returns:
        dict: ETA and route data
            - distance_km: Distance in kilometers
            - eta_hours: Estimated travel time in hours
            - route_confidence: Confidence (0-1)
            - api_available: Whether ORS API was available
            - used_fallback: Whether fallback calculation was used
            - route_summary: Human-readable summary
            
    Notes:
        - Gracefully handles API failures
        - Falls back to haversine distance calculation
        - Caches results for 1 hour
    """
    # Extract coordinates
    source_lat = source_geo.get("lat")
    source_lon = source_geo.get("lon")
    dest_lat = destination_geo.get("lat")
    dest_lon = destination_geo.get("lon")
    
    # Fallback to mock coordinates if not provided
    if source_lat is None or source_lon is None:
        logger.warning("Source coordinates not provided, using defaults")
        source_lat, source_lon = 19.0760, 72.8777  # Mumbai
    
    if dest_lat is None or dest_lon is None:
        logger.warning("Destination coordinates not provided, using defaults")
        dest_lat, dest_lon = 12.9716, 77.5946  # Bangalore
    
    # Try ORS API first
    route_data = fetch_route_from_ors(source_lat, source_lon, dest_lat, dest_lon)
    
    if route_data:
        try:
            # Extract distance and duration from ORS response
            features = route_data.get("features", [])
            if features:
                summary = features[0].get("properties", {}).get("summary", {})
                
                distance_meters = summary.get("distance", 0)
                duration_seconds = summary.get("duration", 0)
                
                distance_km = distance_meters / 1000
                eta_hours = duration_seconds / 3600
                
                route_confidence = compute_route_confidence(route_data, False)
                
                route_summary = (
                    f"Route via ORS: {distance_km:.1f} km, "
                    f"ETA {eta_hours:.1f} hours"
                )
                
                logger.info(route_summary)
                
                return {
                    "distance_km": round(distance_km, 2),
                    "eta_hours": round(eta_hours, 2),
                    "route_confidence": route_confidence,
                    "api_available": True,
                    "used_fallback": False,
                    "route_summary": route_summary,
                }
        
        except Exception as e:
            logger.error(f"Error parsing ORS response: {str(e)}")
    
    # Fallback: Use haversine distance
    logger.warning("Using fallback ETA calculation")
    
    distance_km = haversine_distance(source_lat, source_lon, dest_lat, dest_lon)
    
    # Estimate speed based on distance
    if distance_km < 50:
        avg_speed = FALLBACK_SPEEDS["urban"]
    elif distance_km < 200:
        avg_speed = FALLBACK_SPEEDS["state"]
    elif distance_km < 500:
        avg_speed = FALLBACK_SPEEDS["national"]
    else:
        avg_speed = FALLBACK_SPEEDS["highway"]
    
    eta_hours = calculate_fallback_eta(distance_km, avg_speed)
    route_confidence = compute_route_confidence(None, True)
    
    route_summary = (
        f"Fallback estimate: {distance_km:.1f} km (straight-line), "
        f"ETA ~{eta_hours:.1f} hours (avg {avg_speed} km/h)"
    )
    
    logger.info(route_summary)
    
    return {
        "distance_km": round(distance_km, 2),
        "eta_hours": round(eta_hours, 2),
        "route_confidence": route_confidence,
        "api_available": False,
        "used_fallback": True,
        "route_summary": route_summary,
    }


def estimate_sla_feasibility(eta_hours: float, sla_hours: int, buffer_factor: float = 1.2) -> Dict[str, Any]:
    """
    Estimate SLA feasibility based on ETA.
    
    Args:
        eta_hours: Estimated travel time
        sla_hours: SLA deadline in hours
        buffer_factor: Safety buffer multiplier (default 1.2 = 20% buffer)
        
    Returns:
        dict: SLA feasibility assessment
            - is_feasible: Whether SLA can be met
            - buffer_hours: Available buffer time
            - utilization: SLA time utilization (0-1)
            - recommendation: Action recommendation
    """
    buffered_eta = eta_hours * buffer_factor
    is_feasible = buffered_eta <= sla_hours
    buffer_hours = sla_hours - buffered_eta
    utilization = buffered_eta / sla_hours if sla_hours > 0 else 1.0
    
    if not is_feasible:
        recommendation = "SLA likely to be breached. Consider priority handling or customer notification."
    elif utilization > 0.9:
        recommendation = "Tight SLA timeline. Monitor closely and avoid delays."
    elif utilization > 0.7:
        recommendation = "Moderate buffer. Standard handling should suffice."
    else:
        recommendation = "Comfortable buffer. SLA easily achievable."
    
    return {
        "is_feasible": is_feasible,
        "buffer_hours": round(buffer_hours, 2),
        "utilization": round(utilization, 2),
        "recommendation": recommendation,
    }


def get_eta(*, history: List[Dict]) -> float:
    """
    LEGACY: Estimate ETA (in hours) from shipment event history.
    
    NOTE: This is the old implementation kept for backward compatibility.
    Use compute_eta() for new code with full route intelligence.
    """
    if not history:
        return 0.0

    # Simple baseline heuristic
    base = 6
    factor = 1.8

    eta = base + factor * len(history)
    return round(eta, 2)


def clear_eta_cache():
    """Clear ETA cache. Use for testing or manual refresh."""
    global _eta_cache
    _eta_cache.clear()
    logger.info("ETA cache cleared")
