"""
COMPLIANCE EXPORT TYPES

Purpose:
- Define regulator-safe export types
- Enum-based for type safety
- Used for audit trails and compliance reports

Rules:
- No business logic
- No IO operations
- Only type definitions
"""

from typing import Literal

# ==================================================
# EXPORT FORMAT TYPES
# ==================================================

EXPORT_FORMAT_JSON: Literal["JSON"] = "JSON"
EXPORT_FORMAT_CSV: Literal["CSV"] = "CSV"
EXPORT_FORMAT_PDF: Literal["PDF"] = "PDF"
EXPORT_FORMAT_XML: Literal["XML"] = "XML"

ALL_EXPORT_FORMATS: list[str] = [
    EXPORT_FORMAT_JSON,
    EXPORT_FORMAT_CSV,
    EXPORT_FORMAT_PDF,
    EXPORT_FORMAT_XML,
]


# ==================================================
# AUDIT EXPORT TYPES
# ==================================================

AUDIT_EXPORT_ACCESS_DENIALS: Literal["ACCESS_DENIALS"] = "ACCESS_DENIALS"
AUDIT_EXPORT_ROLE_ACTIVITY: Literal["ROLE_ACTIVITY"] = "ROLE_ACTIVITY"
AUDIT_EXPORT_GEO_VIOLATIONS: Literal["GEO_VIOLATIONS"] = "GEO_VIOLATIONS"
AUDIT_EXPORT_FULL_TRAIL: Literal["FULL_TRAIL"] = "FULL_TRAIL"

ALL_AUDIT_EXPORT_TYPES: list[str] = [
    AUDIT_EXPORT_ACCESS_DENIALS,
    AUDIT_EXPORT_ROLE_ACTIVITY,
    AUDIT_EXPORT_GEO_VIOLATIONS,
    AUDIT_EXPORT_FULL_TRAIL,
]


# ==================================================
# SHIPMENT EXPORT TYPES
# ==================================================

SHIPMENT_EXPORT_LIFECYCLE: Literal["LIFECYCLE"] = "LIFECYCLE"
SHIPMENT_EXPORT_EVENTS: Literal["EVENTS"] = "EVENTS"
SHIPMENT_EXPORT_SLA: Literal["SLA"] = "SLA"
SHIPMENT_EXPORT_RISK: Literal["RISK"] = "RISK"
SHIPMENT_EXPORT_FULL: Literal["FULL"] = "FULL"

ALL_SHIPMENT_EXPORT_TYPES: list[str] = [
    SHIPMENT_EXPORT_LIFECYCLE,
    SHIPMENT_EXPORT_EVENTS,
    SHIPMENT_EXPORT_SLA,
    SHIPMENT_EXPORT_RISK,
    SHIPMENT_EXPORT_FULL,
]


# ==================================================
# COMPLIANCE REPORT TYPES
# ==================================================

COMPLIANCE_REPORT_ACCESS_CONTROL: Literal["ACCESS_CONTROL"] = "ACCESS_CONTROL"
COMPLIANCE_REPORT_DATA_RETENTION: Literal["DATA_RETENTION"] = "DATA_RETENTION"
COMPLIANCE_REPORT_DISPUTE_LOG: Literal["DISPUTE_LOG"] = "DISPUTE_LOG"
COMPLIANCE_REPORT_SLA_BREACH: Literal["SLA_BREACH"] = "SLA_BREACH"
COMPLIANCE_REPORT_REGULATORY: Literal["REGULATORY"] = "REGULATORY"

ALL_COMPLIANCE_REPORT_TYPES: list[str] = [
    COMPLIANCE_REPORT_ACCESS_CONTROL,
    COMPLIANCE_REPORT_DATA_RETENTION,
    COMPLIANCE_REPORT_DISPUTE_LOG,
    COMPLIANCE_REPORT_SLA_BREACH,
    COMPLIANCE_REPORT_REGULATORY,
]


# ==================================================
# EXPORT SCOPE TYPES
# ==================================================

EXPORT_SCOPE_SINGLE_SHIPMENT: Literal["SINGLE_SHIPMENT"] = "SINGLE_SHIPMENT"
EXPORT_SCOPE_CORRIDOR: Literal["CORRIDOR"] = "CORRIDOR"
EXPORT_SCOPE_STATE: Literal["STATE"] = "STATE"
EXPORT_SCOPE_ROLE: Literal["ROLE"] = "ROLE"
EXPORT_SCOPE_GLOBAL: Literal["GLOBAL"] = "GLOBAL"

ALL_EXPORT_SCOPES: list[str] = [
    EXPORT_SCOPE_SINGLE_SHIPMENT,
    EXPORT_SCOPE_CORRIDOR,
    EXPORT_SCOPE_STATE,
    EXPORT_SCOPE_ROLE,
    EXPORT_SCOPE_GLOBAL,
]


# ==================================================
# REDACTION LEVEL TYPES
# ==================================================

REDACTION_NONE: Literal["NONE"] = "NONE"
REDACTION_PARTIAL: Literal["PARTIAL"] = "PARTIAL"
REDACTION_PII_ONLY: Literal["PII_ONLY"] = "PII_ONLY"
REDACTION_FULL: Literal["FULL"] = "FULL"

ALL_REDACTION_LEVELS: list[str] = [
    REDACTION_NONE,
    REDACTION_PARTIAL,
    REDACTION_PII_ONLY,
    REDACTION_FULL,
]
