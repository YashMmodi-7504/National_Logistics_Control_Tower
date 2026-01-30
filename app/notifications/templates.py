"""
NOTIFICATION TEMPLATES

Purpose:
- Centralized message templates
- Consistent notification formatting
- Severity classification
- Role-based routing

Requirements:
• Immutable templates
• Clear severity levels
• Explicit recipient roles
• Human-readable messages

Author: National Logistics Control Tower
Phase: 9.2 - Notification Engine
"""

from typing import List, Dict, Any
from enum import Enum


class NotificationSeverity(str, Enum):
    """Notification severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    URGENT = "URGENT"
    CRITICAL = "CRITICAL"


class NotificationTemplate:
    """Base notification template."""
    
    def __init__(
        self,
        message_template: str,
        severity: NotificationSeverity,
        recipient_roles: List[str]
    ):
        """
        Initialize notification template.
        
        Args:
            message_template: Template string with placeholders
            severity: Notification severity level
            recipient_roles: List of role constants who receive this
        """
        self.message_template = message_template
        self.severity = severity
        self.recipient_roles = recipient_roles
    
    def format(self, **kwargs) -> str:
        """
        Format template with provided values.
        
        Args:
            **kwargs: Values for template placeholders
            
        Returns:
            str: Formatted message
        """
        return self.message_template.format(**kwargs)


# ────────────────────────────────────────────────────────────
# RECEIVER ACKNOWLEDGMENT NOTIFICATIONS
# ────────────────────────────────────────────────────────────

RECEIVER_ACK_TO_SENDER = NotificationTemplate(
    message_template="Shipment {shipment_id} has reached Receiver Manager in {destination_state}.",
    severity=NotificationSeverity.INFO,
    recipient_roles=["SENDER_MANAGER", "SENDER_SUPERVISOR"]
)

RECEIVER_ACK_DELAYED = NotificationTemplate(
    message_template="⚠️ Shipment {shipment_id} acknowledged late. SLA risk increased to {sla_risk}%.",
    severity=NotificationSeverity.WARNING,
    recipient_roles=["SENDER_MANAGER", "SENDER_SUPERVISOR", "COO"]
)


# ────────────────────────────────────────────────────────────
# DELIVERY CONFIRMATION NOTIFICATIONS
# ────────────────────────────────────────────────────────────

DELIVERY_CONFIRMED = NotificationTemplate(
    message_template="✅ Shipment {shipment_id} successfully delivered to customer at {delivery_time}.",
    severity=NotificationSeverity.INFO,
    recipient_roles=["WAREHOUSE_MANAGER", "RECEIVER_MANAGER", "SENDER_MANAGER"]
)

DELIVERY_FAILED = NotificationTemplate(
    message_template="❌ Delivery attempt failed for {shipment_id}. Reason: {failure_reason}.",
    severity=NotificationSeverity.URGENT,
    recipient_roles=["WAREHOUSE_MANAGER", "RECEIVER_MANAGER", "COO"]
)


# ────────────────────────────────────────────────────────────
# PRIORITY ESCALATION NOTIFICATIONS
# ────────────────────────────────────────────────────────────

SUPERVISOR_PRIORITY_ESCALATION = NotificationTemplate(
    message_template="🚨 URGENT: High-priority shipment {shipment_id} approved. Risk score: {risk_score}. Will be dispatched first.",
    severity=NotificationSeverity.URGENT,
    recipient_roles=["SENDER_MANAGER", "COO"]
)

SLA_BREACH_WARNING = NotificationTemplate(
    message_template="⚠️ Shipment {shipment_id} at risk of SLA breach. Current probability: {breach_probability}%.",
    severity=NotificationSeverity.WARNING,
    recipient_roles=["SENDER_MANAGER", "RECEIVER_MANAGER", "COO"]
)


# ────────────────────────────────────────────────────────────
# WAREHOUSE NOTIFICATIONS
# ────────────────────────────────────────────────────────────

WAREHOUSE_INTAKE_READY = NotificationTemplate(
    message_template="Shipment {shipment_id} ready for warehouse intake. Priority: {priority_level}.",
    severity=NotificationSeverity.INFO,
    recipient_roles=["WAREHOUSE_MANAGER"]
)

WAREHOUSE_OUT_FOR_DELIVERY = NotificationTemplate(
    message_template="Shipment {shipment_id} out for delivery. ETA: {eta}.",
    severity=NotificationSeverity.INFO,
    recipient_roles=["RECEIVER_MANAGER", "SENDER_MANAGER"]
)


# ────────────────────────────────────────────────────────────
# AI PREDICTION NOTIFICATIONS
# ────────────────────────────────────────────────────────────

AI_HIGH_RISK_ALERT = NotificationTemplate(
    message_template="🤖 AI detected high risk for {shipment_id}. Weather: {weather_risk}, Route: {route_risk}, SLA: {sla_risk}.",
    severity=NotificationSeverity.WARNING,
    recipient_roles=["SENDER_MANAGER", "SENDER_SUPERVISOR"]
)

AI_ROUTE_OPTIMIZATION = NotificationTemplate(
    message_template="💡 AI suggests alternative route for {shipment_id}. Potential time savings: {time_saved} hours.",
    severity=NotificationSeverity.INFO,
    recipient_roles=["SENDER_MANAGER"]
)


# ────────────────────────────────────────────────────────────
# MANAGER OVERRIDE NOTIFICATIONS
# ────────────────────────────────────────────────────────────

MANAGER_OVERRIDE_RECORDED = NotificationTemplate(
    message_template="⚡ Manager override recorded for {shipment_id}. Reason: {override_reason}. Original decision: {original_decision}.",
    severity=NotificationSeverity.INFO,
    recipient_roles=["COO", "SYSTEM"]
)

OVERRIDE_AUDIT_ALERT = NotificationTemplate(
    message_template="📋 Override audit required for {shipment_id}. Override count: {override_count} in last 24h.",
    severity=NotificationSeverity.WARNING,
    recipient_roles=["COO", "REGULATOR"]
)


# ────────────────────────────────────────────────────────────
# SYSTEM NOTIFICATIONS
# ────────────────────────────────────────────────────────────

DAILY_METRICS_ROLLUP = NotificationTemplate(
    message_template="📊 Daily metrics rollup completed. Date: {date}. Total shipments: {total_shipments}.",
    severity=NotificationSeverity.INFO,
    recipient_roles=["COO", "SYSTEM"]
)

SNAPSHOT_INTEGRITY_ALERT = NotificationTemplate(
    message_template="🔒 Snapshot integrity verification complete. Status: {status}. Issues: {issue_count}.",
    severity=NotificationSeverity.CRITICAL if "{issue_count}" != "0" else NotificationSeverity.INFO,
    recipient_roles=["SYSTEM", "COO", "REGULATOR"]
)


# ────────────────────────────────────────────────────────────
# TEMPLATE REGISTRY
# ────────────────────────────────────────────────────────────

NOTIFICATION_TEMPLATES: Dict[str, NotificationTemplate] = {
    # Receiver acknowledgment
    "RECEIVER_ACK_TO_SENDER": RECEIVER_ACK_TO_SENDER,
    "RECEIVER_ACK_DELAYED": RECEIVER_ACK_DELAYED,
    
    # Delivery confirmation
    "DELIVERY_CONFIRMED": DELIVERY_CONFIRMED,
    "DELIVERY_FAILED": DELIVERY_FAILED,
    
    # Priority escalation
    "SUPERVISOR_PRIORITY_ESCALATION": SUPERVISOR_PRIORITY_ESCALATION,
    "SLA_BREACH_WARNING": SLA_BREACH_WARNING,
    
    # Warehouse
    "WAREHOUSE_INTAKE_READY": WAREHOUSE_INTAKE_READY,
    "WAREHOUSE_OUT_FOR_DELIVERY": WAREHOUSE_OUT_FOR_DELIVERY,
    
    # AI predictions
    "AI_HIGH_RISK_ALERT": AI_HIGH_RISK_ALERT,
    "AI_ROUTE_OPTIMIZATION": AI_ROUTE_OPTIMIZATION,
    
    # Manager overrides
    "MANAGER_OVERRIDE_RECORDED": MANAGER_OVERRIDE_RECORDED,
    "OVERRIDE_AUDIT_ALERT": OVERRIDE_AUDIT_ALERT,
    
    # System
    "DAILY_METRICS_ROLLUP": DAILY_METRICS_ROLLUP,
    "SNAPSHOT_INTEGRITY_ALERT": SNAPSHOT_INTEGRITY_ALERT,
}


def get_template(template_name: str) -> NotificationTemplate:
    """
    Retrieve notification template by name.
    
    Args:
        template_name: Template identifier
        
    Returns:
        NotificationTemplate: Template object
        
    Raises:
        KeyError: If template not found
    """
    if template_name not in NOTIFICATION_TEMPLATES:
        raise KeyError(f"Template '{template_name}' not found in registry")
    
    return NOTIFICATION_TEMPLATES[template_name]


def list_templates_by_severity(severity: NotificationSeverity) -> List[str]:
    """
    List all templates with given severity.
    
    Args:
        severity: Severity level to filter by
        
    Returns:
        List[str]: Template names matching severity
    """
    return [
        name
        for name, template in NOTIFICATION_TEMPLATES.items()
        if template.severity == severity
    ]


def list_templates_by_role(role: str) -> List[str]:
    """
    List all templates targeting given role.
    
    Args:
        role: Role constant (e.g., "SENDER_MANAGER")
        
    Returns:
        List[str]: Template names targeting this role
    """
    return [
        name
        for name, template in NOTIFICATION_TEMPLATES.items()
        if role in template.recipient_roles
    ]
