# app/intelligence/explainability.py


def generate_explanation(risk_score: int, shipment_history: list[dict]) -> list[str]:
    """
    Generate human-readable explanations for AI suggestions.
    """

    reasons = []

    if risk_score >= 60:
        reasons.append("Long transit duration increases delay risk")

    if len(shipment_history) >= 5:
        reasons.append("Multiple operational handovers detected")

    event_types = {e["event_type"] for e in shipment_history}
    if "WAREHOUSE_INTAKE_STARTED" in event_types:
        reasons.append("Shipment currently inside warehouse processing")

    if not reasons:
        reasons.append("No significant operational risk detected")

    return reasons
