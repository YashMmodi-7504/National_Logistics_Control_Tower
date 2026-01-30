"""
INCIDENT TIMELINE RECONSTRUCTION

Purpose:
- Reconstruct what the system "knew" at any time
- Build ordered, explainable timeline
- Human-readable incident analysis

Requirements:
- Ordered timeline
- Explainable events
- Human-readable
- Snapshot-based only
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from app.forensics.replay_engine import replay_snapshot_state, ReplayError
from app.security.tamper_detector import detect_snapshot_tampering


class TimelineEntry:
    """
    Represents a single entry in an incident timeline.
    
    Attributes:
        timestamp: When this event occurred
        snapshot_name: Which snapshot this relates to
        event_type: Type of event
        description: Human-readable description
        details: Additional details
        severity: Severity level
    """
    
    def __init__(
        self,
        timestamp: float,
        snapshot_name: str,
        event_type: str,
        description: str,
        details: Optional[Dict[str, Any]] = None,
        severity: Optional[str] = None,
    ):
        self.timestamp = timestamp
        self.snapshot_name = snapshot_name
        self.event_type = event_type
        self.description = description
        self.details = details or {}
        self.severity = severity
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "timestamp_human": datetime.fromtimestamp(self.timestamp).isoformat(),
            "snapshot_name": self.snapshot_name,
            "event_type": self.event_type,
            "description": self.description,
            "details": self.details,
            "severity": self.severity,
        }
    
    def to_human_readable(self) -> str:
        """Convert to human-readable string."""
        dt = datetime.fromtimestamp(self.timestamp)
        severity_prefix = f"[{self.severity}] " if self.severity else ""
        return (
            f"{dt.strftime('%Y-%m-%d %H:%M:%S')} | "
            f"{severity_prefix}{self.event_type} | "
            f"{self.snapshot_name} | "
            f"{self.description}"
        )


def build_incident_timeline(
    snapshot_name: str,
    include_integrity: bool = True,
) -> List[TimelineEntry]:
    """
    Build an incident timeline for a snapshot.
    
    Args:
        snapshot_name: Name of the snapshot
        include_integrity: Include integrity check events
    
    Returns:
        List of TimelineEntry objects (ordered by timestamp)
    
    Output:
        Human-readable timeline of events
    """
    timeline = []
    
    # Integrity check event
    if include_integrity:
        integrity_result = detect_snapshot_tampering(snapshot_name)
        
        if integrity_result["status"] == "INTACT":
            timeline.append(TimelineEntry(
                timestamp=0,  # Placeholder - will be updated with actual timestamp
                snapshot_name=snapshot_name,
                event_type="INTEGRITY_CHECK",
                description="Snapshot integrity verified",
                severity="INFO",
            ))
        else:
            timeline.append(TimelineEntry(
                timestamp=0,
                snapshot_name=snapshot_name,
                event_type="INTEGRITY_VIOLATION",
                description=f"Snapshot integrity compromised: {', '.join(integrity_result['violated_rules'])}",
                details=integrity_result["details"],
                severity=integrity_result["severity"],
            ))
    
    # Replay snapshot state
    try:
        replay_result = replay_snapshot_state(snapshot_name)
        
        snapshot_timestamp = replay_result.get("timestamp")
        if snapshot_timestamp:
            # Update integrity check timestamp
            for entry in timeline:
                if entry.timestamp == 0:
                    entry.timestamp = snapshot_timestamp
            
            # Snapshot creation event
            timeline.append(TimelineEntry(
                timestamp=snapshot_timestamp,
                snapshot_name=snapshot_name,
                event_type="SNAPSHOT_CREATED",
                description=f"Snapshot {snapshot_name} created",
                details={
                    "integrity": replay_result.get("integrity_status"),
                },
                severity="INFO",
            ))
            
            # Analyze snapshot content for events
            content = replay_result.get("content", {})
            content_events = _extract_events_from_snapshot(
                snapshot_name,
                content,
                snapshot_timestamp,
            )
            timeline.extend(content_events)
    
    except ReplayError as e:
        timeline.append(TimelineEntry(
            timestamp=0,
            snapshot_name=snapshot_name,
            event_type="REPLAY_ERROR",
            description=f"Failed to replay snapshot: {str(e)}",
            severity="ERROR",
        ))
    
    # Sort by timestamp
    timeline.sort(key=lambda x: x.timestamp)
    
    return timeline


def build_multi_snapshot_timeline(
    snapshot_names: List[str],
) -> List[TimelineEntry]:
    """
    Build a timeline across multiple snapshots.
    
    Args:
        snapshot_names: List of snapshot names
    
    Returns:
        Combined timeline ordered by timestamp
    """
    combined_timeline = []
    
    for snapshot_name in snapshot_names:
        timeline = build_incident_timeline(snapshot_name, include_integrity=True)
        combined_timeline.extend(timeline)
    
    # Sort combined timeline
    combined_timeline.sort(key=lambda x: x.timestamp)
    
    return combined_timeline


def get_timeline_summary(timeline: List[TimelineEntry]) -> Dict[str, Any]:
    """
    Get summary statistics for a timeline.
    
    Args:
        timeline: List of timeline entries
    
    Returns:
        Summary dictionary:
        - total_events: int
        - event_types: dict (type -> count)
        - severity_breakdown: dict (severity -> count)
        - time_span: dict (start, end)
    """
    if not timeline:
        return {
            "total_events": 0,
            "event_types": {},
            "severity_breakdown": {},
            "time_span": None,
        }
    
    event_types = {}
    severity_breakdown = {}
    
    for entry in timeline:
        # Count event types
        event_type = entry.event_type
        event_types[event_type] = event_types.get(event_type, 0) + 1
        
        # Count severity
        if entry.severity:
            severity_breakdown[entry.severity] = severity_breakdown.get(entry.severity, 0) + 1
    
    # Calculate time span
    timestamps = [e.timestamp for e in timeline if e.timestamp > 0]
    time_span = None
    
    if timestamps:
        time_span = {
            "start": min(timestamps),
            "end": max(timestamps),
            "duration_seconds": max(timestamps) - min(timestamps),
        }
    
    return {
        "total_events": len(timeline),
        "event_types": event_types,
        "severity_breakdown": severity_breakdown,
        "time_span": time_span,
    }


def export_timeline_text(timeline: List[TimelineEntry]) -> str:
    """
    Export timeline as human-readable text.
    
    Args:
        timeline: List of timeline entries
    
    Returns:
        Formatted text string
    """
    lines = []
    lines.append("=" * 80)
    lines.append("INCIDENT TIMELINE")
    lines.append("=" * 80)
    lines.append("")
    
    for entry in timeline:
        lines.append(entry.to_human_readable())
    
    lines.append("")
    lines.append("=" * 80)
    lines.append(f"Total Events: {len(timeline)}")
    lines.append("=" * 80)
    
    return "\n".join(lines)


def export_timeline_json(timeline: List[TimelineEntry]) -> List[Dict[str, Any]]:
    """
    Export timeline as JSON-serializable list.
    
    Args:
        timeline: List of timeline entries
    
    Returns:
        List of dictionaries
    """
    return [entry.to_dict() for entry in timeline]


# ==================================================
# INTERNAL HELPERS
# ==================================================

def _extract_events_from_snapshot(
    snapshot_name: str,
    content: Dict[str, Any],
    base_timestamp: float,
) -> List[TimelineEntry]:
    """
    Extract implicit events from snapshot content.
    
    Args:
        snapshot_name: Name of snapshot
        content: Snapshot content
        base_timestamp: Base timestamp for events
    
    Returns:
        List of timeline entries
    """
    events = []
    
    # Check for alerts
    if "alerts" in content:
        alerts = content["alerts"]
        if isinstance(alerts, list) and len(alerts) > 0:
            events.append(TimelineEntry(
                timestamp=base_timestamp,
                snapshot_name=snapshot_name,
                event_type="ALERTS_DETECTED",
                description=f"{len(alerts)} alerts detected",
                details={"alert_count": len(alerts)},
                severity="WARNING",
            ))
    
    # Check for data
    if "data" in content:
        data = content["data"]
        if isinstance(data, dict):
            events.append(TimelineEntry(
                timestamp=base_timestamp,
                snapshot_name=snapshot_name,
                event_type="DATA_CAPTURED",
                description=f"Captured {len(data)} data entries",
                details={"entry_count": len(data)},
                severity="INFO",
            ))
    
    return events
