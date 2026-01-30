from app.intelligence.sla_engine import predict_sla_breach

history = [
    {"timestamp": "2026-01-01T10:00:00"},
    {"timestamp": "2026-01-03T02:00:00"},
]

result = predict_sla_breach(history=history)
print(result)
