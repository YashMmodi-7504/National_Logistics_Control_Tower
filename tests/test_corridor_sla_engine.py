from app.intelligence.corridor_alert_engine import detect_corridor_alerts

if __name__ == "__main__":
    alerts = detect_corridor_alerts()

    if not alerts:
        print("✅ No corridor alerts detected")
    else:
        print("🚨 CORRIDOR ALERTS")
        for a in alerts:
            print(
                f"{a['corridor']} | {a['alert_type']} | "
                f"Severity: {a['severity']} | Avg Breach: {a['avg_breach']}"
            )
