from typing import List, Dict

from app.intelligence.corridor_sla_engine import compute_corridor_sla_health


# ==================================================
# CONFIG
# ==================================================
HIGH_RISK_THRESHOLD = 0.60
MEDIUM_RISK_THRESHOLD = 0.40
DRIFT_THRESHOLD = 0.20  # sudden jump in breach probability


# ==================================================
# PUBLIC API (THIS WAS MISSING)
# ==================================================
def detect_corridor_alerts() -> List[Dict]:
    """
    Detect SLA risk alerts on logistics corridors.
    Returns a list of alert dictionaries.
    """

    corridor_health = compute_corridor_sla_health()
    alerts: List[Dict] = []

    for corridor, metrics in corridor_health.items():
        avg_breach = metrics.get("avg_breach_probability", 0.0)
        max_breach = metrics.get("max_breach_probability", 0.0)
        shipment_count = metrics.get("shipment_count", 0)

        # --------------------------------------
        # Skip low-signal corridors
        # --------------------------------------
        if shipment_count < 2:
            continue

        alert_level = None
        reason = None

        # --------------------------------------
        # Threshold-based alerts
        # --------------------------------------
        if avg_breach >= HIGH_RISK_THRESHOLD:
            alert_level = "HIGH"
            reason = "Average SLA breach probability very high"

        elif avg_breach >= MEDIUM_RISK_THRESHOLD:
            alert_level = "MEDIUM"
            reason = "Elevated SLA breach probability"

        # --------------------------------------
        # Drift detection (worst-case boost)
        # --------------------------------------
        if max_breach - avg_breach >= DRIFT_THRESHOLD:
            alert_level = alert_level or "DRIFT"
            reason = "Sudden SLA risk spike detected"

        if alert_level:
            alerts.append({
                "corridor": corridor,
                "alert_level": alert_level,
                "avg_breach_probability": round(avg_breach, 2),
                "max_breach_probability": round(max_breach, 2),
                "shipment_count": shipment_count,
                "reason": reason
            })

    return alerts
