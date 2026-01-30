"""
Weather Integration Module

Thin wrapper around weather_engine for easier imports.
"""

from app.intelligence.weather_engine import (
    get_weather_risk,
    fetch_current_weather,
    fetch_weather_forecast,
    calculate_rain_risk,
    calculate_storm_risk,
    calculate_temperature_risk,
    calculate_visibility_risk,
    compute_weather_risk_score,
    clear_weather_cache,
)

__all__ = [
    'get_weather_risk',
    'fetch_current_weather',
    'fetch_weather_forecast',
    'calculate_rain_risk',
    'calculate_storm_risk',
    'calculate_temperature_risk',
    'calculate_visibility_risk',
    'compute_weather_risk_score',
    'clear_weather_cache',
]
