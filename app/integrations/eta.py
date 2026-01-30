"""
ETA/Routing Integration Module

Thin wrapper around eta_engine for easier imports.
Provides estimate_eta() as an alias for compute_eta().
"""

from app.intelligence.eta_engine import (
    compute_eta,
    estimate_sla_feasibility,
    haversine_distance,
    fetch_route_from_ors,
    clear_eta_cache,
    get_eta,  # legacy function
)

# Alias for user-friendly naming
estimate_eta = compute_eta

__all__ = [
    'estimate_eta',
    'compute_eta',
    'estimate_sla_feasibility',
    'haversine_distance',
    'fetch_route_from_ors',
    'clear_eta_cache',
    'get_eta',
]
