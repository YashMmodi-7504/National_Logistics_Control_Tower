from app.core.corridor_read_model import get_all_corridors, get_high_risk_corridors

print("ALL CORRIDORS")
for c in get_all_corridors():
    print(c)

print("\nHIGH RISK CORRIDORS")
for c in get_high_risk_corridors():
    print(c)
