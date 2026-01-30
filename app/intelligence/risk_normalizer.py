from typing import Dict


# --------------------------------------------------
# Color palette (UI-agnostic, executive friendly)
# --------------------------------------------------
RISK_COLORS = {
    "LOW": "#2ECC71",        # Green
    "MEDIUM": "#F1C40F",     # Yellow
    "HIGH": "#E67E22",       # Orange
    "CRITICAL": "#E74C3C",   # Red
}


def normalize_risk(score: float) -> int:
    """
    Normalize raw risk (0.0–1.0) → percentage (0–100)
    """
    if score < 0:
        score = 0.0
    if score > 1:
        score = 1.0

    return int(round(score * 100))


def classify_risk(score: float) -> str:
    """
    Convert raw risk into semantic bucket
    """
    pct = normalize_risk(score)

    if pct <= 25:
        return "LOW"
    if pct <= 50:
        return "MEDIUM"
    if pct <= 75:
        return "HIGH"
    return "CRITICAL"


def risk_to_color(score: float) -> str:
    """
    Convert raw risk → HEX color
    """
    level = classify_risk(score)
    return RISK_COLORS[level]


def normalize_risk_payload(score: float) -> Dict:
    """
    UI-ready normalization payload
    """
    pct = normalize_risk(score)
    level = classify_risk(score)

    return {
        "risk_score": round(score, 3),
        "risk_percent": pct,
        "risk_level": level,
        "color": RISK_COLORS[level],
    }
