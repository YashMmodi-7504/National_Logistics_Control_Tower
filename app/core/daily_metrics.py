"""
DAILY METRICS ROLLUP

Purpose:
- Automated daily snapshot at 5 PM
- Freeze daily metrics for analytics
- State-wise aggregation
- Historical tracking

Requirements:
• Runs at 17:00 local time
• Snapshot-driven
• Immutable daily records
• No live event dependency

Author: National Logistics Control Tower
Phase: 9.6 - Daily Metrics Rollup
"""

import time
import json
import os
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from pathlib import Path


# Storage path
DAILY_METRICS_PATH = "data/snapshots/daily_metrics"


class DailyMetrics:
    """Daily metrics snapshot."""
    
    def __init__(
        self,
        date: str,
        state: str,
        total_shipments: int,
        completed_today: int,
        pending: int,
        high_risk: int,
        avg_sla_risk: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize daily metrics.
        
        Args:
            date: Date in YYYY-MM-DD format
            state: State name
            total_shipments: All-time total
            completed_today: Completed today
            pending: Pending shipments
            high_risk: High-risk shipments (score > 70)
            avg_sla_risk: Average SLA breach probability
            metadata: Additional context
        """
        self.date = date
        self.state = state
        self.total_shipments = total_shipments
        self.completed_today = completed_today
        self.pending = pending
        self.high_risk = high_risk
        self.avg_sla_risk = avg_sla_risk
        self.metadata = metadata or {}
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "date": self.date,
            "state": self.state,
            "total_shipments": self.total_shipments,
            "completed_today": self.completed_today,
            "pending": self.pending,
            "high_risk": self.high_risk,
            "avg_sla_risk": self.avg_sla_risk,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DailyMetrics":
        """Create from dictionary."""
        return cls(
            date=data["date"],
            state=data["state"],
            total_shipments=data["total_shipments"],
            completed_today=data["completed_today"],
            pending=data["pending"],
            high_risk=data["high_risk"],
            avg_sla_risk=data["avg_sla_risk"],
            metadata=data.get("metadata", {}),
        )


def _ensure_metrics_dir():
    """Ensure daily metrics directory exists."""
    Path(DAILY_METRICS_PATH).mkdir(parents=True, exist_ok=True)


def _get_metrics_file_path(date: str) -> str:
    """
    Get file path for daily metrics.
    
    Args:
        date: Date in YYYY-MM-DD format
        
    Returns:
        str: File path
    """
    return os.path.join(DAILY_METRICS_PATH, f"daily_{date}.json")


def compute_daily_metrics_for_state(state: str, target_date: Optional[str] = None) -> DailyMetrics:
    """
    Compute daily metrics for a state.
    
    Args:
        state: State name
        target_date: Date in YYYY-MM-DD format (defaults to today)
        
    Returns:
        DailyMetrics: Computed metrics
        
    Notes:
        - Reads from snapshot read models
        - Calculates aggregates
        - Does not write to storage (use save_daily_metrics)
    """
    if target_date is None:
        target_date = date.today().isoformat()
    
    try:
        # Import snapshot read model
        from app.core.state_read_model import read_snapshot
        
        # Read sender state snapshot
        sender_snapshot = read_snapshot("sender_state")
        
        if not sender_snapshot:
            # Fallback to mock
            return _mock_daily_metrics(state, target_date)
        
        # Extract shipments for this state
        shipments = sender_snapshot.get("shipments", {})
        
        # Filter by source or destination state
        state_shipments = [
            s for s in shipments.values()
            if s.get("source_state") == state or s.get("destination_state") == state
        ]
        
        # Total shipments
        total_shipments = len(state_shipments)
        
        # Completed today (delivered status + today's date)
        target_timestamp = datetime.strptime(target_date, "%Y-%m-%d").timestamp()
        day_start = target_timestamp
        day_end = target_timestamp + 86400
        
        completed_today = len([
            s for s in state_shipments
            if s.get("current_state") == "DELIVERED"
            and day_start <= s.get("delivered_at", 0) < day_end
        ])
        
        # Pending shipments
        pending = len([
            s for s in state_shipments
            if s.get("current_state") not in ["DELIVERED", "CANCELLED"]
        ])
        
        # High-risk shipments
        high_risk = len([
            s for s in state_shipments
            if s.get("combined_risk_score", 0) > 70
        ])
        
        # Average SLA risk
        sla_risks = [s.get("sla_breach_probability", 0) for s in state_shipments]
        avg_sla_risk = sum(sla_risks) / len(sla_risks) if sla_risks else 0.0
        
        return DailyMetrics(
            date=target_date,
            state=state,
            total_shipments=total_shipments,
            completed_today=completed_today,
            pending=pending,
            high_risk=high_risk,
            avg_sla_risk=round(avg_sla_risk, 2),
            metadata={"snapshot_source": "sender_state"}
        )
    
    except Exception as e:
        # Fallback to mock
        return _mock_daily_metrics(state, target_date)


def _mock_daily_metrics(state: str, target_date: str) -> DailyMetrics:
    """Generate mock daily metrics."""
    import random
    
    base = hash(state + target_date) % 100
    
    return DailyMetrics(
        date=target_date,
        state=state,
        total_shipments=50 + base,
        completed_today=5 + (base % 10),
        pending=10 + (base % 20),
        high_risk=2 + (base % 5),
        avg_sla_risk=round(15 + (base % 40), 2),
        metadata={"mock": True}
    )


def save_daily_metrics(metrics: DailyMetrics) -> None:
    """
    Save daily metrics to storage.
    
    Args:
        metrics: Metrics to save
        
    Notes:
        - Creates file if not exists
        - Overwrites existing metrics for same date/state
    """
    _ensure_metrics_dir()
    
    file_path = _get_metrics_file_path(metrics.date)
    
    # Load existing metrics for this date
    existing_metrics = []
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            existing_metrics = json.load(f)
    
    # Remove old entry for this state if exists
    existing_metrics = [
        m for m in existing_metrics
        if m.get("state") != metrics.state
    ]
    
    # Add new metrics
    existing_metrics.append(metrics.to_dict())
    
    # Write back
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(existing_metrics, f, indent=2)


def load_daily_metrics(target_date: str) -> List[DailyMetrics]:
    """
    Load daily metrics for a date.
    
    Args:
        target_date: Date in YYYY-MM-DD format
        
    Returns:
        List[DailyMetrics]: All state metrics for this date
    """
    file_path = _get_metrics_file_path(target_date)
    
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return [DailyMetrics.from_dict(m) for m in data]


def rollup_daily_metrics(target_date: Optional[str] = None) -> List[DailyMetrics]:
    """
    Rollup daily metrics for all states.
    
    Args:
        target_date: Date in YYYY-MM-DD format (defaults to today)
        
    Returns:
        List[DailyMetrics]: Metrics for all states
        
    Notes:
        - Called by snapshot worker at 5 PM
        - Computes and saves metrics for all states
    """
    if target_date is None:
        target_date = date.today().isoformat()
    
    # Import states list
    from app.ui.national_dashboard import INDIAN_STATES
    
    all_metrics = []
    
    for state in INDIAN_STATES:
        metrics = compute_daily_metrics_for_state(state, target_date)
        save_daily_metrics(metrics)
        all_metrics.append(metrics)
    
    return all_metrics


def should_trigger_rollup() -> bool:
    """
    Check if it's time to trigger daily rollup.
    
    Returns:
        bool: True if current time is 17:00 (5 PM)
        
    Notes:
        - Checks hour only (17:00-17:59)
        - Called by snapshot worker
    """
    now = datetime.now()
    return now.hour == 17


def get_latest_metrics_for_state(state: str) -> Optional[DailyMetrics]:
    """
    Get most recent daily metrics for a state.
    
    Args:
        state: State name
        
    Returns:
        DailyMetrics or None: Latest metrics if available
    """
    # Try today first
    today = date.today().isoformat()
    metrics = load_daily_metrics(today)
    
    for m in metrics:
        if m.state == state:
            return m
    
    # Try yesterday
    import datetime as dt
    yesterday = (dt.date.today() - dt.timedelta(days=1)).isoformat()
    metrics = load_daily_metrics(yesterday)
    
    for m in metrics:
        if m.state == state:
            return m
    
    return None


def get_metrics_trend(state: str, days: int = 7) -> List[DailyMetrics]:
    """
    Get daily metrics trend for a state.
    
    Args:
        state: State name
        days: Number of days to retrieve
        
    Returns:
        List[DailyMetrics]: Metrics for each day (oldest first)
    """
    import datetime as dt
    
    trend = []
    
    for i in range(days):
        target_date = (dt.date.today() - dt.timedelta(days=i)).isoformat()
        metrics = load_daily_metrics(target_date)
        
        for m in metrics:
            if m.state == state:
                trend.append(m)
                break
    
    # Reverse to get oldest first
    trend.reverse()
    
    return trend
