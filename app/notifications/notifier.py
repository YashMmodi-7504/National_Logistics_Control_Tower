"""
NOTIFICATION ENGINE

Purpose:
- Event-driven notification system
- Immutable notification creation
- Role-based routing
- Template-based messaging

Requirements:
• Triggered only by events
• Immutable after creation
• No manual notification creation
• Clear audit trail

Author: National Logistics Control Tower
Phase: 9.2 - Notification Engine
"""

import time
from typing import Dict, Any, List, Optional
from app.notifications.templates import (
    get_template,
    NotificationTemplate,
    NotificationSeverity,
)
from app.notifications.notification_store import (
    Notification,
    append_notification,
)
from app.core.id_generator import generate_shipment_id


def _generate_notification_id() -> str:
    """
    Generate unique notification ID.
    
    Returns:
        str: Unique notification ID (reuses shipment ID generator)
    """
    # Reuse shipment ID generator for consistency
    # Format: SHIP-YYYYMMDD-HHMMSS-XXXX → NOTIF-YYYYMMDD-HHMMSS-XXXX
    ship_id = generate_shipment_id()
    return ship_id.replace("SHIP-", "NOTIF-")


def emit_notification(
    template_name: str,
    shipment_id: str,
    context: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None
) -> Notification:
    """
    Emit a notification using a template.
    
    Args:
        template_name: Template identifier from registry
        shipment_id: Associated shipment ID
        context: Values for template placeholders
        metadata: Additional context data
        
    Returns:
        Notification: Created notification object
        
    Raises:
        KeyError: If template not found
        
    Examples:
        >>> emit_notification(
        ...     template_name="RECEIVER_ACK_TO_SENDER",
        ...     shipment_id="SHIP-20260119-120000-1234",
        ...     context={
        ...         "shipment_id": "SHIP-20260119-120000-1234",
        ...         "destination_state": "Maharashtra"
        ...     }
        ... )
    """
    # Get template
    template = get_template(template_name)
    
    # Format message
    message = template.format(**context)
    
    # Create notification
    notification = Notification(
        notification_id=_generate_notification_id(),
        timestamp=time.time(),
        shipment_id=shipment_id,
        template_name=template_name,
        message=message,
        severity=template.severity.value,
        recipients=template.recipient_roles,
        metadata=metadata or {},
        read_by=[],
    )
    
    # Store notification
    append_notification(notification)
    
    return notification


# ────────────────────────────────────────────────────────────
# EVENT-DRIVEN NOTIFICATION HANDLERS
# ────────────────────────────────────────────────────────────


def notify_receiver_acknowledgment(event: Dict[str, Any]) -> List[Notification]:
    """
    Handle RECEIVER_ACKNOWLEDGED event.
    
    Notifications:
    - RECEIVER_ACK_TO_SENDER: Inform sender manager and supervisor
    - RECEIVER_ACK_DELAYED: If acknowledgment was late
    
    Args:
        event: Event payload with shipment data
        
    Returns:
        List[Notification]: Created notifications
    """
    notifications = []
    
    shipment_id = event.get("shipment_id")
    shipment = event.get("shipment", {})
    destination_state = shipment.get("destination_state", "Unknown")
    
    # Base notification
    notification = emit_notification(
        template_name="RECEIVER_ACK_TO_SENDER",
        shipment_id=shipment_id,
        context={
            "shipment_id": shipment_id,
            "destination_state": destination_state,
        },
        metadata={"event_type": "RECEIVER_ACKNOWLEDGED"}
    )
    notifications.append(notification)
    
    # Check for delayed acknowledgment
    sla_risk = shipment.get("sla_breach_probability", 0)
    if sla_risk > 50:  # High SLA risk indicates delay
        delayed_notification = emit_notification(
            template_name="RECEIVER_ACK_DELAYED",
            shipment_id=shipment_id,
            context={
                "shipment_id": shipment_id,
                "sla_risk": int(sla_risk),
            },
            metadata={"event_type": "RECEIVER_ACKNOWLEDGED", "delayed": True}
        )
        notifications.append(delayed_notification)
    
    return notifications


def notify_delivery_confirmation(event: Dict[str, Any]) -> List[Notification]:
    """
    Handle DELIVERY_CONFIRMED event.
    
    Notifications:
    - DELIVERY_CONFIRMED: Success notification
    - DELIVERY_FAILED: If delivery failed
    
    Args:
        event: Event payload with delivery data
        
    Returns:
        List[Notification]: Created notifications
    """
    notifications = []
    
    shipment_id = event.get("shipment_id")
    delivery_status = event.get("status", "success")
    
    if delivery_status == "success":
        notification = emit_notification(
            template_name="DELIVERY_CONFIRMED",
            shipment_id=shipment_id,
            context={
                "shipment_id": shipment_id,
                "delivery_time": event.get("timestamp", "Unknown"),
            },
            metadata={"event_type": "DELIVERY_CONFIRMED"}
        )
        notifications.append(notification)
    
    else:
        # Delivery failed
        notification = emit_notification(
            template_name="DELIVERY_FAILED",
            shipment_id=shipment_id,
            context={
                "shipment_id": shipment_id,
                "failure_reason": event.get("failure_reason", "Unknown"),
            },
            metadata={"event_type": "DELIVERY_FAILED"}
        )
        notifications.append(notification)
    
    return notifications


def notify_supervisor_priority_escalation(event: Dict[str, Any]) -> List[Notification]:
    """
    Handle SUPERVISOR_APPROVED event for high-priority shipments.
    
    Notifications:
    - SUPERVISOR_PRIORITY_ESCALATION: If high risk detected
    
    Args:
        event: Event payload with approval data
        
    Returns:
        List[Notification]: Created notifications
    """
    notifications = []
    
    shipment_id = event.get("shipment_id")
    shipment = event.get("shipment", {})
    risk_score = shipment.get("combined_risk_score", 0)
    
    # Only notify if high risk
    if risk_score > 70:
        notification = emit_notification(
            template_name="SUPERVISOR_PRIORITY_ESCALATION",
            shipment_id=shipment_id,
            context={
                "shipment_id": shipment_id,
                "risk_score": int(risk_score),
            },
            metadata={"event_type": "SUPERVISOR_APPROVED", "high_priority": True}
        )
        notifications.append(notification)
    
    return notifications


def notify_sla_breach_warning(shipment_id: str, breach_probability: float) -> Notification:
    """
    Notify about SLA breach risk.
    
    Args:
        shipment_id: Shipment ID
        breach_probability: Probability of breach (0-100)
        
    Returns:
        Notification: Created notification
    """
    return emit_notification(
        template_name="SLA_BREACH_WARNING",
        shipment_id=shipment_id,
        context={
            "shipment_id": shipment_id,
            "breach_probability": int(breach_probability),
        },
        metadata={"event_type": "SLA_BREACH_WARNING"}
    )


def notify_ai_high_risk(event: Dict[str, Any]) -> Notification:
    """
    Notify about AI-detected high risk.
    
    Args:
        event: Event payload with AI predictions
        
    Returns:
        Notification: Created notification
    """
    shipment_id = event.get("shipment_id")
    ai_predictions = event.get("ai_predictions", {})
    
    return emit_notification(
        template_name="AI_HIGH_RISK_ALERT",
        shipment_id=shipment_id,
        context={
            "shipment_id": shipment_id,
            "weather_risk": ai_predictions.get("weather_risk", "N/A"),
            "route_risk": ai_predictions.get("route_risk", "N/A"),
            "sla_risk": ai_predictions.get("sla_risk", "N/A"),
        },
        metadata={"event_type": "AI_PREDICTION", "high_risk": True}
    )


def notify_manager_override(event: Dict[str, Any]) -> Notification:
    """
    Notify about manager override.
    
    Args:
        event: Event payload with override data
        
    Returns:
        Notification: Created notification
    """
    shipment_id = event.get("shipment_id")
    
    return emit_notification(
        template_name="MANAGER_OVERRIDE_RECORDED",
        shipment_id=shipment_id,
        context={
            "shipment_id": shipment_id,
            "override_reason": event.get("reason", "Not specified"),
            "original_decision": event.get("original_decision", "Unknown"),
        },
        metadata={"event_type": "HUMAN_OVERRIDE_RECORDED"}
    )


def notify_daily_metrics_rollup(date: str, total_shipments: int) -> Notification:
    """
    Notify about daily metrics rollup completion.
    
    Args:
        date: Rollup date (YYYY-MM-DD)
        total_shipments: Total shipments processed
        
    Returns:
        Notification: Created notification
    """
    return emit_notification(
        template_name="DAILY_METRICS_ROLLUP",
        shipment_id="SYSTEM",
        context={
            "date": date,
            "total_shipments": total_shipments,
        },
        metadata={"event_type": "DAILY_METRICS_ROLLUP"}
    )


# ────────────────────────────────────────────────────────────
# EVENT ROUTER
# ────────────────────────────────────────────────────────────


def route_event_to_notifications(event: Dict[str, Any]) -> List[Notification]:
    """
    Route event to appropriate notification handlers.
    
    Args:
        event: Event payload
        
    Returns:
        List[Notification]: All notifications created from event
        
    Notes:
        - Called by event emitter after event storage
        - Returns empty list if event doesn't trigger notifications
    """
    event_type = event.get("event_type")
    
    if event_type == "RECEIVER_ACKNOWLEDGED":
        return notify_receiver_acknowledgment(event)
    
    elif event_type == "DELIVERY_CONFIRMED":
        return notify_delivery_confirmation(event)
    
    elif event_type == "SUPERVISOR_APPROVED":
        return notify_supervisor_priority_escalation(event)
    
    elif event_type == "HUMAN_OVERRIDE_RECORDED":
        return [notify_manager_override(event)]
    
    # Add more event routing as needed
    
    return []
