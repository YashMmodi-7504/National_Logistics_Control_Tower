from app.intelligence.sla_engine import predict_sla_breach

print(
    predict_sla_breach(
        shipment_state="IN_TRANSIT",
        risk_score=65,
        hours_elapsed=40
    )
)

print(
    predict_sla_breach(
        shipment_state="OUT_FOR_DELIVERY",
        risk_score=20,
        hours_elapsed=3
    )
)
