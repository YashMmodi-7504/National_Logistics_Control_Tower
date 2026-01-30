"""
REGULATOR VIEWS

Purpose:
- Provide regulator-safe read models
- Read ONLY from snapshot_store
- Flat structures with no joins

Rules:
- Read ONLY from snapshot_store
- Flat structures (lists/dicts)
- No joins across snapshots
- No correlations
- No drilldowns
- Handle missing snapshots safely
- Return explainable data only
"""

from typing import Dict, Any, List, Optional
from app.core.snapshot_store import read_snapshot
from app.guards.regulator_guard import assert_regulator_access


# ==================================================
# SLA HEALTH SUMMARY
# ==================================================

def get_sla_health_summary() -> Dict[str, Any]:
    """
    Get SLA health summary from snapshot.
    
    Returns:
        Dictionary with:
        - snapshot_exists: bool
        - generated_at: timestamp or None
        - total_shipments: int
        - high_risk_count: int (breach_probability > 0.7)
        - medium_risk_count: int (breach_probability 0.4-0.7)
        - low_risk_count: int (breach_probability < 0.4)
        - avg_breach_probability: float or None
    """
    # Enforce regulator access
    assert_regulator_access({
        "operation": "read_snapshot",
        "snapshot_name": "sla_snapshot",
    })
    
    snapshot = read_snapshot("sla_snapshot")
    
    if snapshot is None:
        return {
            "snapshot_exists": False,
            "generated_at": None,
            "total_shipments": 0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0,
            "avg_breach_probability": None,
        }
    
    generated_at = snapshot.get("generated_at")
    data = snapshot.get("data", {})
    
    # Calculate risk categories
    high_risk = 0
    medium_risk = 0
    low_risk = 0
    probabilities = []
    
    for shipment_data in data.values():
        if isinstance(shipment_data, dict):
            prob = shipment_data.get("breach_probability", 0)
            probabilities.append(prob)
            
            if prob > 0.7:
                high_risk += 1
            elif prob >= 0.4:
                medium_risk += 1
            else:
                low_risk += 1
    
    avg_prob = sum(probabilities) / len(probabilities) if probabilities else None
    
    return {
        "snapshot_exists": True,
        "generated_at": generated_at,
        "total_shipments": len(data),
        "high_risk_count": high_risk,
        "medium_risk_count": medium_risk,
        "low_risk_count": low_risk,
        "avg_breach_probability": avg_prob,
    }


# ==================================================
# CORRIDOR HEALTH SUMMARY
# ==================================================

def get_corridor_health_summary() -> Dict[str, Any]:
    """
    Get corridor health summary from snapshot.
    
    Returns:
        Dictionary with:
        - snapshot_exists: bool
        - generated_at: timestamp or None
        - total_corridors: int
        - corridors: list of corridor data (flat)
    """
    # Enforce regulator access
    assert_regulator_access({
        "operation": "read_snapshot",
        "snapshot_name": "corridor_snapshot",
    })
    
    snapshot = read_snapshot("corridor_snapshot")
    
    if snapshot is None:
        return {
            "snapshot_exists": False,
            "generated_at": None,
            "total_corridors": 0,
            "corridors": [],
        }
    
    generated_at = snapshot.get("generated_at")
    data = snapshot.get("data", [])
    
    # Flatten corridor data (no nested objects)
    corridors = []
    for corridor in data:
        if isinstance(corridor, dict):
            corridors.append({
                "corridor": corridor.get("corridor", "Unknown"),
                "source_state": corridor.get("source_state", "Unknown"),
                "destination_state": corridor.get("destination_state", "Unknown"),
                "avg_breach_probability": corridor.get("avg_breach_probability", 0),
                "shipment_count": corridor.get("shipment_count", 0),
            })
    
    return {
        "snapshot_exists": True,
        "generated_at": generated_at,
        "total_corridors": len(corridors),
        "corridors": corridors,
    }


# ==================================================
# ALERTS TIMELINE
# ==================================================

def get_alerts_timeline() -> Dict[str, Any]:
    """
    Get alerts timeline from snapshot.
    
    Returns:
        Dictionary with:
        - snapshot_exists: bool
        - generated_at: timestamp or None
        - total_alerts: int
        - alerts: list of alert data (flat)
    """
    # Enforce regulator access
    assert_regulator_access({
        "operation": "read_snapshot",
        "snapshot_name": "alerts_snapshot",
    })
    
    snapshot = read_snapshot("alerts_snapshot")
    
    if snapshot is None:
        return {
            "snapshot_exists": False,
            "generated_at": None,
            "total_alerts": 0,
            "alerts": [],
        }
    
    generated_at = snapshot.get("generated_at")
    alerts = snapshot.get("alerts", [])
    
    # Flatten alert data
    flat_alerts = []
    for alert in alerts:
        if isinstance(alert, dict):
            flat_alerts.append({
                "corridor": alert.get("corridor", "Unknown"),
                "breach_probability": alert.get("breach_probability", 0),
                "severity": _calculate_severity(alert.get("breach_probability", 0)),
                "shipment_count": alert.get("shipment_count", 0),
            })
    
    return {
        "snapshot_exists": True,
        "generated_at": generated_at,
        "total_alerts": len(flat_alerts),
        "alerts": flat_alerts,
    }


# ==================================================
# SNAPSHOT METADATA
# ==================================================

def get_snapshot_metadata() -> List[Dict[str, Any]]:
    """
    Get metadata for all available snapshots.
    
    Returns:
        List of dictionaries with:
        - snapshot_name: str
        - exists: bool
        - generated_at: timestamp or None
        - description: str
    """
    from app.policies.regulator_policy import ALLOWED_SNAPSHOTS, get_snapshot_description
    
    metadata = []
    
    for snapshot_name in ALLOWED_SNAPSHOTS:
        # Enforce regulator access
        assert_regulator_access({
            "operation": "read_snapshot",
            "snapshot_name": snapshot_name,
        })
        
        snapshot = read_snapshot(snapshot_name)
        
        metadata.append({
            "snapshot_name": snapshot_name,
            "exists": snapshot is not None,
            "generated_at": snapshot.get("generated_at") if snapshot else None,
            "description": get_snapshot_description(snapshot_name),
        })
    
    return metadata


# ==================================================
# HEATMAP DATA
# ==================================================

def get_heatmap_summary() -> Dict[str, Any]:
    """
    Get heatmap summary from snapshot.
    
    Returns:
        Dictionary with:
        - snapshot_exists: bool
        - generated_at: timestamp or None
        - total_points: int
        - high_risk_points: int
    """
    # Enforce regulator access
    assert_regulator_access({
        "operation": "read_snapshot",
        "snapshot_name": "heatmap_snapshot",
    })
    
    snapshot = read_snapshot("heatmap_snapshot")
    
    if snapshot is None:
        return {
            "snapshot_exists": False,
            "generated_at": None,
            "total_points": 0,
            "high_risk_points": 0,
        }
    
    generated_at = snapshot.get("generated_at")
    points = snapshot.get("points", [])
    
    # Count high risk points (risk_weight > 0.7)
    high_risk = sum(1 for p in points if isinstance(p, dict) and p.get("risk_weight", 0) > 0.7)
    
    return {
        "snapshot_exists": True,
        "generated_at": generated_at,
        "total_points": len(points),
        "high_risk_points": high_risk,
    }


# ==================================================
# COMPLIANCE STATUS
# ==================================================

def get_compliance_status() -> Dict[str, Any]:
    """
    Get overall compliance status from snapshots.
    
    Returns:
        Dictionary with:
        - all_snapshots_available: bool
        - missing_snapshots: list
        - last_update: timestamp or None
    """
    from app.policies.regulator_policy import ALLOWED_SNAPSHOTS
    
    missing = []
    last_update = None
    
    for snapshot_name in ALLOWED_SNAPSHOTS:
        assert_regulator_access({
            "operation": "read_snapshot",
            "snapshot_name": snapshot_name,
        })
        
        snapshot = read_snapshot(snapshot_name)
        
        if snapshot is None:
            missing.append(snapshot_name)
        else:
            generated_at = snapshot.get("generated_at")
            if generated_at and (last_update is None or generated_at > last_update):
                last_update = generated_at
    
    return {
        "all_snapshots_available": len(missing) == 0,
        "missing_snapshots": missing,
        "last_update": last_update,
        "total_snapshots": len(ALLOWED_SNAPSHOTS),
        "available_snapshots": len(ALLOWED_SNAPSHOTS) - len(missing),
    }


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def _calculate_severity(breach_probability: float) -> str:
    """
    Calculate severity level from breach probability.
    
    Args:
        breach_probability: Probability value (0-1)
    
    Returns:
        Severity level: CRITICAL, HIGH, MEDIUM, LOW
    """
    if breach_probability >= 0.8:
        return "CRITICAL"
    elif breach_probability >= 0.6:
        return "HIGH"
    elif breach_probability >= 0.4:
        return "MEDIUM"
    else:
        return "LOW"
