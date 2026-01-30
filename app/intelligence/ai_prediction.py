"""
AI PREDICTION AT SHIPMENT CREATION

Purpose:
- Immediate AI inference at SHIPMENT_CREATED event
- Weather risk assessment
- Route risk calculation
- Historical corridor risk
- SLA breach probability
- Explainable predictions

Requirements:
• Runs at shipment creation
• Results attached to metadata
• Instantly visible in UI
• Explainable AI
• Mock acceptable for weather

Author: National Logistics Control Tower
Phase: 9.8 - AI Prediction at Creation
"""

import time
from typing import Dict, Any, List, Optional
from datetime import datetime


def predict_weather_risk(
    source_state: str,
    destination_state: str,
    departure_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Predict weather risk for shipment route.
    
    Args:
        source_state: Origin state
        destination_state: Destination state
        departure_date: Expected departure date (YYYY-MM-DD)
        
    Returns:
        dict: Weather risk assessment
            - risk_score: 0-100
            - risk_level: LOW/MEDIUM/HIGH/CRITICAL
            - explanation: Human-readable reason
            - factors: Contributing factors
            
    Notes:
        - Currently uses mock data
        - Production: Integrate with weather API
        - Monsoon season increases risk
    """
    # Mock weather risk based on state and season
    risk_score = 20  # Base risk
    factors = []
    
    # Monsoon-prone states (June-September)
    monsoon_states = ["Maharashtra", "Kerala", "Karnataka", "Goa", "West Bengal"]
    now = datetime.now()
    is_monsoon_season = 6 <= now.month <= 9
    
    if source_state in monsoon_states or destination_state in monsoon_states:
        if is_monsoon_season:
            risk_score += 30
            factors.append("Monsoon season in route")
    
    # Himalayan states (winter risk)
    himalayan_states = ["Himachal Pradesh", "Uttarakhand", "Jammu and Kashmir", "Ladakh"]
    is_winter = now.month in [12, 1, 2]
    
    if source_state in himalayan_states or destination_state in himalayan_states:
        if is_winter:
            risk_score += 25
            factors.append("Winter weather in mountainous region")
    
    # Determine risk level
    if risk_score < 30:
        risk_level = "LOW"
    elif risk_score < 60:
        risk_level = "MEDIUM"
    elif risk_score < 80:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"
    
    # Generate explanation
    if risk_score < 30:
        explanation = "Weather conditions are favorable for transit."
    elif risk_score < 60:
        explanation = f"Moderate weather risk due to: {', '.join(factors)}."
    else:
        explanation = f"High weather risk detected: {', '.join(factors)}. Consider delay or route change."
    
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "explanation": explanation,
        "factors": factors,
        "model": "weather_risk_v1_mock",
    }


def predict_route_risk(
    source_state: str,
    destination_state: str,
    corridor: str
) -> Dict[str, Any]:
    """
    Predict route risk based on corridor characteristics.
    
    Args:
        source_state: Origin state
        destination_state: Destination state
        corridor: Corridor identifier (e.g., "MH-KA")
        
    Returns:
        dict: Route risk assessment
            - risk_score: 0-100
            - risk_level: LOW/MEDIUM/HIGH/CRITICAL
            - explanation: Human-readable reason
            - factors: Contributing factors
    """
    risk_score = 15  # Base risk
    factors = []
    
    # High-traffic corridors
    high_traffic = ["MH-KA", "MH-GJ", "DL-HR", "TN-KA"]
    if corridor in high_traffic:
        risk_score += 10
        factors.append("High traffic corridor")
    
    # Long-distance corridors
    long_distance_pairs = [
        ("Delhi", "Tamil Nadu"),
        ("Kerala", "Jammu and Kashmir"),
        ("West Bengal", "Gujarat"),
    ]
    
    for src, dst in long_distance_pairs:
        if (src in source_state or src in destination_state) and \
           (dst in source_state or dst in destination_state):
            risk_score += 20
            factors.append("Long-distance route (>1500 km)")
            break
    
    # Border states (customs delays)
    border_states = ["Punjab", "Rajasthan", "West Bengal", "Assam"]
    if source_state in border_states or destination_state in border_states:
        risk_score += 5
        factors.append("Border state (possible delays)")
    
    # Determine risk level
    if risk_score < 30:
        risk_level = "LOW"
    elif risk_score < 60:
        risk_level = "MEDIUM"
    elif risk_score < 80:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"
    
    # Generate explanation
    if risk_score < 30:
        explanation = "Route is optimal with minimal known risks."
    else:
        explanation = f"Route risk factors: {', '.join(factors)}."
    
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "explanation": explanation,
        "factors": factors,
        "model": "route_risk_v1",
    }


def predict_historical_corridor_risk(corridor: str) -> Dict[str, Any]:
    """
    Predict risk based on historical corridor performance.
    
    Args:
        corridor: Corridor identifier (e.g., "MH-KA")
        
    Returns:
        dict: Historical risk assessment
            - risk_score: 0-100
            - risk_level: LOW/MEDIUM/HIGH/CRITICAL
            - explanation: Human-readable reason
            - historical_sla_breach_rate: Percentage of breaches
    """
    # Mock historical data
    # Production: Query from analytics database
    
    historical_breach_rates = {
        "MH-KA": 12,
        "MH-GJ": 8,
        "DL-HR": 15,
        "TN-KA": 10,
        "KL-TN": 5,
    }
    
    breach_rate = historical_breach_rates.get(corridor, 10)  # Default 10%
    
    # Convert breach rate to risk score
    risk_score = min(breach_rate * 5, 100)
    
    # Determine risk level
    if risk_score < 30:
        risk_level = "LOW"
    elif risk_score < 60:
        risk_level = "MEDIUM"
    elif risk_score < 80:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"
    
    # Generate explanation
    explanation = (
        f"Historical analysis shows {breach_rate}% SLA breach rate for this corridor. "
        f"Risk level: {risk_level}."
    )
    
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "explanation": explanation,
        "historical_sla_breach_rate": breach_rate,
        "model": "historical_corridor_v1",
    }


def predict_sla_breach_probability(
    source_state: str,
    destination_state: str,
    corridor: str,
    sla_hours: int,
    weather_risk: int,
    route_risk: int,
    historical_risk: int
) -> Dict[str, Any]:
    """
    Predict probability of SLA breach.
    
    Args:
        source_state: Origin state
        destination_state: Destination state
        corridor: Corridor identifier
        sla_hours: SLA in hours
        weather_risk: Weather risk score (0-100)
        route_risk: Route risk score (0-100)
        historical_risk: Historical risk score (0-100)
        
    Returns:
        dict: SLA breach prediction
            - breach_probability: 0-100 (percentage)
            - risk_level: LOW/MEDIUM/HIGH/CRITICAL
            - explanation: Human-readable reason
            - contributing_factors: Weighted factors
    """
    # Weighted combination of risk factors
    weights = {
        "weather": 0.3,
        "route": 0.3,
        "historical": 0.4,
    }
    
    # Calculate weighted risk
    weighted_risk = (
        weather_risk * weights["weather"] +
        route_risk * weights["route"] +
        historical_risk * weights["historical"]
    )
    
    # Adjust for SLA tightness
    # Shorter SLA = higher breach probability
    if sla_hours < 24:
        weighted_risk += 15
    elif sla_hours < 48:
        weighted_risk += 10
    elif sla_hours < 72:
        weighted_risk += 5
    
    breach_probability = min(int(weighted_risk), 100)
    
    # Determine risk level
    if breach_probability < 30:
        risk_level = "LOW"
    elif breach_probability < 60:
        risk_level = "MEDIUM"
    elif breach_probability < 80:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"
    
    # Generate explanation
    if breach_probability < 30:
        explanation = f"Low risk of SLA breach ({breach_probability}%). Shipment should arrive on time."
    elif breach_probability < 60:
        explanation = f"Moderate risk of SLA breach ({breach_probability}%). Monitor closely."
    else:
        explanation = f"High risk of SLA breach ({breach_probability}%). Consider priority handling."
    
    return {
        "breach_probability": breach_probability,
        "risk_level": risk_level,
        "explanation": explanation,
        "contributing_factors": {
            "weather_risk": weather_risk,
            "route_risk": route_risk,
            "historical_risk": historical_risk,
            "sla_tightness": "HIGH" if sla_hours < 48 else "MEDIUM",
        },
        "model": "sla_breach_v1",
    }


def run_ai_predictions_at_creation(shipment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run all AI predictions at shipment creation.
    
    Args:
        shipment: Shipment data with source, destination, corridor, SLA
        
    Returns:
        dict: Complete AI predictions
            - weather_risk: Weather risk assessment
            - route_risk: Route risk assessment
            - historical_risk: Historical corridor risk
            - sla_breach: SLA breach prediction
            - combined_risk_score: Overall risk (0-100)
            - combined_risk_level: Overall level
            - ai_explanation: Summary explanation
            - timestamp: Prediction timestamp
            
    Notes:
        - Called immediately after SHIPMENT_CREATED event
        - Results attached to shipment metadata
        - Visible in manager UI instantly
    """
    source_state = shipment.get("source_state", "Unknown")
    destination_state = shipment.get("destination_state", "Unknown")
    corridor = shipment.get("corridor", "UNKNOWN")
    sla_hours = shipment.get("sla_hours", 72)
    
    # Run predictions
    weather = predict_weather_risk(source_state, destination_state)
    route = predict_route_risk(source_state, destination_state, corridor)
    historical = predict_historical_corridor_risk(corridor)
    sla = predict_sla_breach_probability(
        source_state=source_state,
        destination_state=destination_state,
        corridor=corridor,
        sla_hours=sla_hours,
        weather_risk=weather["risk_score"],
        route_risk=route["risk_score"],
        historical_risk=historical["risk_score"],
    )
    
    # Calculate combined risk
    combined_risk_score = int(
        (weather["risk_score"] + route["risk_score"] + historical["risk_score"]) / 3
    )
    
    # Determine combined risk level
    if combined_risk_score < 30:
        combined_risk_level = "LOW"
    elif combined_risk_score < 60:
        combined_risk_level = "MEDIUM"
    elif combined_risk_score < 80:
        combined_risk_level = "HIGH"
    else:
        combined_risk_level = "CRITICAL"
    
    # Generate summary explanation
    ai_explanation = (
        f"AI Analysis: {combined_risk_level} risk shipment. "
        f"Weather: {weather['risk_level']}, "
        f"Route: {route['risk_level']}, "
        f"Historical: {historical['risk_level']}. "
        f"SLA breach probability: {sla['breach_probability']}%."
    )
    
    return {
        "weather_risk": weather,
        "route_risk": route,
        "historical_risk": historical,
        "sla_breach": sla,
        "combined_risk_score": combined_risk_score,
        "combined_risk_level": combined_risk_level,
        "ai_explanation": ai_explanation,
        "timestamp": time.time(),
        "models_used": [
            weather["model"],
            route["model"],
            historical["model"],
            sla["model"],
        ],
    }


def get_ai_recommendation(predictions: Dict[str, Any]) -> str:
    """
    Get actionable recommendation based on AI predictions.
    
    Args:
        predictions: AI predictions from run_ai_predictions_at_creation
        
    Returns:
        str: Actionable recommendation
    """
    combined_risk = predictions["combined_risk_score"]
    sla_probability = predictions["sla_breach"]["breach_probability"]
    
    if combined_risk >= 80:
        return "🚨 CRITICAL: Reject shipment or request manager override. Risk too high."
    elif combined_risk >= 60:
        return "⚠️ HIGH RISK: Approve only if priority handling can be guaranteed."
    elif sla_probability >= 70:
        return "⚠️ SLA RISK: Consider expedited handling or notify customer of possible delay."
    elif combined_risk >= 40:
        return "ℹ️ MODERATE: Approve with standard handling. Monitor progress."
    else:
        return "✅ LOW RISK: Safe to approve with standard procedures."
