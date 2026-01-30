"""
AI RISK FUSION ENGINE

Purpose:
- Combine multiple risk signals into unified assessment
- Weather risk + Corridor risk + Historical risk + ETA uncertainty
- Weighted hybrid model (average + worst-case boost)
- Override recommendation logic
- Explainable AI outputs

Requirements:
• Combine external intelligence (weather, ETA)
• Historical corridor analysis
• SLA feasibility assessment
• Clear override recommendations
• Detailed explanations

Author: National Logistics Control Tower
Phase: 10 - External Service Integration
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


def _parse_timestamp(ts) -> datetime:
    """
    Parse timestamp, handling both ISO string and Unix timestamp formats.
    Converts all to UTC timezone-aware for consistent comparison.
    """
    # If already a float/int (Unix timestamp), convert directly
    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    
    # Handle string timestamps
    if not isinstance(ts, str):
        ts = str(ts)
    
    # Remove 'Z' suffix if present and parse
    ts_clean = ts.replace('Z', '+00:00')
    
    try:
        dt = datetime.fromisoformat(ts_clean)
    except ValueError:
        # Fallback for other formats
        dt = datetime.fromisoformat(ts)
    
    # If naive, assume UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt


def compute_risk_score(shipment_history: list[dict]) -> int:
    """
    LEGACY: Compute a risk score (0–100) based on shipment lifecycle signals.
    This is advisory only — no state changes.
    
    NOTE: Kept for backward compatibility. Use compute_risk_fusion() for new code.
    """

    score = 0

    # Base risk for any shipment
    score += 10

    # Longer lifecycle → higher risk
    if len(shipment_history) >= 5:
        score += 20

    # Check for warehouse delay
    timestamps = [
        _parse_timestamp(event["timestamp"])
        for event in shipment_history
    ]

    if len(timestamps) >= 2:
        total_duration = (timestamps[-1] - timestamps[0]).total_seconds() / 3600
        if total_duration > 24:
            score += 20

    # Receiver handover adds complexity
    event_types = {e["event_type"] for e in shipment_history}
    if "RECEIVER_ACKNOWLEDGED" in event_types:
        score += 10

    return min(score, 100)


def compute_historical_corridor_risk(
    corridor: str,
    historical_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Compute historical corridor risk from past performance.
    
    Args:
        corridor: Corridor identifier (e.g., "MH-KA")
        historical_data: Optional historical breach data
        
    Returns:
        dict: Historical risk assessment
            - risk_score: 0-100
            - breach_rate: Historical breach percentage
            - reliability_score: Corridor reliability (0-1)
    """
    # Mock historical breach rates by corridor
    # Production: Query from analytics database
    default_breach_rates = {
        "MH-KA": 12,
        "MH-GJ": 8,
        "DL-HR": 15,
        "TN-KA": 10,
        "KL-TN": 5,
        "DL-MH": 18,
        "WB-DL": 20,
    }
    
    breach_rate = default_breach_rates.get(corridor, 10)  # Default 10%
    
    if historical_data:
        breach_rate = historical_data.get("breach_rate", breach_rate)
    
    # Convert breach rate to risk score
    risk_score = min(breach_rate * 5, 100)
    
    # Reliability is inverse of risk
    reliability_score = max(0, 1.0 - (risk_score / 100))
    
    return {
        "risk_score": risk_score,
        "breach_rate": breach_rate,
        "reliability_score": round(reliability_score, 2),
    }


def compute_eta_uncertainty_risk(
    eta_hours: float,
    sla_hours: int,
    route_confidence: float
) -> Dict[str, Any]:
    """
    Compute risk from ETA uncertainty.
    
    Args:
        eta_hours: Estimated travel time
        sla_hours: SLA deadline
        route_confidence: Confidence in ETA (0-1)
        
    Returns:
        dict: ETA uncertainty risk
            - risk_score: 0-100
            - sla_utilization: Percentage of SLA used
            - buffer_hours: Remaining buffer
    """
    # Calculate SLA utilization (with 20% buffer)
    buffered_eta = eta_hours * 1.2
    sla_utilization = (buffered_eta / sla_hours) if sla_hours > 0 else 1.0
    buffer_hours = sla_hours - buffered_eta
    
    # Base risk from utilization
    if sla_utilization > 1.0:
        base_risk = 100  # Already over SLA
    elif sla_utilization > 0.9:
        base_risk = 80
    elif sla_utilization > 0.75:
        base_risk = 60
    elif sla_utilization > 0.5:
        base_risk = 40
    else:
        base_risk = 20
    
    # Adjust for confidence
    # Low confidence increases risk
    confidence_factor = 1.0 + (1.0 - route_confidence) * 0.5
    
    risk_score = min(int(base_risk * confidence_factor), 100)
    
    return {
        "risk_score": risk_score,
        "sla_utilization": round(sla_utilization * 100, 1),
        "buffer_hours": round(buffer_hours, 2),
    }


def fuse_risk_signals(
    weather_risk: int,
    corridor_risk: int,
    eta_risk: int,
    use_worst_case_boost: bool = True
) -> int:
    """
    Fuse multiple risk signals using weighted hybrid model.
    
    Args:
        weather_risk: Weather risk score (0-100)
        corridor_risk: Corridor historical risk (0-100)
        eta_risk: ETA uncertainty risk (0-100)
        use_worst_case_boost: Apply worst-case penalty
        
    Returns:
        int: Fused risk score (0-100)
        
    Model:
    1. Base: Weighted average
       - Weather: 30%
       - Corridor: 30%
       - ETA: 40%
    2. Worst-case boost: If any signal > 80, add 10% penalty
    """
    # Weighted average
    weights = {
        "weather": 0.30,
        "corridor": 0.30,
        "eta": 0.40,
    }
    
    weighted_avg = (
        weather_risk * weights["weather"] +
        corridor_risk * weights["corridor"] +
        eta_risk * weights["eta"]
    )
    
    # Worst-case boost
    if use_worst_case_boost:
        max_risk = max(weather_risk, corridor_risk, eta_risk)
        if max_risk >= 80:
            penalty = 10
            weighted_avg = min(weighted_avg + penalty, 100)
    
    return int(weighted_avg)


def determine_risk_level(total_risk: int) -> str:
    """
    Determine risk level from total risk score.
    
    Args:
        total_risk: Total risk score (0-100)
        
    Returns:
        str: Risk level (LOW/MEDIUM/HIGH/CRITICAL)
    """
    if total_risk < 30:
        return "LOW"
    elif total_risk < 60:
        return "MEDIUM"
    elif total_risk < 80:
        return "HIGH"
    else:
        return "CRITICAL"


def should_recommend_override(
    total_risk: int,
    weather_risk: int,
    eta_risk: int,
    corridor_risk: int
) -> bool:
    """
    Determine if manager override is recommended.
    
    Args:
        total_risk: Total risk score
        weather_risk: Weather risk score
        eta_risk: ETA risk score
        corridor_risk: Corridor risk score
        
    Returns:
        bool: True if override recommended
        
    Logic:
    - Total risk >= 80: Definitely recommend override
    - Total risk >= 60 AND any individual risk >= 80: Recommend
    - Otherwise: Don't recommend
    """
    if total_risk >= 80:
        return True
    
    if total_risk >= 60:
        if max(weather_risk, eta_risk, corridor_risk) >= 80:
            return True
    
    return False


def generate_risk_explanation(
    total_risk: int,
    weather_risk: int,
    corridor_risk: int,
    eta_risk: int,
    weather_data: Optional[Dict[str, Any]] = None,
    corridor_data: Optional[Dict[str, Any]] = None,
    eta_data: Optional[Dict[str, Any]] = None
) -> List[str]:
    """
    Generate human-readable risk explanation bullets.
    
    Args:
        total_risk: Total risk score
        weather_risk: Weather risk score
        corridor_risk: Corridor risk score
        eta_risk: ETA risk score
        weather_data: Optional weather details
        corridor_data: Optional corridor details
        eta_data: Optional ETA details
        
    Returns:
        List[str]: Explanation bullets
    """
    bullets = []
    
    # Weather
    if weather_risk >= 70:
        if weather_data:
            explanation = weather_data.get("explanation", "Severe weather conditions")
        else:
            explanation = "High weather risk detected"
        bullets.append(f"🌦️ {explanation}")
    elif weather_risk >= 40:
        bullets.append(f"🌤️ Moderate weather risk ({weather_risk}%)")
    
    # Corridor
    if corridor_risk >= 70:
        if corridor_data:
            breach_rate = corridor_data.get("breach_rate", 0)
            bullets.append(f"🛣️ Corridor has {breach_rate}% historical SLA breach rate")
        else:
            bullets.append(f"🛣️ High corridor risk ({corridor_risk}%)")
    elif corridor_risk >= 40:
        bullets.append(f"🛣️ Moderate corridor risk")
    
    # ETA
    if eta_risk >= 70:
        if eta_data:
            sla_util = eta_data.get("sla_utilization", 100)
            bullets.append(f"⏰ ETA uses {sla_util}% of SLA - very tight timeline")
        else:
            bullets.append(f"⏰ High ETA uncertainty ({eta_risk}%)")
    elif eta_risk >= 40:
        bullets.append(f"⏰ Moderate SLA pressure")
    
    # Overall assessment
    if total_risk >= 80:
        bullets.append("🚨 CRITICAL: Multiple high-risk factors converge")
    elif total_risk >= 60:
        bullets.append("⚠️ HIGH RISK: Close monitoring required")
    
    # Positive signals
    if total_risk < 30:
        bullets.append("✅ All risk indicators are favorable")
    
    return bullets


def compute_risk_fusion(
    source_geo: Dict[str, Any],
    destination_geo: Dict[str, Any],
    corridor: str,
    sla_hours: int,
    historical_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Compute fused risk assessment combining all signals.
    
    Args:
        source_geo: Source location {lat, lon}
        destination_geo: Destination location {lat, lon}
        corridor: Corridor identifier
        sla_hours: SLA deadline in hours
        historical_data: Optional historical corridor data
        
    Returns:
        dict: Complete risk assessment
            - total_risk_score: 0-100
            - risk_level: LOW/MEDIUM/HIGH/CRITICAL
            - override_recommended: bool
            - weather_risk: Weather risk details
            - corridor_risk: Corridor risk details
            - eta_risk: ETA risk details
            - explanation: List of explanation bullets
            - recommendation: Actionable recommendation
            
    Notes:
        - Calls external APIs (weather, ETA)
        - Graceful degradation if APIs fail
        - Detailed explanations for all decisions
    """
    try:
        # Import engines
        from app.intelligence.weather_engine import get_weather_risk
        from app.intelligence.eta_engine import compute_eta
        
        # Fetch weather risk
        weather_result = get_weather_risk(source_geo, destination_geo)
        weather_risk_score = weather_result.get("weather_risk_score", 50)
        
        # Fetch ETA
        eta_result = compute_eta(source_geo, destination_geo)
        eta_hours = eta_result.get("eta_hours", 24)
        route_confidence = eta_result.get("route_confidence", 0.5)
        
        # Compute ETA uncertainty risk
        eta_risk_result = compute_eta_uncertainty_risk(
            eta_hours, sla_hours, route_confidence
        )
        eta_risk_score = eta_risk_result.get("risk_score", 50)
        
        # Compute corridor risk
        corridor_result = compute_historical_corridor_risk(corridor, historical_data)
        corridor_risk_score = corridor_result.get("risk_score", 50)
        
        # Fuse all signals
        total_risk_score = fuse_risk_signals(
            weather_risk_score,
            corridor_risk_score,
            eta_risk_score,
            use_worst_case_boost=True
        )
        
        # Determine risk level
        risk_level = determine_risk_level(total_risk_score)
        
        # Override recommendation
        override_recommended = should_recommend_override(
            total_risk_score,
            weather_risk_score,
            eta_risk_score,
            corridor_risk_score
        )
        
        # Generate explanation
        explanation = generate_risk_explanation(
            total_risk_score,
            weather_risk_score,
            corridor_risk_score,
            eta_risk_score,
            weather_data=weather_result,
            corridor_data=corridor_result,
            eta_data=eta_risk_result
        )
        
        # Generate recommendation
        if override_recommended:
            recommendation = (
                "🚨 OVERRIDE RECOMMENDED: Risk level is too high for auto-approval. "
                "Manager review required."
            )
        elif total_risk_score >= 60:
            recommendation = (
                "⚠️ CAUTION: High risk detected. Approve only if priority handling can be guaranteed."
            )
        elif total_risk_score >= 40:
            recommendation = (
                "ℹ️ MODERATE: Approve with standard monitoring. No special action needed."
            )
        else:
            recommendation = (
                "✅ LOW RISK: Safe to approve with standard procedures."
            )
        
        return {
            "total_risk_score": total_risk_score,
            "risk_level": risk_level,
            "override_recommended": override_recommended,
            "weather_risk": {
                "score": weather_risk_score,
                "details": weather_result,
            },
            "corridor_risk": {
                "score": corridor_risk_score,
                "details": corridor_result,
            },
            "eta_risk": {
                "score": eta_risk_score,
                "details": eta_risk_result,
                "eta_hours": eta_hours,
            },
            "explanation": explanation,
            "recommendation": recommendation,
        }
    
    except Exception as e:
        logger.error(f"Risk fusion error: {str(e)}")
        
        # Fallback to neutral risk
        return {
            "total_risk_score": 50,
            "risk_level": "MEDIUM",
            "override_recommended": False,
            "weather_risk": {"score": 50, "details": {}},
            "corridor_risk": {"score": 50, "details": {}},
            "eta_risk": {"score": 50, "details": {}},
            "explanation": ["⚠️ Risk calculation unavailable. Using neutral estimate."],
            "recommendation": "ℹ️ Unable to compute full risk assessment. Manual review suggested.",
        }
