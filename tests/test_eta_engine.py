from app.intelligence.eta_engine import get_eta

history = [
    {"timestamp": "2026-01-01T10:00:00"},
    {"timestamp": "2026-01-02T12:00:00"},
]

print(get_eta(history=history))
