# app/intelligence/sla_engine.py

from typing import Dict, List
from datetime import datetime, timezone


def _parse_timestamp(ts: str) -> datetime:
    """
    Parse ISO timestamp, handling both timezone-aware and naive formats.
    Converts all to UTC timezone-aware for consistent comparison.
    """
    # Remove 'Z' suffix if present and parse
    ts_clean = ts.replace('Z', '+00:00')
    
    try:
        dt = datetime.fromisoformat(ts_clean)
    except ValueError:
        # Fallback for other formats
        dt = datetime.fromisoformat(ts)
    
    # If naive, assume UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt


def _hours_between(ts1: str, ts2: str) -> float:
    """Calculate hours between two timestamps, handling timezone differences."""
    t1 = _parse_timestamp(ts1)
    t2 = _parse_timestamp(ts2)
    return abs((t2 - t1).total_seconds()) / 3600


def predict_sla_breach(*, history: List[Dict]) -> Dict:
    """
    Predict SLA breach probability based on shipment lifecycle history.

    Input:
        history: list of domain events (immutable)

    Output:
        {
            eta_hours,
            hours_elapsed,
            sla_utilization,
            breach_probability,
            risk_level
        }
    """

    if not history or len(history) < 2:
        return {
            "eta_hours": 0,
            "hours_elapsed": 0,
            "sla_utilization": 0,
            "breach_probability": 0.0,
            "risk_level": "LOW",
        }

    start_ts = history[0]["timestamp"]
    last_ts = history[-1]["timestamp"]

    hours_elapsed = _hours_between(start_ts, last_ts)

    # Heuristic ETA model (replace later with ML)
    eta_hours = max(8, 2.2 * len(history) ** 1.3)

    sla_utilization = min(hours_elapsed / eta_hours, 1.5)

    if sla_utilization < 0.6:
        breach_probability = 0.1
        risk_level = "LOW"
    elif sla_utilization < 0.85:
        breach_probability = 0.4
        risk_level = "MEDIUM"
    else:
        breach_probability = 0.8
        risk_level = "HIGH"

    return {
        "eta_hours": round(eta_hours, 2),
        "hours_elapsed": round(hours_elapsed, 2),
        "sla_utilization": round(sla_utilization, 2),
        "breach_probability": breach_probability,
        "risk_level": risk_level,
    }
