"""
Centralized Data Loading for National Logistics Control Tower
Staff+ Mandate: Single source of truth, no duplicate loads

CRITICAL PRINCIPLE:
All data loading goes through this module.
Data is loaded ONCE per render cycle and shared across all tabs.
"""

import streamlit as st
from typing import Dict, List, Any, Optional
from datetime import datetime


class DataLoader:
    """
    Enterprise Data Loader with render-cycle caching.
    
    DESIGN:
    1. Load data ONCE at start of render cycle
    2. Store in session state with version key
    3. All tabs reference the SAME loaded data
    4. No duplicate database/file reads per render
    """
    
    # Version key for cache invalidation
    _RENDER_KEY = "_current_render_data"
    
    @staticmethod
    def get_all_shipments() -> Dict[str, Any]:
        """
        Get all shipments for current render cycle.
        
        CACHED: Returns same data for entire render cycle.
        Only reloads when cache expires or mutation occurs.
        """
        return DataLoader._get_cached_data("all_shipments", DataLoader._load_all_shipments)
    
    @staticmethod
    def get_shipments_by_state(state: str) -> List[Dict]:
        """
        Get shipments filtered by state.
        
        Uses pre-loaded data, no additional DB calls.
        """
        all_data = DataLoader.get_all_shipments()
        return [
            {
                'shipment_id': sid,
                **s
            }
            for sid, s in all_data.items()
            if s.get('current_state') == state
        ]
    
    @staticmethod
    def get_created_shipments() -> List[Dict]:
        return DataLoader.get_shipments_by_state("CREATED")
    
    @staticmethod
    def get_in_transit_shipments() -> List[Dict]:
        return DataLoader.get_shipments_by_state("IN_TRANSIT")
    
    @staticmethod
    def get_delivered_shipments() -> List[Dict]:
        return DataLoader.get_shipments_by_state("DELIVERED")
    
    @staticmethod
    def invalidate():
        """
        Invalidate all cached data (call after mutations).
        
        This forces a reload on next access.
        """
        if DataLoader._RENDER_KEY in st.session_state:
            del st.session_state[DataLoader._RENDER_KEY]
    
    @staticmethod
    def _get_cached_data(key: str, loader_fn) -> Any:
        """Internal: Get data from render cache or load it"""
        if DataLoader._RENDER_KEY not in st.session_state:
            st.session_state[DataLoader._RENDER_KEY] = {}
        
        cache = st.session_state[DataLoader._RENDER_KEY]
        
        if key not in cache:
            cache[key] = loader_fn()
        
        return cache[key]
    
    @staticmethod
    def _load_all_shipments() -> Dict[str, Any]:
        """Internal: Load all shipments from event sourcing system"""
        try:
            from app.core.read_model import get_all_shipments_state
            return get_all_shipments_state()
        except ImportError:
            # Fallback if read model not available
            return {}


# Pre-computed metrics cache (expensive AI computations)
class MetricsCache:
    """
    Cache for expensive metric computations.
    
    AI risk scores, priority calculations, etc. are computed ONCE
    and cached for the render cycle.
    """
    
    _METRICS_KEY = "_computed_metrics"
    
    @staticmethod
    def get_risk_scores() -> Dict[str, int]:
        """Get pre-computed risk scores for all shipments"""
        return MetricsCache._get_or_compute("risk_scores", MetricsCache._compute_all_risks)
    
    @staticmethod
    def get_priority_scores() -> Dict[str, int]:
        """Get pre-computed priority scores"""
        return MetricsCache._get_or_compute("priority_scores", MetricsCache._compute_all_priorities)
    
    @staticmethod
    def get_risk_for_shipment(shipment_id: str) -> int:
        """Get risk score for a specific shipment (from cache)"""
        scores = MetricsCache.get_risk_scores()
        return scores.get(shipment_id, 50)  # Default to medium risk
    
    @staticmethod
    def _get_or_compute(key: str, compute_fn) -> Dict:
        """Internal: Get from cache or compute once"""
        if MetricsCache._METRICS_KEY not in st.session_state:
            st.session_state[MetricsCache._METRICS_KEY] = {}
        
        cache = st.session_state[MetricsCache._METRICS_KEY]
        
        if key not in cache:
            cache[key] = compute_fn()
        
        return cache[key]
    
    @staticmethod
    def _compute_all_risks() -> Dict[str, int]:
        """Compute risk scores for all shipments ONCE"""
        try:
            from app.core.fluctuation_engine import compute_risk_score_realistic
            
            all_shipments = DataLoader.get_all_shipments()
            risk_scores = {}
            
            for sid, s in all_shipments.items():
                # Extract metadata
                history = s.get("history", [])
                if not history:
                    risk_scores[sid] = 50
                    continue
                
                first_event = history[0]
                metadata = first_event.get("metadata", {})
                
                # Extract fields for risk calculation
                source = metadata.get("source", "")
                destination = metadata.get("destination", "")
                source_state = source.split(",")[-1].strip() if "," in source else source
                dest_state = destination.split(",")[-1].strip() if "," in destination else destination
                delivery_type = metadata.get("delivery_type", "NORMAL")
                weight = metadata.get("parcel_weight_kg", 5.0)
                
                # Calculate age
                age_hours = 0.0
                timestamp = first_event.get("timestamp")
                if timestamp:
                    try:
                        if isinstance(timestamp, str):
                            created = datetime.fromisoformat(timestamp.replace('Z', ''))
                            age_hours = (datetime.now() - created).total_seconds() / 3600
                    except:
                        pass
                
                risk = compute_risk_score_realistic(
                    shipment_id=sid,
                    base_risk=40,
                    delivery_type=delivery_type,
                    weight_kg=float(weight) if weight else 5.0,
                    source_state=source_state,
                    dest_state=dest_state,
                    age_hours=age_hours
                )
                risk_scores[sid] = risk
            
            return risk_scores
        except ImportError:
            return {}
    
    @staticmethod
    def _compute_all_priorities() -> Dict[str, int]:
        """Compute priority scores for all shipments ONCE"""
        try:
            from app.core.fluctuation_engine import compute_priority_score_realistic
            
            all_shipments = DataLoader.get_all_shipments()
            risk_scores = MetricsCache.get_risk_scores()
            priority_scores = {}
            
            for sid, s in all_shipments.items():
                history = s.get("history", [])
                if not history:
                    priority_scores[sid] = 50
                    continue
                
                first_event = history[0]
                metadata = first_event.get("metadata", {})
                
                delivery_type = metadata.get("delivery_type", "NORMAL")
                weight = metadata.get("parcel_weight_kg", 5.0)
                risk = risk_scores.get(sid, 50)
                
                # Calculate age
                age_hours = 0.0
                timestamp = first_event.get("timestamp")
                if timestamp:
                    try:
                        if isinstance(timestamp, str):
                            created = datetime.fromisoformat(timestamp.replace('Z', ''))
                            age_hours = (datetime.now() - created).total_seconds() / 3600
                    except:
                        pass
                
                priority = compute_priority_score_realistic(
                    shipment_id=sid,
                    risk_score=risk,
                    delivery_type=delivery_type,
                    age_hours=age_hours,
                    weight_kg=float(weight) if weight else 5.0
                )
                priority_scores[sid] = priority
            
            return priority_scores
        except ImportError:
            return {}
    
    @staticmethod
    def invalidate():
        """Clear metrics cache (call after data changes)"""
        if MetricsCache._METRICS_KEY in st.session_state:
            del st.session_state[MetricsCache._METRICS_KEY]
