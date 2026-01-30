def risk_to_color(prob: float) -> str:
    """
    Maps breach probability → color
    """
    if prob >= 0.75:
        return "#d73027"   # Deep Red
    if prob >= 0.5:
        return "#fc8d59"   # Orange
    if prob >= 0.3:
        return "#fee08b"   # Yellow
    return "#1a9850"       # Green
