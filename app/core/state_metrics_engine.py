"""
State Metrics Engine - Dynamic, realistic state-level metrics
Generates fluctuating data per state based on shipment mix, characteristics
Daily refresh at 5:00 PM IST for live feel

⚡ ENTERPRISE UPGRADE: Uses fluctuation_engine for bell-curve realistic values
NO hardcoded constants, NO zeros, NO uniform distribution
"""

import random
from datetime import datetime, timedelta
from typing import Dict, Any
from app.core.india_states import INDIA_STATES, STATE_CHARACTERISTICS
from app.core.fluctuation_engine import (
    get_daily_seed,
    compute_state_volume_realistic,
    compute_daily_distributions,
    compute_risk_score_realistic,
    compute_express_probability,
)


def compute_state_metrics(shipments_dict: Dict, state_name: str) -> Dict[str, Any]:
    """
    Compute realistic, fluctuating metrics for a specific state.
    ⚡ ENTERPRISE ENGINE: Bell-curve distributions, NO zeros, NO constants
    
    Returns:
        - total_shipments: 500-25,000 (based on state size)
        - today_created: 8-16% of total
        - today_left: 5-14% of total
        - yesterday_completed: 10-20% of total
        - tomorrow_scheduled: 6-15% of total
        - pending: 20-35% of total
        - delivered: 40-60% of total
        - avg_sla_risk: 20-85 (bell-curved)
        - high_risk_count: 5-18% of total
        - express_ratio: 0.15-0.45 (metro states higher)
    """
    
    # Get state characteristics
    char = STATE_CHARACTERISTICS.get(state_name, {
        "metro": False,
        "volume_multiplier": 0.5,
        "risk_base": 40
    })
    
    # Filter shipments for this state
    state_shipments = {
        sid: s for sid, s in shipments_dict.items()
        if s.get("source_state") == state_name
    }
    
    # ⚡ ALWAYS generate realistic volumes using fluctuation engine
    # NO zeros, even if no real shipments
    realistic_volume = compute_state_volume_realistic(
        state_name=state_name,
        volume_multiplier=char["volume_multiplier"],
        min_volume=500,
        max_volume=25000
    )
    
    # Use real shipment count if higher than realistic baseline
    total = max(len(state_shipments), realistic_volume)
    
    # ⚡ Generate bell-curve distributed daily metrics (NO hardcoded percentages)
    distributions = compute_daily_distributions(
        total_volume=total,
        shipment_id_prefix=state_name
    )
    
    # Calculate risk metrics with REALISTIC variance
    daily_seed = get_daily_seed()
    seed = daily_seed + hash(state_name)
    rng = random.Random(seed)
    
    # Base risk from state characteristics
    base_risk = char["risk_base"]
    
    # Count express shipments with realistic probability
    express_count = 0
    high_risk_count = 0
    total_risk = 0
    
    if len(state_shipments) > 0:
        # Use real shipment data for risk calculations
        for sid, s in state_shipments.items():
            history = s.get("history", [])
            if history:
                first_event = history[0]
                metadata = first_event.get("metadata", {})
                
                # Check if express
                if metadata.get("delivery_type") == "EXPRESS":
                    express_count += 1
                
                # Calculate realistic risk score
                weight = metadata.get("parcel_weight_kg", 5.0)
                delivery_type = metadata.get("delivery_type", "NORMAL")
                dest_state = s.get("destination_state", "Unknown")
                
                # Use enterprise fluctuation engine
                shipment_risk = compute_risk_score_realistic(
                    shipment_id=sid,
                    base_risk=base_risk,
                    delivery_type=delivery_type,
                    weight_kg=weight,
                    source_state=state_name,
                    dest_state=dest_state,
                    age_hours=0
                )
                
                total_risk += shipment_risk
                if shipment_risk >= 70:
                    high_risk_count += 1
        
        avg_sla_risk = int(total_risk / len(state_shipments))
        express_ratio = round(express_count / len(state_shipments), 2)
    else:
        # Generate synthetic risk metrics when no real shipments
        # Use bell-curve variance around base risk
        import math
        
        # Generate varied risk scores for synthetic shipments
        for i in range(min(100, total // 10)):  # Sample 10% for performance
            synthetic_id = f"SYN-{state_name}-{i}"
            
            # Determine if express
            is_express = compute_express_probability(state_name, synthetic_id)
            delivery_type = "EXPRESS" if is_express else "NORMAL"
            
            if is_express:
                express_count += 1
            
            # Generate realistic weight
            rng_weight = random.Random(seed + i)
            weight = rng_weight.uniform(0.5, 80)
            
            # Calculate risk
            risk = compute_risk_score_realistic(
                shipment_id=synthetic_id,
                base_risk=base_risk,
                delivery_type=delivery_type,
                weight_kg=weight,
                source_state=state_name,
                dest_state="Unknown",
                age_hours=0
            )
            
            total_risk += risk
            if risk >= 70:
                high_risk_count += 1
        
        # Scale counts to full volume
        sample_size = min(100, total // 10)
        scale_factor = total / max(sample_size, 1)
        
        avg_sla_risk = int(total_risk / max(sample_size, 1))
        high_risk_count = int(high_risk_count * scale_factor)
        express_count = int(express_count * scale_factor)
        express_ratio = round(express_count / total, 2)
    
    return {
        "total_shipments": total,
        "today_created": distributions["today_created"],
        "today_left": distributions["today_left"],
        "yesterday_completed": distributions["yesterday_completed"],
        "tomorrow_scheduled": distributions["tomorrow_scheduled"],
        "pending": distributions["pending"],
        "delivered": distributions["delivered"],
        "avg_sla_risk": avg_sla_risk,
        "high_risk_count": high_risk_count,
        "express_ratio": express_ratio,
        "express_count": express_count
    }


def compute_all_states_metrics(shipments_dict: Dict) -> Dict[str, Dict[str, Any]]:
    """
    Compute metrics for ALL 36 Indian states and UTs.
    ⚡ ENTERPRISE GUARANTEE: Every state has realistic non-zero data
    """
    all_metrics = {}
    
    for state in INDIA_STATES:
        all_metrics[state] = compute_state_metrics(shipments_dict, state)
    
    return all_metrics
def compute_national_aggregates(all_state_metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate all state metrics to national level.
    """
    return {
        "total_shipments": sum(m["total_shipments"] for m in all_state_metrics.values()),
        "today_created": sum(m["today_created"] for m in all_state_metrics.values()),
        "today_left": sum(m["today_left"] for m in all_state_metrics.values()),
        "yesterday_completed": sum(m["yesterday_completed"] for m in all_state_metrics.values()),
        "tomorrow_scheduled": sum(m["tomorrow_scheduled"] for m in all_state_metrics.values()),
        "pending": sum(m["pending"] for m in all_state_metrics.values()),
        "delivered": sum(m["delivered"] for m in all_state_metrics.values()),
        "high_risk_count": sum(m["high_risk_count"] for m in all_state_metrics.values()),
        "avg_sla_risk": int(sum(m["avg_sla_risk"] * m["total_shipments"] for m in all_state_metrics.values()) / 
                           max(sum(m["total_shipments"] for m in all_state_metrics.values()), 1))
    }
