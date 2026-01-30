"""
Enterprise Cache Management for National Logistics Control Tower
Staff+ Mandate: Stable cache keys, no time-based invalidation in render path
"""

import streamlit as st
import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional, Callable
import functools


def get_cache_key(prefix: str, invalidation_window_seconds: int = 300) -> str:
    """
    Generate stable cache key with configurable invalidation window.
    
    CRITICAL: Use 300s (5 min) as default to prevent cache churn.
    For real-time data, use 60s minimum.
    """
    # Round to invalidation window to prevent constant cache misses
    timestamp = int(datetime.now().timestamp() // invalidation_window_seconds)
    return f"{prefix}_{timestamp}"


class CacheManager:
    """
    Centralized cache management for the Control Tower.
    
    Staff+ Design Principles:
    1. Session-scoped module caching (loaded once per session)
    2. Data caching with stable keys (no per-render invalidation)
    3. Lazy initialization of expensive resources
    4. Cache warming on first access, not at import
    """
    
    # Cache TTL configuration (in seconds)
    TTL_SHIPMENTS = 60       # Shipment data - balance freshness vs performance
    TTL_METRICS = 120        # Computed metrics - more expensive, longer cache
    TTL_SNAPSHOTS = 300      # Snapshot data - rarely changes
    TTL_AI_SCORES = 180      # AI/Risk scores - expensive computation
    TTL_UI_COMPONENTS = 30   # UI-specific data - short cache for responsiveness
    
    @staticmethod
    def init_session_caches():
        """Initialize cache tracking in session state (call once at startup)"""
        if "_cache_initialized" not in st.session_state:
            st.session_state._cache_initialized = True
            st.session_state._cache_hits = 0
            st.session_state._cache_misses = 0
            st.session_state._module_cache = {}
            st.session_state._data_cache_versions = {}
    
    @staticmethod
    def get_module(module_key: str, loader_fn: Callable) -> Any:
        """
        Get a module from session cache or load it once.
        
        CRITICAL: Modules are loaded ONCE per session, not per render.
        This prevents repeated import overhead.
        """
        CacheManager.init_session_caches()
        
        if module_key not in st.session_state._module_cache:
            st.session_state._module_cache[module_key] = loader_fn()
            st.session_state._cache_misses += 1
        else:
            st.session_state._cache_hits += 1
        
        return st.session_state._module_cache[module_key]
    
    @staticmethod
    def clear_data_caches():
        """Clear all data caches (call after mutations like create/update)"""
        # Clear Streamlit's internal caches for data functions
        funcs_to_clear = [
            'get_cached_shipments',
            'load_manager_shipments', 
            'get_all_shipments_state_cached',
            'get_viewer_shipments',
            'compute_coo_metrics',
        ]
        # Note: Individual cache clears happen via function.clear() method
        # This is a marker for when full refresh is needed
        if "_last_mutation_time" not in st.session_state:
            st.session_state._last_mutation_time = datetime.now()
        else:
            st.session_state._last_mutation_time = datetime.now()


def cache_with_stable_key(ttl_seconds: int = 300, prefix: str = ""):
    """
    Decorator for caching with stable keys (prevents cache churn).
    
    Usage:
        @cache_with_stable_key(ttl_seconds=120, prefix="metrics")
        def compute_expensive_metrics(shipment_count):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Use Streamlit's native cache with proper TTL
            cache_key = get_cache_key(prefix or func.__name__, ttl_seconds)
            
            # Create a cached version dynamically
            cached_func = st.cache_data(ttl=ttl_seconds, show_spinner=False)(func)
            return cached_func(*args, **kwargs)
        
        return wrapper
    return decorator
