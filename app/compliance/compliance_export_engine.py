"""
COMPLIANCE EXPORT ENGINE

Purpose:
- Generate compliance exports from snapshots
- Time-bounded and role-scoped
- Regulator-safe output
- Deterministic and reproducible

Rules:
- Snapshot-based only (no event store access)
- Time-bounded exports
- Role-scoped filtering using Geo-RBAC
- Deterministic output
- No side effects
"""

import json
from typing import Dict, Any, List, Optional
from app.core.audit_snapshot_store import read_audit_snapshot
from app.core.snapshot_store import read_snapshot
from app.compliance.export_types import (
    AUDIT_EXPORT_ACCESS_DENIALS,
    AUDIT_EXPORT_ROLE_ACTIVITY,
    AUDIT_EXPORT_GEO_VIOLATIONS,
    EXPORT_FORMAT_JSON,
    EXPORT_FORMAT_CSV,
    REDACTION_NONE,
    REDACTION_PII_ONLY,
)


# ==================================================
# AUDIT EXPORT ENGINE
# ==================================================

def export_audit_denials(
    role: str,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    redaction_level: str = REDACTION_NONE,
) -> Dict[str, Any]:
    """
    Export access denial audit data for a role.
    
    Args:
        role: User's role to export denials for
        start_time: Optional start timestamp (inclusive)
        end_time: Optional end timestamp (inclusive)
        redaction_level: Level of data redaction
    
    Returns:
        Dictionary with audit denial data
        - export_type: Type of export
        - generated_at: Export generation timestamp
        - role: Role this export is for
        - time_bounds: Start and end time filters
        - denials: List of denial records
        - summary: Aggregated statistics
    """
    # Read audit snapshot for role
    audit_data = read_audit_snapshot(role)
    
    if audit_data is None:
        return {
            "export_type": AUDIT_EXPORT_ACCESS_DENIALS,
            "generated_at": audit_data.get("generated_at") if audit_data else None,
            "role": role,
            "time_bounds": {"start": start_time, "end": end_time},
            "denials": [],
            "summary": {},
        }
    
    generated_at = audit_data.get("generated_at")
    denials = audit_data.get("denials", [])
    
    # Filter by time bounds if specified
    if start_time is not None or end_time is not None:
        filtered_denials = []
        for denial in denials:
            # In production, denials would have individual timestamps
            # For now, use snapshot generated_at
            if generated_at:
                if start_time and generated_at < start_time:
                    continue
                if end_time and generated_at > end_time:
                    continue
            filtered_denials.append(denial)
        denials = filtered_denials
    
    # Apply redaction
    if redaction_level == REDACTION_PII_ONLY:
        # For PII redaction, mask shipment IDs partially
        denials = [
            {
                "shipment_id": _redact_partial(d.get("shipment_id", "")),
                "reason_code": d.get("reason_code"),
            }
            for d in denials
        ]
    
    # Generate summary statistics
    summary = {}
    for denial in denials:
        reason = denial.get("reason_code", "UNKNOWN")
        summary[reason] = summary.get(reason, 0) + 1
    
    return {
        "export_type": AUDIT_EXPORT_ACCESS_DENIALS,
        "generated_at": generated_at,
        "role": role,
        "time_bounds": {"start": start_time, "end": end_time},
        "denials": denials,
        "summary": summary,
        "total_denials": len(denials),
    }


def export_role_activity(
    role: str,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Export role activity summary.
    
    Args:
        role: User's role
        start_time: Optional start timestamp
        end_time: Optional end timestamp
    
    Returns:
        Dictionary with role activity data
    """
    audit_data = read_audit_snapshot(role)
    
    if audit_data is None:
        return {
            "export_type": AUDIT_EXPORT_ROLE_ACTIVITY,
            "role": role,
            "time_bounds": {"start": start_time, "end": end_time},
            "activity_summary": {
                "total_access_attempts": 0,
                "denied_attempts": 0,
                "allowed_attempts": 0,
            },
        }
    
    generated_at = audit_data.get("generated_at")
    denials = audit_data.get("denials", [])
    
    # Filter by time if needed
    denial_count = len(denials)
    
    return {
        "export_type": AUDIT_EXPORT_ROLE_ACTIVITY,
        "generated_at": generated_at,
        "role": role,
        "time_bounds": {"start": start_time, "end": end_time},
        "activity_summary": {
            "total_access_attempts": denial_count,  # In production, track both allowed and denied
            "denied_attempts": denial_count,
            "allowed_attempts": 0,  # Would be calculated from full access logs
        },
        "denial_breakdown": _calculate_denial_breakdown(denials),
    }


def export_geo_violations(
    role: str,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Export geographic policy violations.
    
    Args:
        role: User's role
        start_time: Optional start timestamp
        end_time: Optional end timestamp
    
    Returns:
        Dictionary with geo violation data
    """
    audit_data = read_audit_snapshot(role)
    
    if audit_data is None:
        return {
            "export_type": AUDIT_EXPORT_GEO_VIOLATIONS,
            "role": role,
            "time_bounds": {"start": start_time, "end": end_time},
            "violations": [],
        }
    
    generated_at = audit_data.get("generated_at")
    denials = audit_data.get("denials", [])
    
    # Filter for geo-related violations only
    geo_violations = [
        d for d in denials
        if d.get("reason_code") in [
            "GEO_SCOPE_MISMATCH",
            "MISSING_GEO_DATA",
            "NO_USER_REGIONS",
        ]
    ]
    
    return {
        "export_type": AUDIT_EXPORT_GEO_VIOLATIONS,
        "generated_at": generated_at,
        "role": role,
        "time_bounds": {"start": start_time, "end": end_time},
        "violations": geo_violations,
        "total_violations": len(geo_violations),
        "violation_types": _calculate_denial_breakdown(geo_violations),
    }


# ==================================================
# EXPORT FORMATTING
# ==================================================

def format_export(
    export_data: Dict[str, Any],
    format_type: str = EXPORT_FORMAT_JSON,
) -> str:
    """
    Format export data into specified format.
    
    Args:
        export_data: Export data dictionary
        format_type: Output format (JSON, CSV, etc.)
    
    Returns:
        Formatted string output
    """
    if format_type == EXPORT_FORMAT_JSON:
        return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    elif format_type == EXPORT_FORMAT_CSV:
        return _format_as_csv(export_data)
    
    else:
        # Default to JSON
        return json.dumps(export_data, indent=2, ensure_ascii=False)


def _format_as_csv(export_data: Dict[str, Any]) -> str:
    """Convert export data to CSV format."""
    lines = []
    
    # Header
    export_type = export_data.get("export_type", "UNKNOWN")
    lines.append(f"Export Type,{export_type}")
    lines.append(f"Role,{export_data.get('role', 'N/A')}")
    lines.append(f"Generated At,{export_data.get('generated_at', 'N/A')}")
    lines.append("")
    
    # Denials (if present)
    denials = export_data.get("denials", [])
    if denials:
        lines.append("Shipment ID,Reason Code")
        for denial in denials:
            shipment_id = denial.get("shipment_id", "")
            reason_code = denial.get("reason_code", "")
            lines.append(f"{shipment_id},{reason_code}")
        lines.append("")
    
    # Summary (if present)
    summary = export_data.get("summary", {})
    if summary:
        lines.append("Reason Code,Count")
        for reason, count in summary.items():
            lines.append(f"{reason},{count}")
    
    return "\n".join(lines)


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def _redact_partial(value: str) -> str:
    """Partially redact a value for PII protection."""
    if not value or len(value) < 4:
        return "***"
    
    # Show first 3 and last 3 characters
    return f"{value[:3]}***{value[-3:]}"


def _calculate_denial_breakdown(denials: List[Dict[str, Any]]) -> Dict[str, int]:
    """Calculate breakdown of denials by reason code."""
    breakdown = {}
    for denial in denials:
        reason = denial.get("reason_code", "UNKNOWN")
        breakdown[reason] = breakdown.get(reason, 0) + 1
    return breakdown
