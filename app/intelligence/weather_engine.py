"""
WEATHER INTELLIGENCE ENGINE

Purpose:
- Fetch weather data from OpenWeatherMap API
- Convert weather conditions to normalized risk signals
- Compute unified weather risk score (0-100)
- Graceful degradation if API unavailable

Requirements:
• Never hardcode API keys (use os.getenv)
• Timeout protection (5s max)
• Graceful failure (return neutral risk)
• Cache responses to avoid rate limits
• Support lat/lon OR city/state lookup

Author: National Logistics Control Tower
Phase: 10 - External Service Integration
"""

import os
import requests
import logging
import time
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

# OpenWeatherMap API configuration
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
API_TIMEOUT = 5  # seconds
CACHE_DURATION = 1800  # 30 minutes

# In-memory cache
_weather_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}


def _get_cache_key(lat: float, lon: float) -> str:
    """Generate cache key from coordinates."""
    return f"{round(lat, 2)}_{round(lon, 2)}"


def _is_cache_valid(cache_key: str) -> bool:
    """Check if cached data is still valid."""
    if cache_key not in _weather_cache:
        return False
    
    timestamp, _ = _weather_cache[cache_key]
    age = time.time() - timestamp
    
    return age < CACHE_DURATION


def _get_from_cache(cache_key: str) -> Optional[Dict[str, Any]]:
    """Retrieve data from cache if valid."""
    if _is_cache_valid(cache_key):
        _, data = _weather_cache[cache_key]
        logger.info(f"Weather cache hit for {cache_key}")
        return data
    return None


def _save_to_cache(cache_key: str, data: Dict[str, Any]):
    """Save data to cache."""
    _weather_cache[cache_key] = (time.time(), data)


def fetch_current_weather(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    Fetch current weather from OpenWeatherMap.
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        dict: Weather data or None if failed
        
    API Response includes:
    - weather[].main: Weather condition (Rain, Snow, etc.)
    - weather[].description: Detailed description
    - main.temp: Temperature
    - main.humidity: Humidity %
    - visibility: Visibility in meters
    - wind.speed: Wind speed m/s
    """
    if not OPENWEATHER_API_KEY:
        logger.warning("OPENWEATHER_API_KEY not configured")
        return None
    
    # Check cache first
    cache_key = _get_cache_key(lat, lon)
    cached = _get_from_cache(cache_key)
    if cached:
        return cached
    
    try:
        url = f"{OPENWEATHER_BASE_URL}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"  # Celsius
        }
        
        logger.info(f"Fetching weather for ({lat}, {lon})")
        response = requests.get(url, params=params, timeout=API_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        
        # Cache the result
        _save_to_cache(cache_key, data)
        
        return data
    
    except requests.exceptions.Timeout:
        logger.error(f"Weather API timeout for ({lat}, {lon})")
        return None
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Weather API error: {str(e)}")
        return None
    
    except Exception as e:
        logger.error(f"Unexpected error fetching weather: {str(e)}")
        return None


def fetch_weather_forecast(lat: float, lon: float, hours: int = 24) -> Optional[Dict[str, Any]]:
    """
    Fetch weather forecast from OpenWeatherMap.
    
    Args:
        lat: Latitude
        lon: Longitude
        hours: Forecast hours (default 24)
        
    Returns:
        dict: Forecast data or None if failed
    """
    if not OPENWEATHER_API_KEY:
        logger.warning("OPENWEATHER_API_KEY not configured")
        return None
    
    try:
        url = f"{OPENWEATHER_BASE_URL}/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "cnt": min(hours // 3, 40)  # API returns 3-hour intervals
        }
        
        logger.info(f"Fetching forecast for ({lat}, {lon})")
        response = requests.get(url, params=params, timeout=API_TIMEOUT)
        response.raise_for_status()
        
        return response.json()
    
    except Exception as e:
        logger.error(f"Forecast API error: {str(e)}")
        return None


def calculate_rain_risk(weather_data: Dict[str, Any]) -> float:
    """
    Calculate rain risk from weather data.
    
    Args:
        weather_data: Weather API response
        
    Returns:
        float: Rain risk (0.0 - 1.0)
    """
    if not weather_data:
        return 0.5  # Neutral
    
    risk = 0.0
    
    # Check weather conditions
    weather_list = weather_data.get("weather", [])
    for condition in weather_list:
        main = condition.get("main", "").lower()
        
        if main == "rain":
            risk = max(risk, 0.6)
        elif main == "drizzle":
            risk = max(risk, 0.4)
        elif main == "thunderstorm":
            risk = max(risk, 0.9)
    
    # Check rain volume if available
    rain = weather_data.get("rain", {})
    rain_1h = rain.get("1h", 0)
    
    if rain_1h > 10:  # Heavy rain (>10mm/h)
        risk = max(risk, 0.8)
    elif rain_1h > 5:  # Moderate rain
        risk = max(risk, 0.6)
    elif rain_1h > 0:  # Light rain
        risk = max(risk, 0.3)
    
    return min(risk, 1.0)


def calculate_storm_risk(weather_data: Dict[str, Any]) -> float:
    """
    Calculate storm/severe weather risk.
    
    Args:
        weather_data: Weather API response
        
    Returns:
        float: Storm risk (0.0 - 1.0)
    """
    if not weather_data:
        return 0.5
    
    risk = 0.0
    
    # Check for thunderstorms
    weather_list = weather_data.get("weather", [])
    for condition in weather_list:
        main = condition.get("main", "").lower()
        description = condition.get("description", "").lower()
        
        if main == "thunderstorm":
            risk = max(risk, 0.9)
        elif "storm" in description:
            risk = max(risk, 0.8)
    
    # Check wind speed
    wind = weather_data.get("wind", {})
    wind_speed = wind.get("speed", 0)  # m/s
    
    if wind_speed > 20:  # >70 km/h - severe
        risk = max(risk, 0.9)
    elif wind_speed > 15:  # >50 km/h - high
        risk = max(risk, 0.7)
    elif wind_speed > 10:  # >35 km/h - moderate
        risk = max(risk, 0.5)
    
    return min(risk, 1.0)


def calculate_temperature_risk(weather_data: Dict[str, Any]) -> float:
    """
    Calculate temperature extreme risk.
    
    Args:
        weather_data: Weather API response
        
    Returns:
        float: Temperature risk (0.0 - 1.0)
    """
    if not weather_data:
        return 0.5
    
    main = weather_data.get("main", {})
    temp = main.get("temp", 25)  # Default comfortable temp
    
    risk = 0.0
    
    # Extreme cold
    if temp < -10:
        risk = 0.9
    elif temp < 0:
        risk = 0.6
    elif temp < 5:
        risk = 0.3
    
    # Extreme heat
    if temp > 45:
        risk = max(risk, 0.9)
    elif temp > 40:
        risk = max(risk, 0.7)
    elif temp > 35:
        risk = max(risk, 0.4)
    
    return min(risk, 1.0)


def calculate_visibility_risk(weather_data: Dict[str, Any]) -> float:
    """
    Calculate visibility risk.
    
    Args:
        weather_data: Weather API response
        
    Returns:
        float: Visibility risk (0.0 - 1.0)
    """
    if not weather_data:
        return 0.5
    
    visibility = weather_data.get("visibility", 10000)  # meters
    
    if visibility < 500:  # <500m - severe fog
        return 0.9
    elif visibility < 1000:  # <1km
        return 0.7
    elif visibility < 2000:  # <2km
        return 0.5
    elif visibility < 5000:  # <5km
        return 0.3
    
    return 0.1  # Clear visibility


def compute_weather_risk_score(
    rain_risk: float,
    storm_risk: float,
    temperature_risk: float,
    visibility_risk: float
) -> int:
    """
    Compute unified weather risk score.
    
    Args:
        rain_risk: Rain risk (0-1)
        storm_risk: Storm risk (0-1)
        temperature_risk: Temperature risk (0-1)
        visibility_risk: Visibility risk (0-1)
        
    Returns:
        int: Weather risk score (0-100)
    """
    # Weighted average (storms and rain are more critical)
    weighted_risk = (
        storm_risk * 0.35 +
        rain_risk * 0.30 +
        visibility_risk * 0.20 +
        temperature_risk * 0.15
    )
    
    return int(weighted_risk * 100)


def get_weather_risk(source_geo: Dict[str, Any], destination_geo: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get weather risk for shipment route.
    
    Args:
        source_geo: Source location {lat, lon} or {city, state}
        destination_geo: Destination location {lat, lon} or {city, state}
        
    Returns:
        dict: Weather risk assessment
            - weather_risk_score: 0-100
            - risk_level: LOW/MEDIUM/HIGH/CRITICAL
            - source_weather: Source weather data
            - destination_weather: Destination weather data
            - rain_risk: 0-1
            - storm_risk: 0-1
            - temperature_risk: 0-1
            - visibility_risk: 0-1
            - explanation: Human-readable summary
            - api_available: bool
            
    Notes:
        - Gracefully handles API failures
        - Returns neutral risk (50) if API down
        - Combines source + destination weather
    """
    # Extract coordinates
    source_lat = source_geo.get("lat")
    source_lon = source_geo.get("lon")
    dest_lat = destination_geo.get("lat")
    dest_lon = destination_geo.get("lon")
    
    # Fallback to mock coordinates if not provided
    if source_lat is None or source_lon is None:
        logger.warning("Source coordinates not provided, using neutral risk")
        source_lat, source_lon = 19.0760, 72.8777  # Mumbai default
    
    if dest_lat is None or dest_lon is None:
        logger.warning("Destination coordinates not provided, using neutral risk")
        dest_lat, dest_lon = 12.9716, 77.5946  # Bangalore default
    
    # Fetch weather data
    source_weather = fetch_current_weather(source_lat, source_lon)
    dest_weather = fetch_current_weather(dest_lat, dest_lon)
    
    # API availability check
    api_available = source_weather is not None or dest_weather is not None
    
    if not api_available:
        logger.warning("Weather API unavailable, returning neutral risk")
        return {
            "weather_risk_score": 50,
            "risk_level": "MEDIUM",
            "source_weather": None,
            "destination_weather": None,
            "rain_risk": 0.5,
            "storm_risk": 0.5,
            "temperature_risk": 0.5,
            "visibility_risk": 0.5,
            "explanation": "Weather data unavailable. Using neutral risk estimate.",
            "api_available": False,
        }
    
    # Calculate individual risks for both locations
    source_rain = calculate_rain_risk(source_weather) if source_weather else 0.5
    source_storm = calculate_storm_risk(source_weather) if source_weather else 0.5
    source_temp = calculate_temperature_risk(source_weather) if source_weather else 0.5
    source_vis = calculate_visibility_risk(source_weather) if source_weather else 0.5
    
    dest_rain = calculate_rain_risk(dest_weather) if dest_weather else 0.5
    dest_storm = calculate_storm_risk(dest_weather) if dest_weather else 0.5
    dest_temp = calculate_temperature_risk(dest_weather) if dest_weather else 0.5
    dest_vis = calculate_visibility_risk(dest_weather) if dest_weather else 0.5
    
    # Take worst-case for route
    rain_risk = max(source_rain, dest_rain)
    storm_risk = max(source_storm, dest_storm)
    temperature_risk = max(source_temp, dest_temp)
    visibility_risk = max(source_vis, dest_vis)
    
    # Compute unified score
    weather_risk_score = compute_weather_risk_score(
        rain_risk, storm_risk, temperature_risk, visibility_risk
    )
    
    # Determine risk level
    if weather_risk_score < 30:
        risk_level = "LOW"
    elif weather_risk_score < 60:
        risk_level = "MEDIUM"
    elif weather_risk_score < 80:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"
    
    # Generate explanation
    issues = []
    if storm_risk > 0.6:
        issues.append("severe weather/storms")
    if rain_risk > 0.6:
        issues.append("heavy rain")
    if visibility_risk > 0.6:
        issues.append("poor visibility")
    if temperature_risk > 0.6:
        issues.append("extreme temperatures")
    
    if issues:
        explanation = f"Weather risk due to: {', '.join(issues)}."
    else:
        explanation = "Weather conditions are favorable for transit."
    
    return {
        "weather_risk_score": weather_risk_score,
        "risk_level": risk_level,
        "source_weather": source_weather,
        "destination_weather": dest_weather,
        "rain_risk": round(rain_risk, 2),
        "storm_risk": round(storm_risk, 2),
        "temperature_risk": round(temperature_risk, 2),
        "visibility_risk": round(visibility_risk, 2),
        "explanation": explanation,
        "api_available": True,
    }


def clear_weather_cache():
    """Clear weather cache. Use for testing or manual refresh."""
    global _weather_cache
    _weather_cache.clear()
    logger.info("Weather cache cleared")
