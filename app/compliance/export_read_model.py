"""
EXPORT SERIALIZERS

Purpose:
- Flat schemas for compliance exports
- CSV and JSON support
- Stable column ordering
- No data enrichment

Rules:
- Flat structures only (no nested objects in CSV)
- Deterministic column order
- No joins or enrichment
- Direct field mapping
"""

import json
import csv
from typing import List, Dict, Any
from io import StringIO


# ==================================================
# SCHEMA DEFINITIONS (STABLE COLUMN ORDER)
# ==================================================

# Audit Denial Schema
AUDIT_DENIAL_COLUMNS = [
    "shipment_id",
    "reason_code",
    "timestamp",
]

# Role Activity Schema
ROLE_ACTIVITY_COLUMNS = [
    "role",
    "generated_at",
    "total_attempts",
    "denied_attempts",
    "allowed_attempts",
]

# Geo Violation Schema
GEO_VIOLATION_COLUMNS = [
    "shipment_id",
    "reason_code",
    "violation_type",
    "timestamp",
]

# Compliance Summary Schema
COMPLIANCE_SUMMARY_COLUMNS = [
    "export_type",
    "role",
    "generated_at",
    "start_time",
    "end_time",
    "total_records",
]


# ==================================================
# JSON SERIALIZERS
# ==================================================

def serialize_audit_denials_json(denials: List[Dict[str, Any]]) -> str:
    """
    Serialize audit denials to JSON.
    
    Args:
        denials: List of denial records
    
    Returns:
        JSON string with flat structure
    """
    flat_records = []
    for denial in denials:
        flat_records.append({
            "shipment_id": denial.get("shipment_id", ""),
            "reason_code": denial.get("reason_code", ""),
            "timestamp": denial.get("timestamp", ""),
        })
    
    return json.dumps(flat_records, indent=2, ensure_ascii=False)


def serialize_role_activity_json(activity_data: Dict[str, Any]) -> str:
    """
    Serialize role activity to JSON.
    
    Args:
        activity_data: Role activity data dictionary
    
    Returns:
        JSON string with flat structure
    """
    activity_summary = activity_data.get("activity_summary", {})
    
    flat_record = {
        "role": activity_data.get("role", ""),
        "generated_at": activity_data.get("generated_at", ""),
        "total_attempts": activity_summary.get("total_access_attempts", 0),
        "denied_attempts": activity_summary.get("denied_attempts", 0),
        "allowed_attempts": activity_summary.get("allowed_attempts", 0),
    }
    
    return json.dumps(flat_record, indent=2, ensure_ascii=False)


def serialize_geo_violations_json(violations: List[Dict[str, Any]]) -> str:
    """
    Serialize geo violations to JSON.
    
    Args:
        violations: List of violation records
    
    Returns:
        JSON string with flat structure
    """
    flat_records = []
    for violation in violations:
        flat_records.append({
            "shipment_id": violation.get("shipment_id", ""),
            "reason_code": violation.get("reason_code", ""),
            "violation_type": _extract_violation_type(violation.get("reason_code", "")),
            "timestamp": violation.get("timestamp", ""),
        })
    
    return json.dumps(flat_records, indent=2, ensure_ascii=False)


# ==================================================
# CSV SERIALIZERS
# ==================================================

def serialize_audit_denials_csv(denials: List[Dict[str, Any]]) -> str:
    """
    Serialize audit denials to CSV.
    
    Args:
        denials: List of denial records
    
    Returns:
        CSV string with stable column order
    """
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=AUDIT_DENIAL_COLUMNS)
    
    # Write header
    writer.writeheader()
    
    # Write rows
    for denial in denials:
        writer.writerow({
            "shipment_id": denial.get("shipment_id", ""),
            "reason_code": denial.get("reason_code", ""),
            "timestamp": denial.get("timestamp", ""),
        })
    
    return output.getvalue()


def serialize_role_activity_csv(activity_data: Dict[str, Any]) -> str:
    """
    Serialize role activity to CSV.
    
    Args:
        activity_data: Role activity data dictionary
    
    Returns:
        CSV string with stable column order
    """
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=ROLE_ACTIVITY_COLUMNS)
    
    # Write header
    writer.writeheader()
    
    # Write row
    activity_summary = activity_data.get("activity_summary", {})
    writer.writerow({
        "role": activity_data.get("role", ""),
        "generated_at": activity_data.get("generated_at", ""),
        "total_attempts": activity_summary.get("total_access_attempts", 0),
        "denied_attempts": activity_summary.get("denied_attempts", 0),
        "allowed_attempts": activity_summary.get("allowed_attempts", 0),
    })
    
    return output.getvalue()


def serialize_geo_violations_csv(violations: List[Dict[str, Any]]) -> str:
    """
    Serialize geo violations to CSV.
    
    Args:
        violations: List of violation records
    
    Returns:
        CSV string with stable column order
    """
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=GEO_VIOLATION_COLUMNS)
    
    # Write header
    writer.writeheader()
    
    # Write rows
    for violation in violations:
        writer.writerow({
            "shipment_id": violation.get("shipment_id", ""),
            "reason_code": violation.get("reason_code", ""),
            "violation_type": _extract_violation_type(violation.get("reason_code", "")),
            "timestamp": violation.get("timestamp", ""),
        })
    
    return output.getvalue()


def serialize_compliance_summary_csv(export_data: Dict[str, Any]) -> str:
    """
    Serialize compliance summary to CSV.
    
    Args:
        export_data: Export data dictionary
    
    Returns:
        CSV string with stable column order
    """
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=COMPLIANCE_SUMMARY_COLUMNS)
    
    # Write header
    writer.writeheader()
    
    # Write row
    time_bounds = export_data.get("time_bounds", {})
    writer.writerow({
        "export_type": export_data.get("export_type", ""),
        "role": export_data.get("role", ""),
        "generated_at": export_data.get("generated_at", ""),
        "start_time": time_bounds.get("start", ""),
        "end_time": time_bounds.get("end", ""),
        "total_records": export_data.get("total_denials", 0),
    })
    
    return output.getvalue()


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def _extract_violation_type(reason_code: str) -> str:
    """
    Extract violation type from reason code.
    
    Args:
        reason_code: Denial reason code
    
    Returns:
        Simplified violation type
    """
    if reason_code == "GEO_SCOPE_MISMATCH":
        return "SCOPE_MISMATCH"
    elif reason_code == "MISSING_GEO_DATA":
        return "MISSING_DATA"
    elif reason_code == "NO_USER_REGIONS":
        return "NO_REGIONS"
    else:
        return "OTHER"


# ==================================================
# GENERIC SERIALIZER
# ==================================================

def serialize_export(
    export_data: Dict[str, Any],
    format_type: str = "JSON",
) -> str:
    """
    Serialize export data to specified format.
    
    Args:
        export_data: Export data dictionary
        format_type: Output format ("JSON" or "CSV")
    
    Returns:
        Serialized string
    """
    export_type = export_data.get("export_type", "")
    
    if format_type == "JSON":
        return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    elif format_type == "CSV":
        # Route to appropriate CSV serializer based on export type
        if export_type == "ACCESS_DENIALS":
            denials = export_data.get("denials", [])
            return serialize_audit_denials_csv(denials)
        
        elif export_type == "ROLE_ACTIVITY":
            return serialize_role_activity_csv(export_data)
        
        elif export_type == "GEO_VIOLATIONS":
            violations = export_data.get("violations", [])
            return serialize_geo_violations_csv(violations)
        
        else:
            # Default to summary
            return serialize_compliance_summary_csv(export_data)
    
    else:
        # Default to JSON
        return json.dumps(export_data, indent=2, ensure_ascii=False)
