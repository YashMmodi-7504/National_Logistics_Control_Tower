# app/intelligence/priority_engine.py


def compute_priority(risk_score: int) -> str:
    """
    Convert risk score into operational priority.
    """

    if risk_score >= 80:
        return "CRITICAL"
    if risk_score >= 60:
        return "HIGH"
    if risk_score >= 30:
        return "MEDIUM"
    return "LOW"
