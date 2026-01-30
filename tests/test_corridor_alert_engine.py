from app.intelligence.corridor_alert_engine import (
    detect_corridor_alerts
)

def test_corridor_alerts():
    alerts = detect_corridor_alerts()

    print("ALERTS:")
    for a in alerts:
        print(a)

if __name__ == "__main__":
    test_corridor_alerts()
