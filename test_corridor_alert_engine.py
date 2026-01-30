from app.intelligence.corridor_alert_engine import detect_corridor_alerts
from app.intelligence.corridor_sla_engine import compute_corridor_sla_health

# monkey patch (test-only)
def fake_health():
    return {
        "Gujarat → Maharashtra": {
            "avg_breach_probability": 0.72,
            "max_breach_probability": 0.91,
            "shipment_count": 6
        }
    }

import app.intelligence.corridor_sla_engine
app.intelligence.corridor_sla_engine.compute_corridor_sla_health = fake_health

alerts = detect_corridor_alerts()
print(alerts)
